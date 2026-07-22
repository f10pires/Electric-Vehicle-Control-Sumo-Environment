import random
import traci


class RandomVeh:

    def __init__(self, config):

        self.config = config
        self.refdist = 0.0

        self.edges = set([edge for edge in traci.edge.getIDList()if not edge.startswith(":")])

        self.vehicle_type = config["vTypes"]
        self.max_vehicles = config["Max_vehicles"]

        # Fix random seed for reproducibility
        random.seed(int(config["seed"]))


        self.mu = 13.8      # hours
        self.sigma = 2.5    # hours

        
        # -------------------------------------------------
        # Get all parking areas and charging stations
        # -------------------------------------------------
        self.parkings = set(traci.parkingarea.getIDList())
        self.stations = set(traci.chargingstation.getIDList())

        # -------------------------------------------------
        # Map each charging station to its corresponding edge
        # -------------------------------------------------
        self.station_edges = {
            station: traci.chargingstation.getLaneID(station).rsplit("_", 1)[0]
            for station in self.stations
        }

        # -------------------------------------------------
        # Map parking areas to their edges
        # (excluding edges that already contain charging stations)
        # -------------------------------------------------
        station_edge_set = set(self.station_edges.values())
        self.parking_edges = {
                parking: traci.parkingarea.getLaneID(parking).rsplit("_", 1)[0] 
                for parking in self.parkings
                if traci.parkingarea.getLaneID(parking).rsplit("_", 1)[0] not in station_edge_set}

        # Create all vehicles
        self.route()

    # -------------------------------------------------
    # Create routes and insert vehicles into the simulation
    # -------------------------------------------------
    def route(self):

        for i in range(self.max_vehicles):

            # Select a random origin edge
            initial_edge = random.choice(list(self.edges))

            # Build the list of possible destinations
            destinations = {}
            destinations.update(self.station_edges)
            destinations.update(self.parking_edges)

            # Randomly choose one destination
            destination_id = random.choice(list(destinations.keys()))
            destination_edge = destinations[destination_id]

            # Compute the route
            route = traci.simulation.findRoute(
                initial_edge,
                destination_edge,
                vType=self.vehicle_type,
            )

            if not route.edges:
                raise RuntimeError(
                    f"No route found from '{initial_edge}' to '{destination_edge}'."
                )

            route_id = f"vehicle_route_{i}"
            vehicle_id = f"vehicle_{i}"

            traci.route.add(route_id, route.edges)

            # Random departure time
            departure_hour = random.gauss(self.mu, self.sigma)
            depart_veh = int(departure_hour * 3600)

            traci.vehicle.add(
                vehID=vehicle_id,
                routeID=route_id,
                typeID=self.vehicle_type,
                depart=depart_veh,
            )

            # Configure the final stop
            self.stop(vehicle_id, destination_id, destination_edge)

    # -------------------------------------------------
    # Assign the final stop according to the destination type
    # -------------------------------------------------
    def stop(self, vehicle_id, destination_id, destination_edge):

        if destination_id in self.parking_edges:

            traci.vehicle.setParkingAreaStop(
                vehicle_id,
                destination_id,
                duration=360,
            )

        else:

            traci.vehicle.setChargingStationStop(
                vehicle_id,
                destination_id,
                duration=360,
                flags=1,
            )
        
import traci
import itertools

class Action:
    def __init__(self, ev):
        self.ev = ev
        self.stop_duration = 43200
        self.charging_stop_flag = 1

    # -----------------------------
    # Route control
    # -----------------------------
    def continue_travel(self):
        return


    def find_optimal_bincollection(self,destination_id: str, bins_edges: list):
        combinations = list(itertools.permutations(bins_edges))

        routes = []

        for route in combinations : 
            routes.append(list(route))

        for i in range(len(routes)):
            routes[i] = [self.ev.edge] + routes[i] + [destination_id]

        travel_times = {}
        distances = {}
        dic_routes = {}
        
        for p_route in routes :
            travel_times[tuple(p_route)] = 0
            distances[tuple(p_route)] = 0
            dic_routes[tuple(p_route)] = []
            
            for i in range(len(p_route)):
                if i == len(p_route) - 1:
                    break
                route = traci.simulation.findRoute(p_route[i], p_route[i + 1], vType=self.ev.vehicle_type)

                if not route.edges:
                    raise RuntimeError(
                        f"No route found from '{p_route[i]}' to '{p_route[i + 1]}'."
                    )

                travel_times[tuple(p_route)] += route.travelTime
                distances[tuple(p_route)] += route.length
                dic_routes[tuple(p_route)].append(list(route.edges))

        # Find the route with the minimum travel time
        min_travel_time_route = min(travel_times, key=travel_times.get)

        # Get the corresponding route edges
        
        route_edges = []

        for route in dic_routes[min_travel_time_route]:
            for edge in route:
                if not route_edges or route_edges[-1] != edge:
                    route_edges.append(edge)


        # Route metrics
        print("\n========== New Route ==========")
        print(f"Vehicle ID     : {self.ev.vehicle_id}")
        print(f"Simulation Time: {traci.simulation.getTime():.1f} s")
        print(f"Origin Edge    : {self.ev.edge}")
        print(f"Destination    : {destination_id}")
        print(f"Edges          : {route_edges}")
        print(f"Number of Edges: {len(route_edges)}")
        print(f"Length         : {distances[min_travel_time_route]:.2f} m")
        print(f"Travel Time    : {travel_times[min_travel_time_route]:.2f} s")
        print(f"Cost           : {0:.2f}")  # Placeholder for cost calculation
        print("===============================\n")

        traci.vehicle.setRoute(self.ev.vehicle_id, route_edges)

    def new_route(self, destination_id: str):
            """Recalculate and assign a new route to the vehicle."""
            route = traci.simulation.findRoute(self.ev.edge, destination_id, vType=self.ev.vehicle_type)

            if not route.edges:
                raise RuntimeError(
                    f"No route found from '{self.ev.edge}' to '{destination_id}'."
                )

            if self.ev.vehicle_id not in traci.vehicle.getIDList():
                raise RuntimeError(
                    f"Vehicle '{self.ev.vehicle_id}' is not in the simulation."
                )
        
            # Route metrics
            print("\n========== New Route ==========")
            print(f"Vehicle ID     : {self.ev.vehicle_id}")
            print(f"Simulation Time: {traci.simulation.getTime():.1f} s")
            print(f"Origin Edge    : {self.ev.edge}")
            print(f"Destination    : {destination_id}")
            print(f"Edges          : {route.edges}")
            print(f"Number of Edges: {len(route.edges)}")
            print(f"Length         : {route.length:.2f} m")
            print(f"Travel Time    : {route.travelTime:.2f} s")
            print(f"Cost           : {route.cost:.2f}")
            print("===============================\n")

            traci.vehicle.setRoute(self.ev.vehicle_id, route.edges)

    def set_target(self, destination_id: str):
        """Change the vehicle destination and let SUMO recalculate the route."""
        print("\n========= Change Target =========")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Old destination : {self.ev.dest}")
        print(f"New Target      : {destination_id}")

        traci.vehicle.changeTarget(self.ev.vehicle_id, destination_id)

        print("=================================\n")

    # -----------------------------
    # Vehicle dynamic control
    # -----------------------------
    def slow_down(self):
        if self.ev.dist_to_dest <= 0:
            return

        # acceleration
        a = (-self.ev.speed ** 2) / (2 * self.ev.dist_to_dest)

        a = max(-self.ev.max_decel, a)

        if abs(a) < 1e-6:
            return

        traci.vehicle.setAcceleration(self.ev.vehicle_id, a, self.ev.step_length)

    def stop_car(self):
        traci.vehicle.setSpeed(self.ev.vehicle_id, 0)

    def resume_speed_control(self):
        traci.vehicle.setSpeed(self.ev.vehicle_id, -1)

    # -----------------------------
    # State control and logistics
    # -----------------------------
    def recharge_substation(self, station_edge: str, station_id: str):
        """Route the vehicle to a charging station and schedule a charging stop."""
        print("\n====== Charging Request ======")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Station ID      : {station_id}")
        print(f"Station Edge    : {station_edge}")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print("==============================")

        traci.vehicle.changeTarget(self.ev.vehicle_id, station_edge)
        traci.vehicle.setChargingStationStop(
            self.ev.vehicle_id,
            station_id,
            duration=self.stop_duration,
            flags=self.charging_stop_flag
        )

    def stop_parking(self, parking_edge: str, parking_id: str):
        
        print("\n======= Parking Request =======")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Parking ID      : {parking_id}")
        print(f"Parking Edge    : {parking_edge}")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print("===============================")
        
        traci.vehicle.changeTarget(self.ev.vehicle_id, parking_edge)
        traci.vehicle.setParkingAreaStop(
            self.ev.vehicle_id,
            parking_id,
            duration=self.stop_duration
        )
    
    def waste_collection(self, bin_edge: str, bin_id: str):
        
        print("\n======= Collection Request =======")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Bin ID      : {bin_id}")
        print(f"Bin Edge    : {bin_edge}")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print("===============================")
        
        traci.vehicle.setParkingAreaStop(
            self.ev.vehicle_id,
            bin_id,
            duration=90
        )

        collection_flag = True
        
        return collection_flag

    def go_to_landfill(self, landfill_edge: str, landfill_id: str):

        """Route the vehicle to the landfill."""
        print("\n======= Landfill Request =======")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Landfill ID      : {landfill_id}")
        print(f"Landfill Edge    : {landfill_edge}")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print("===============================")

        traci.vehicle.changeTarget(self.ev.vehicle_id, landfill_edge)
        traci.vehicle.setParkingAreaStop(
            self.ev.vehicle_id,
            landfill_id,
            duration=self.stop_duration
        )

    def skip_stop(self):
        """Resume the vehicle after a scheduled stop."""
        traci.vehicle.resume(self.ev.vehicle_id)

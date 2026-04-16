import traci
import numpy as np
from .__action__ import Action  
from .__interpreter_and_set__ import Interpreter_and_set

class EV:
    def __init__(self,id:str,vehicle_type:str,params:dict,reflength):
        # -----------------------------
        # Vehicle identification
        # -----------------------------
        self.id = id                                                                # Vehicle ID
        self.vType = vehicle_type                                                   # Vehicle type

        # -----------------------------
        # Instance of classes
        # -----------------------------  
        self.action = Action(id,vehicle_type)
        self.int_and_set = Interpreter_and_set(id)

        # -----------------------------
        # Actions
        # -----------------------------  
        self.actions_dic = {
            0: self.action.continue_travel,
            1: self.action.skip_stop,
            2: self.action.stop_parking,
            3: self.action.recharge_substation}
        
        # -----------------------------
        # Add the vehicle
        # -----------------------------
        self._addveh(params)

        # -----------------------------
        # Energy state
        # -----------------------------
        self.energy = 0.0                                                           # Current battery charge (kWh)
        self.energy_loaded = 0.0                                                    # Total energy charged over time (kWh)
        self.energy_regen = 0.0                                                     # Total regenerated energy (kWh)
        self.capacity = 0.0                                                         # Total battery capacity (kWh)
        self.soc = 0.0                                                              # State of charge (%)

        # -----------------------------
        # Location and route
        # -----------------------------
        self.edge = None                                                            # Current edge
        self.dest = None                                                            # Current intermediate destination
        self.final_dest = None                                                      # Final trip destination
        self.penultimate_dest = None                                                # Penultimate final trip destination

        # -----------------------------
        # Motion
        # -----------------------------
        self.speed = 0.0                                                            # Current speed (m/s)
        self.consumption = 0.0                                                      # Instantaneous electric consumption (kWh/s)
        self.speedKm = 0.0                                                          # Current speed (km/h)
        self.acceleration = 0.0                                                     # current aceleration (m/s²)
        self.max_speed = traci.vehicle.getMaxSpeed(self.id)                         # Max speed (m/s)
        self.max_accel = traci.vehicle.getAccel(self.id)                            # Mac aceleration (m/s²)

        # -----------------------------
        # Distances
        # -----------------------------
        self.dist_to_dest  = np.inf                                                 # Distance to current destination (m)
        self.dist_to_final = np.inf                                                 # Distance to final destination (m)
        self.total_dist    = np.inf                                                 # Total distance traveled (m)
        self.current_pos   = np.inf                                                 # Vehicle position in lane
        self.dist_to_local = np.inf                                                 # Distance to specific location(m)
        self.reflength   = reflength                                                # Total network lengh

        # -----------------------------
        # ID list
        # -----------------------------
        self.parkings = traci.parkingarea.getIDList()
        self.stations = traci.chargingstation.getIDList()

        # -----------------------------
        # Charging stations (EVSE)
        # -----------------------------
        self.station_edges = {
            s: traci.chargingstation.getLaneID(s).split("_")[0]
            for s in self.stations
        }

        self.station_pos = {
            s: traci.chargingstation.getStartPos(s)
            for s in self.stations
        }

        station_edges_set = set(self.station_edges.values())

        # -----------------------------
        # Parkings
        # -----------------------------
        self.parking_edges = {}
        self.parking_pos = {}

        for p in self.parkings:
            lane_id = traci.parkingarea.getLaneID(p)
            edge_id = lane_id.split("_")[0]

            if edge_id in station_edges_set:
                continue

            self.parking_edges[p] = edge_id
            self.parking_pos[p] = traci.parkingarea.getStartPos(p)

        # -----------------------------
        # Initial initialization
        # -----------------------------
        self.all_up()
        pass
    
    # -----------------------------
    # Information update
    # -----------------------------
    def update_energy(self):
        self.energy = round(float(traci.vehicle.getParameter(self.id, "device.battery.chargeLevel")) / 1000, 2)
        self.energy_loaded = round(float(traci.vehicle.getParameter(self.id, "device.battery.energyCharged")) / 1000, 2)
        self.capacity = round(float(traci.vehicle.getParameter(self.id, "device.battery.capacity")) / 1000, 2)
        self.soc = round(100 * self.energy / self.capacity, 2) 

    def update_route(self):
        edges =  self._get_route_edges()
        self.edge = traci.vehicle.getRoadID(self.id)
        self.dest = edges[-1]

    def update_finalroute(self):
        edges = self._get_route_edges()
        if len(edges) >=2 :
            self.final_dest = edges[-1]
            self.penultimate_dest = edges[-2]
        else :
            self.final_dest = edges[-1]
            self.penultimate_dest = self.final_dest           
    
    def _get_route_edges(self):
        route_id = traci.vehicle.getRouteID(self.id)
        return traci.route.getEdges(route_id)
    
    def update_motion(self):
        self.speed = round(traci.vehicle.getSpeed(self.id), 2)
        self.consumption = round(traci.vehicle.getElectricityConsumption(self.id) / 1000, 2)
        self.speedKm = round(self.speed * 3.6, 2)
        self.acceleration= round(traci.vehicle.getAcceleration(self.id),2)

    def update_distances(self):
        self.dist_to_dest = round(
            traci.vehicle.getDrivingDistance(
                self.id,
                self.dest,
                traci.lane.getLength(f"{self.dest}_0")
            ),
            2
        )

        self.dist_to_final = round(
            traci.vehicle.getDrivingDistance(
                self.id,
                self.final_dest,
                traci.lane.getLength(f"{self.final_dest}_0")
            ),
            2
        )

        self.total_dist = round(traci.vehicle.getDistance(self.id), 2)

        self.current_pos = traci.vehicle.getLanePosition(self.id)

        self.leader =  traci.vehicle.getLeader(self.id) #(near veh_id, dist to near veh_id)

        if self.leader is not None:
            self.gap = self.leader[1] #dist to near veh
        else:
            self.gap = np.inf

        return

    def update_distance_to_location(self, target_edge: str, target_pos: float = 0.0):
        if self.edge == "" or self.edge.startswith(":"):
                self.dist_to_local = np.inf
                return
        
        dist = traci.simulation.getDistanceRoad(
                self.edge,
                self.current_pos,
                target_edge,
                target_pos,
                isDriving=True
            )
        
        if dist < 0:
                self.dist_to_local = np.inf
        else:
                self.dist_to_local = dist

        return
    
    def distances_to_parkings(self):
        if self.edge == "" or self.edge.startswith(":"):
            return {park: np.inf for park in self.parkings}

        distances = {}

        for parking in self.parkings:
            edge_id = self.parking_edges[parking]
            pos = self.parking_pos[parking]

            dist = traci.simulation.getDistanceRoad(
                self.edge,
                self.current_pos,
                edge_id,
                pos,
                isDriving=True
            )

            distances[parking] = np.inf if dist < 0 else round(dist, 2)

        return distances
    
    def distances_to_stations(self):
        if self.edge == "" or self.edge.startswith(":"):
            return {station: np.inf for station in self.stations}

        distances = {}

        for evse in self.stations:
            edge_id = self.station_edges[evse]
            pos = self.station_pos[evse]

            dist = traci.simulation.getDistanceRoad(
                self.edge,
                self.current_pos,
                edge_id,
                pos,
                isDriving=True
            )

            distances[evse] = np.inf if dist < 0 else round(dist, 2)

        return distances
    
    def general_up(self): 
        self.update_energy()
        self.update_motion()
        self.update_route()
        self.update_distances()
        
        return
    
    def all_up(self): 
        self.update_energy()
        self.update_motion()
        self.update_route()
        self.update_finalroute()
        self.update_distances()
        
        return
    
    """Add vehicle"""
    def _addveh(self,params: dict):
        
        self.action.create_route(params)

        traci.vehicle.add(
                    vehID=self.id,
                    routeID=params["route_id"],
                    typeID=self.vType,
                    depart=traci.simulation.getTime()
        )

        self.action.set_route(params)
        return
        
    """Entry and Exit"""
    def step(self, vector: list, params :dict):
        if self.id not in traci.vehicle.getIDList():
            return
        
        self.actions_dic[int(np.argmax(vector))](params)

        return

    def get_obs(self):
        obs = [
            self.speed /  self.max_speed,
            self.acceleration / self.max_accel,
            self.soc/100,
            self.dist_to_dest / self.reflength,
            self.dist_to_final / self.reflength,
            min(self.gap / 50, 1)
        ]
        return obs

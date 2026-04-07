import numpy as np
import traci
from pathlib import Path
import csv

class EV:
    def __init__(self, id:str,type:str,dest:str, reflength):
        # -----------------------------
        # Vehicle identification
        # -----------------------------
        self.id = id                                                                # Vehicle ID
        self.type = type                                                            # Vehicle type

        # -----------------------------
        # Instance of classes
        # -----------------------------  
        self.up = self.Update(self)
        self.action = self.Actions(self)
        self.registration = self.Registers(self)
        self.int_and_set = self.Interpreter_and_set(self)

        # -----------------------------
        # Actions
        # -----------------------------  
        self.actions_dic = {
            0: self.action.continue_travel,
            1: self.action.skip_stop,
            2: self.action.stopParking,
            3: self.action.recharge_substation}
        
        # -----------------------------
        # Add the vehicle
        # -----------------------------
        self._addveh(dest)

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
        # Stop state (bitmask)
        # -----------------------------
        self.stop_state = 0                                                         # Current stop state (bitmask)

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
        self.up.all_up()
        pass
        
    class Update :
        def __init__(self, ev):
            self.ev = ev

        def update_energy(self):
            ev = self.ev
            ev.energy = round(float(traci.vehicle.getParameter(ev.id, "device.battery.chargeLevel")) / 1000, 2)
            ev.energy_loaded = round(float(traci.vehicle.getParameter(ev.id, "device.battery.energyCharged")) / 1000, 2)
            ev.capacity = round(float(traci.vehicle.getParameter(ev.id, "device.battery.capacity")) / 1000, 2)
            ev.soc = round(100 * ev.energy / ev.capacity, 2) 

        def update_route(self):
            ev = self.ev
            route_id = traci.vehicle.getRouteID(ev.id)
            edges = traci.route.getEdges(route_id)
            ev.edge = traci.vehicle.getRoadID(ev.id)
            ev.dest = edges[-1]

        def update_finalroute(self):
            ev = self.ev
            route_id = traci.vehicle.getRouteID(ev.id)
            edges = traci.route.getEdges(route_id)
            if len(edges) >=2 :
                ev.final_dest = edges[-1]
                ev.penultimate_dest = edges[-2]
            else :
                ev.final_dest = edges[-1]
                ev.penultimate_dest = ev.final_dest           
        
        def update_motion(self):
            ev = self.ev
            ev.speed = round(traci.vehicle.getSpeed(ev.id), 2)
            ev.consumption = round(traci.vehicle.getElectricityConsumption(ev.id) / 1000, 2)
            ev.speedKm = round(ev.speed * 3.6, 2)
            ev.acceleration= round(traci.vehicle.getAcceleration(ev.id),2)

        def update_distances(self):
            ev = self.ev
            ev.dist_to_dest = round(
                traci.vehicle.getDrivingDistance(
                    ev.id,
                    ev.dest,
                    traci.lane.getLength(f"{ev.dest}_0")
                ),
                2
            )

            ev.dist_to_final = round(
                traci.vehicle.getDrivingDistance(
                    ev.id,
                    ev.final_dest,
                    traci.lane.getLength(f"{ev.final_dest}_0")
                ),
                2
            )

            ev.total_dist = round(traci.vehicle.getDistance(ev.id), 2)

            ev.current_pos = traci.vehicle.getLanePosition(ev.id)

            ev.leader =  traci.vehicle.getLeader(ev.id) #(near veh_id, dist to near veh_id)

            
            if ev.leader is not None:
                ev.gap = ev.leader[1] #dist to near veh
            else:
                ev.gap = np.inf

            return

        def update_distance_to_location(self, target_edge: str, target_pos: float = 0.0):
            ev = self.ev
            if ev.edge == "" or ev.edge.startswith(":"):
                    ev.dist_to_local = np.inf
                    return
            
            dist = traci.simulation.getDistanceRoad(
                    ev.edge,
                    ev.current_pos,
                    target_edge,
                    target_pos,
                    isDriving=True
                )
            
            if dist < 0:
                    ev.dist_to_local = np.inf
            else:
                    ev.dist_to_local = dist

            return
        
        def distances_to_parkings(self):
            ev = self.ev

            if ev.edge == "" or ev.edge.startswith(":"):
                return {park: np.inf for park in ev.parkings}

            distances = {}

            for parking in ev.parkings:
                edge_id = ev.parking_edges[parking]
                pos = ev.parking_pos[parking]

                dist = traci.simulation.getDistanceRoad(
                    ev.edge,
                    ev.current_pos,
                    edge_id,
                    pos,
                    isDriving=True
                )

                distances[parking] = np.inf if dist < 0 else round(dist, 2)

            return distances
        
        def distances_to_stations(self):
            ev = self.ev

            if ev.edge == "" or ev.edge.startswith(":"):
                return {station: np.inf for station in ev.stations}

            distances = {}

            for evse in ev.stations:
                edge_id = ev.station_edges[evse]
                pos = ev.station_pos[evse]

                dist = traci.simulation.getDistanceRoad(
                    ev.edge,
                    ev.current_pos,
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

        pass

    class Actions :  ###### mudar a lógica completamente !
        def __init__(self, ev):
            self.ev = ev

        def continue_travel(self, dest=None):
            return
        
        def recharge_substation(self,dest):                                              # dest vector = [station edge, station id]
            ev = self.ev

            traci.vehicle.changeTarget(ev.id, dest[0])
            traci.vehicle.setChargingStationStop(ev.id, dest[1], duration=43200,flags=1)
            return 
        
        def stopParking(self,dest):                                                      # dest vector = [parking edge, parking_id]
            ev = self.ev
            traci.vehicle.changeTarget(ev.id, dest[0])
            traci.vehicle.setParkingAreaStop(ev.id, dest[1], duration=43200)
            return
        
        def skip_stop(self,dest = None):
            ev = self.ev
            traci.vehicle.resume(ev.id)
            return
        
        def create_route(self,dest):                                                     # destination vector = [destination id, route id,edge initial]
            ev = self.ev
            route = traci.simulation.findRoute(dest[2], dest[0], vType=ev.type)
            traci.route.add(dest[1], route.edges)
            return 
               
        def newroute(self,dest):                                                         # destination vector = [destination id]
            ev = self.ev

            current_route = traci.vehicle.getRoute(ev.id)

            route = traci.simulation.findRoute(ev.final_dest, dest[0], vType=ev.type)
            
            if ev.penultimate_dest == ev.edge : 
                new_route = [current_route[-2]] + [current_route[-1]] + list(route.edges)[1:]
                traci.vehicle.setRoute(ev.id, new_route)

            if ev.final_dest == ev.edge :
                traci.vehicle.setRoute(ev.id, route.edges)
            
            return 
        
        def returnfinaldest(self,dest = None):  
            ev = self.ev
            traci.vehicle.changeTarget(ev.id, ev.final_dest)
            return
        pass
    
    class Interpreter_and_set :
        def __init__(self, ev):
            self.ev = ev
        
        def stop(self):
            ev = self.ev
            
            state = int(traci.vehicle.getStopState(ev.id))
            ev.stop_state = state

            states = []

            if state & 1:
                states.append("stopped")
            if state & 2:
                states.append("parking")
            if state & 4:
                states.append("triggered")
            if state & 8:
                states.append("container triggered")
            if state & 16:
                states.append("bus stop")
            if state & 32:
                states.append("container stop")
            if state & 64:
                states.append("charging station")
            if state & 128:
                states.append("parking area")

            return states if states else ["moving"]

        def color(self):
            ev = self.ev

            if ev.soc <= 10:
                color = (139, 0, 0, 255)        # dark red (extreme)
            elif ev.soc <= 20:
                color = (255, 0, 0, 255)        # red
            elif ev.soc <= 30:
                color = (255, 69, 0, 255)       # dark orange
            elif ev.soc <= 40:
                color = (255, 140, 0, 255)      # low orange
            elif ev.soc <= 50:
                color = (255, 165, 0, 255)      # orange
            elif ev.soc <= 60:
                color = (255, 215, 0, 255)      # yellow gold
            elif ev.soc <= 70:
                color = (255, 255, 0, 255)      # yellow
            elif ev.soc <= 80:
                color = (173, 255, 47, 255)     # low green
            elif ev.soc <= 90:
                color = (127, 255, 0, 255)      # light green
            else:
                color = (0, 255, 0, 255)        # green (full batery)
            
            traci.vehicle.setColor(ev.id, color)
            return
        
        pass
           
    class Registers: 
        
        def __init__(self, ev):
            self.ev = ev
        
            base_dir = Path(__file__).resolve().parent.parent 
            self.pasta_results = base_dir / "sumo" / "results"
            self.pasta_results.mkdir(parents=True, exist_ok=True) 
            
            self.arquivo_csv = self.pasta_results / f"{ev.id}.csv"

            self.setup_results_and_headers()
            
        def setup_results_and_headers(self):

            # Remove only this EV's CSV file (if it exists)
            if self.arquivo_csv.exists():
                self.arquivo_csv.unlink()

            cabecalho = [
                "== ID ==",
                "== Velocity (km/h) ==",
                "== Current route ==",
                "== Distance traveled (m) ==",
                "== Destination ==",
                "== Distance to destination (m) ==",
                "== Type ==",
                "== Battery level (%) ==",
                "== Timestamp =="
            ]

            # Create file and write header
            with open(self.arquivo_csv, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(cabecalho)

        def register(self, TIME):
            ev = self.ev

            with open(self.arquivo_csv, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    ev.id,
                    ev.speedKm,
                    ev.edge,
                    ev.total_dist,
                    ev.dest,
                    ev.dist_to_dest,
                    ev.type,
                    ev.soc,
                    TIME       
                ])
        
    """Add vehicle"""
    def _addveh(self,dest):                                                              # dest vector = [destination_edge, route_id]
        self.action.create_route(dest)

        traci.vehicle.add(
                    vehID=self.id,
                    routeID=dest[1],
                    typeID=self.type,
                    depart=traci.simulation.getTime()
        )

        return
        
    """Entry and Exit"""
    def step(self, vector, dest):
        if self.id not in traci.vehicle.getIDList():
            return
        
        if np.sum(vector) != 1:
            #ERROR!
            return   
        
        self.actions_dic[int(np.argmax(vector))](dest)

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
    
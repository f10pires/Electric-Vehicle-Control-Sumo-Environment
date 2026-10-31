from Results.example1.results.__register__ import Register
from datetime import datetime, timedelta
from WastecollectionEnv.sumo import Sumo
from WastecollectionEnv.ev import EV
from WastecollectionEnv.sumo.__get_places__ import PlacesManager
# from EVGarbageCollector.TruckControl.__init__ import Control
import gymnasium as gym
import numpy as np
import random
import traci

# Fix random seed for reproducibility
random.seed(42)

class Initgeneral:
    def __init__(self, config, start):
        self.start = start
        self.Δt = float(config["step"]) 
        self.time = start
    
    def step(self):
        self.time = self.time + timedelta(seconds=self.Δt)



class EVGarbageTruck(gym.Env):
    def __init__(self, config, vehicles, start):
        super().__init__()

        self.config     = config
        simulation      = Sumo(self.config)
        simulation.run()                              # Start simulation     
        
        self.ids        = vehicles.keys()
        self.general    = Initgeneral(config, start)   # Time control and global parameters
        self.evs       = [EV(vehicles, vehicle_id) for vehicle_id in self.ids]
        self.places    = PlacesManager()

        a = 1
        
        
        # self.demand = self.ev.bin_edges                    # Demand list

        # -----------------------------
        # Data registration
        # -----------------------------
        # self.registration = Register(self.id)              # Logger / data recorder

       
        self.done = False                                  # Episode termination flag
        
 
        self.refTime = [-1, True]                          # Auxiliary time control
        self.max_time = simulation.max_time
        
    def step(self, action: list):

        reward = 0

        # 1. Decode action
        decod_action = int("".join(map(str, action[:5])), 2)
        place_destin = action[5:]

        if self.done:
            return

        # 2. Simulation step
        traci.simulationStep()

        if self.id not in traci.vehicle.getIDList():
            self.done = True
            self.registration.close()
            return

        # 3. Execute action
        action_name = self.ev.action.action_dict[decod_action]

        if action_name == "Continue Travel":
            self.ev.action.continue_travel()

        elif action_name == "New Route":
            position = place_destin.index(1)
            position_id = self.dic_positions(position)

            edge_dest = (
                self.actions_and_edges["recharge_stations_dict"].get(position_id, {}).get("edge")
                or self.actions_and_edges["parkings_dict"].get(position_id, {}).get("edge")
                or self.actions_and_edges["bins_dict"].get(position_id, {}).get("edge")
            )

            self.ev.action.new_route(edge_dest)

        elif action_name == "Return to Dest":
            self.ev.action.set_target(self.ev.final_dest)

        elif action_name == "Stop":
            self.ev.action.stop_car()
            self.refTime = [traci.simulation.getTime(), False]

        elif action_name == "Back normal speed":
            self.ev.action.resume_speed_control()

        elif action_name == "Recharge":
            position = place_destin.index(1)
            
            position_id = (
                self.ev.int_and_set.places.charging_stations.get(position)
            )

            station_edge = (
                self.parameters["recharge_stations_dict"]
                .get(position_id, {})
                .get("edge")
            )

            self.ev.action.recharge_substation(station_edge, position_id)

        elif action_name == "Parking":
            position = place_destin.index(1)
            
            position_id = (
                self.ev.int_and_set.places
                .get_parking_area_id(position)
            )

            parking_edge = (
                self.parameters["parking_areas_dict"]
                .get(position_id, {})
                .get("edge")
            )

            self.ev.action.stop_parking(parking_edge, position_id)

        elif action_name == "Skip stop":
            self.ev.action.continue_travel()

        # 4. Check stop timer
        if not self.refTime[1]:
            if traci.simulation.getTime() - self.refTime[0] >= self.stop_duration:
                self.ev.action.resume_speed_control()
                self.refTime = [-1, True]

        # 5. Check simulation termination
        if traci.simulation.getTime() >= self.simulation.max_time:
            self.done = True
            self.registration.close()
        
        return # state, reward, terminated, truncated, info

    def get_obs(self):
        # observation: what the agent can "see" - EV position, velocity, soc, etc.

        self.ev.general_up(self)

        obs = [self.ev.soc, self.ev.dist_to_final, self.ev.dist_to_dest, self.ev.edge, self.ev.dest, self.ev.final_dest, self.ev.speed]

        return obs


    def reset(self):
        # termo aleatório de inicialização

        pass

    def close(self):
        traci.close()
        pass

    def updateinfo(self):
        info = {
            "speedKm": self.ev.speedKm,
            "edge": self.ev.edge,
            "total_dist": self.ev.total_dist,
            "dest": self.ev.dest,
            "dist_to_dest": self.ev.dist_to_dest,
            "vType": self.ev.vehicle_type,
            "soc": self.ev.soc
        }
        self.registration.accumulate_information(info, self.general.time)

        return

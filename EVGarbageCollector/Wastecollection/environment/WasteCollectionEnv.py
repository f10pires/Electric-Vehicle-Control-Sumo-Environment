from datetime import datetime, timedelta
from EVGarbageCollector.Wastecollection.sumo import Sumo
from EVGarbageCollector.Wastecollection.sumo.results.__register__ import Register
from EVGarbageCollector.Wastecollection.ev import EV
from EVGarbageCollector.TruckControl.__init__ import Control
import random
import traci
import gymnasium as gym
import numpy as np

# Fix random seed for reproducibility
random.seed(42)

class Initgeneral:
    def __init__(self, config, start,tools: dict):
        self.start = start
        self.Δt = float(config["step"]) 
        self.time = start
        self.tools = tools
    
    def step(self):
        self.time = self.time + timedelta(seconds=self.Δt)

    pass


class EVGarbageTruck(gym.Env):
    def __init__(self, config, vehicle, start, tools,parameters):
        super().__init__()

        # -----------------------------
        # General simulation settings
        # -----------------------------
        self.general = Initgeneral(config, start, tools)   # Time control and global parameters
        self.simulation = Sumo(config)                     # SUMO interface

        # -----------------------------
        # EV agent
        # -----------------------------
        self.ev = EV(vehicle)
        
        self.config = config
        self.demand = self.ev.bin_edges                    # Demand list

        # -----------------------------
        # Data registration
        # -----------------------------
        self.registration = Register(self.id)              # Logger / data recorder

        # -----------------------------
        # Control
        # -----------------------------
        self.done = False                                  # Episode termination flag
        self.waiting_time = config["Waiting_time"]         # Auxiliary time control
        self.refTime = [-1, True]                          # Auxiliary time control
        self.control = Control(self.get_obs(), parameters)                              
        
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

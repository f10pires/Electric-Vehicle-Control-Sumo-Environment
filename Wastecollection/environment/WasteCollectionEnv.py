from datetime import datetime, timedelta
from sumo import Sumo
from sumo.results.__register__ import Register
from ev import EV
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
    def __init__(self, config, vehicle, start, tools):
        super().__init__()

        # -----------------------------
        # General simulation settings
        # -----------------------------
        self.general = Initgeneral(config, start, tools)   # Time control and global parameters
        self.simulation = Sumo(config)                     # SUMO interface

        # -----------------------------
        # Vehicle identification
        # -----------------------------
        self.id = list(vehicle.keys())[0]                  # Vehicle ID
        self.type = vehicle[self.id]["type"]               # Vehicle type
        self.init_route = vehicle[self.id]["initial_route"]# Initial route

        # -----------------------------
        # EV agent
        # -----------------------------
        self.ev = EV(
            self.id,
            self.type,
            self.init_route,
            config["mod dist"],
            config["step"]
        )
        
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
        
    def step(self, action:list,params: tuple = (), return_to_landfill: bool = False):
        
        reward = 0

        if self.done:
            return
        
        # step do ev
        traci.simulationStep()

        if self.id not in traci.vehicle.getIDList():
            self.done = True
            self.registration.close()
            return

        self.ev.general_up()
        self.ev.int_and_set.color()
        self.ev.step(action,params)
        self.general.step()
        self.updateinfo()
        
        if self.config["min_dist_dest"] <self.ev.dist_to_final < self.config["max_dist_dest"]:
            self.ev.action.slow_down()

        if self.ev.edge == self.ev.final_dest and self.ev.dist_to_final  <= self.config["min_dist_dest"] and self.refTime[1]:
            traci.vehicle.setSpeed(self.id, 0)

        # "return_to_landfill"    
        if (self.ev.edge == self.ev.final_dest and self.ev.dist_to_final <= self.config["min_dist_dest"]) and (self.ev.speed == 0) and (return_to_landfill): 

            landfill = "-E70"
            landfillid = "ParkAreaL"
            self.ev.action.new_route(landfill)

            self.ev.all_up()
            self.ev.action.stop_car()

            self.ev.action.go_to_landfill(landfill, landfillid)

            if self.refTime[1]:
                refTime = traci.simulation.getTime() + self.waiting_time
                self.refTime = [refTime,False]

        if traci.simulation.getTime() - self.refTime[0] >= 0 and not(self.refTime[1]):
            self.ev.action.resume_speed_control()
            self.refTime = [-1,True]

        if traci.simulation.getTime() == self.simulation.max_time:
            self.done = True
            self.registration.close()
        
        return # state, reward, terminated, truncated, info

    def get_obs(self):
        obs = []
        # observaçõe do ambiente (horário etc)

        # observações do EV
        pass


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

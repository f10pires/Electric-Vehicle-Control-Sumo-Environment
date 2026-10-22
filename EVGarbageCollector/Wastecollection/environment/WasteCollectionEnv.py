from datetime import datetime, timedelta
from EVGarbageCollector.Wastecollection.sumo import Sumo
from EVGarbageCollector.Wastecollection.sumo.results.__register__ import Register
from EVGarbageCollector.Wastecollection.ev import EV
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
        
    def step(self, action:list):
        
        reward = 0
        decod_number = int("".join(map(str, action)), 2)
        
        if self.done:
            return
        
        # step do ev
        traci.simulationStep()

        if self.id not in traci.vehicle.getIDList():
            self.done = True
            self.registration.close()
            return




        if traci.simulation.getTime() - self.refTime[0] >= 0 and not(self.refTime[1]):
            self.ev.action.resume_speed_control()
            self.refTime = [-1,True]

        if traci.simulation.getTime() == self.simulation.max_time:
            self.done = True
            self.registration.close()
        
        return # state, reward, terminated, truncated, info

    def get_obs(self):
        # observation: what the agent can "see" - EV position, velocity, soc, etc.

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

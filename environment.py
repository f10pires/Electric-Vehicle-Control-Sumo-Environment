from datetime import datetime, timedelta
from parking import PARKING
from evse import EVSE
from sumo import Sumo
from sumo.results.__register__ import Register
import numpy as np
from ev import EV
import random
import traci
import gymnasium as gym

class Initgeneral:
    def __init__(self, config, start):
        self.start = start
        self.Δt = float(config["step"]) 
        self.time = start
    
    def step(self):
        self.time = self.time + timedelta(seconds=self.Δt)

    pass


class SingleEV(gym.Env):
    def __init__(self, config, vehicle, start):
        super().__init__()
        self.general = Initgeneral(config, start)
        self.simulation = Sumo(config)   # cria objeto da classe Sumo

        self.informations = {}

        self.id = list(vehicle.keys())[0]
        self.type = vehicle[self.id]["type"]
        self.init_route = vehicle[self.id]["initial_route"]
       
        self.ev = EV(self.id, self.type, self.init_route, config["mod dist"])
        self.registration = Register(self.id)
        self.done = False

        
    def step(self, action:list,params : dict):
        
        reward = 0
        
        # step do ev
        traci.simulationStep()

        self.ev.general_up()
        self.ev.int_and_set.color(self.ev.soc)
        self.ev.step(action,params)

        if traci.simulation.getTime() == self.simulation.max_time:
            self.done = True
            self.registration.close()
        
        self.updateinfo()

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
            "vType": self.ev.vType,
            "soc": self.ev.soc
        }
        self.registration.accumulate_information(info, self.general.time)

        return
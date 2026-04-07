from datetime import datetime, timedelta
from parking import PARKING
import gymnasium as gym
from sumo import Sumo
from evse import EVSE
import numpy as np
from ev import EV
import random
import traci

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


        self.id = list(vehicle.keys())[0]
        self.type = vehicle[self.id]["type"]
        self.init_route = vehicle[self.id]["initial route"]
       
        self.ev = EV(self.id, self.type, self.init_route, config["mod dist"])
        
        self.done = False
        
    def step(self, action):
        reward = 0
        
        # step do ev
        traci.simulationStep()

        # mexer na rota se for necessário
        self.ev.step()

        if traci.simulation.getTime() == self.simulation.max_time:
            self.done = True

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
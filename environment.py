from datetime import datetime, timedelta
from parking import PARKING
from evse import EVSE
from sumo import Sumo
from sumo.results.__register__ import Register
from ev import EV
import random
import traci
import gymnasium as gym

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


class SingleEV(gym.Env):
    def __init__(self, config, vehicle, start, tools):
        super().__init__()

        # -----------------------------
        # General simulation settings
        # -----------------------------
        self.general = Initgeneral(config, start, tools)   # Time control and global parameters
        self.simulation = Sumo(config)                     # SUMO interface

        # -----------------------------
        # Information storage
        # -----------------------------
        self.informations = {}                             # Dictionary to store environment info

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
            config["mod dist"]
        )

        # -----------------------------
        # Data registration
        # -----------------------------
        self.registration = Register(self.id)              # Logger / data recorder

        # -----------------------------
        # Control
        # -----------------------------
        self.done = False                                  # Episode termination flag
        self.waiting_time = config["Waiting_time"]         # Auxiliary time control
        self.refTime = [None, True]                        # Auxiliary time control
        
    def step(self, action:list,params : dict):
        
        reward = 0
        
        # step do ev
        traci.simulationStep()

        self.ev.general_up()
        self.ev.int_and_set.color(self.ev.soc)
        self.ev.step(action,params)
        self.general.step()
        
        if self.ev.edge == self.ev.penultimate_dest :
            self.ev.action.slow_down({"current_speed": self.ev.speed,
                                      "final_speed": 0,
                                      "distance_to_destination":self.ev.dist_to_final - 10})

        if self.ev.edge == self.ev.final_dest and self.ev.speed == 0: 
            streets = sorted(self.general.tools["streets"])
            dest = random.choice([x for x in streets if x != self.ev.final_dest])
            self.ev.action.new_route({"destination_id": dest})

            self.ev.all_up()
            self.ev.action.stop_car({})

            if self.refTime[1]:
                refTime = traci.simulation.getTime() + self.waiting_time
                self.refTime = [refTime,False]

        if traci.simulation.getTime() == self.refTime[0] and not(self.refTime[1]):
            self.ev.action.back_normal_speed({})
            self.refTime = [None,True]

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
from datetime import datetime, timedelta
from pathlib import Path
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
    def __init__(
        self, config, vehicles, start, additional, bins, evses, landfills, results_path
    ):
        super().__init__()

        self.additional = additional
        self.bins       = bins
        self.evses      = evses
        self.landfills  = landfills
        self.destinations = {**bins, **evses, **landfills}
        self.action_decoder = list(bins) + list(evses) + list(landfills)
        self.results_path   = Path(results_path)
        self.config         = config.copy()
        self.config["additional-files"] = (
            self.results_path / "additional.add.xml"
        ).as_posix()
        simulation = Sumo(
            self.config, additional=additional, bins=bins, evses=evses, landfills=landfills
        )
        self.simulation = simulation
        simulation.run()                              # Start simulation     
        
        self.ids        = vehicles.keys()
        self.general    = Initgeneral(config, start)   # Time control and global parameters
        self.evs        = [EV(vehicles, vehicle_id) for vehicle_id in self.ids]
        
        
        self.done       = False                                  # Episode termination flag
        self.max_time   = simulation.max_time
       
        
    def step(self, action: dict):

        reward = 0

        # filtrar se a action já está no destino. Se já estiver faça nada
        for ev in self.evs:
            destination = self.action_decoder[action[ev.vehicle_id].index(1)]
            if ev.final_dest == self.destinations[destination]["edge"]:
                continue

            else:
                # O EV tem que ir para o outro destino
                

                a = 1
                



        # 1. Decode action
        # decod_action = int("".join(map(str, action[:5])), 2)
        # place_destin = action[5:]

        if self.done:
            return

        # 2. Simulation step
        traci.simulationStep()

        #if self.id not in traci.vehicle.getIDList():
        #    self.done = True
        #    self.registration.close()
        #     return

        # 3. Execute action
        # action_name = self.ev.action.action_dict[decod_action]


        # Check simulation termination
        if traci.simulation.getTime() >= self.simulation.max_time:
            self.done = True
            # self.registration.close()
        
        return # state, reward, terminated, truncated, info

    def get_obs(self):
        # observation: what the agent can "see" - EV position, velocity, soc, etc.

        obs = dict()
        for ev in self.evs:
            ev.general_up()
            obs[ev.vehicle_id] = [ev.soc, ev.dist_to_final, ev.dist_to_dest, ev.edge, ev.dest, ev.final_dest, ev.speed]
            obs[ev.vehicle_id] = [
                #time encoder
                # ev.speed / ev.max_speed,
                # ev.acceleration / ev.max_accel,
                # soc
                # truck trash capacity
                # for distance to bins
                # for distance to evses
                # for distance to landfills
            ]
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

from evse import EVSE
from ev import EV
from parking import PARKING
from sumo import Sumo
import traci
import json
import random
from datetime import datetime, timedelta
from environment import SingleEV

# Fix random seed for reproducibility
random.seed(42)

"""Load config at config/config.json"""
with open(r'config/config.json', 'r') as config_file:
    config = json.load(config_file)

with open('config/vehicles.json', "r", encoding="utf-8") as f:
    vehicles = json.load(f)

def main():
    start = datetime.strptime("2026-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    simulation = Sumo(config)   # cria objeto da classe Sumo
    simulation.run()
    env = SingleEV(config, vehicles, start)

    chargers = EVSE("Charge_ParkD")  # cria objeto da classe EVSE
    park = PARKING("ParkAreaC")

    
    while traci.simulation.getTime() < simulation.max_time:
        env.ev.up.general_up()
        env.ev.int_and_set.color()
        env.ev.step([1,0,0,0,0,0,0,0],[])
        env.ev.registration.register(traci.simulation.getTime())
        
        if env.ev.edge == env.ev.final_dest : 
            w= random.choice([x for x in simulation.streets if x != env.ev.final_dest])
            env.ev.action.newroute([w])
            env.ev.up.all_up()

        
        simulation.step()


if __name__ == "__main__":
    main()
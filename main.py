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

        env.step([1,0,0,0,0,0,0,0],{})

        
        if env.ev.edge == env.ev.penultimate_dest :
            env.ev.action.slow_down({"current_speed": env.ev.speed,
                                      "final_speed": 0,
                                      "distance_to_destination":env.ev.dist_to_final - 5})

        if env.ev.edge == env.ev.final_dest and env.ev.speed == 0: 

            w= random.choice([x for x in simulation.streets if x != env.ev.final_dest])
            env.ev.action.new_route({"destination_id": w})
            env.ev.all_up()
            env.ev.action.stop_car({})
        

        simulation.step()

if __name__ == "__main__":
    main()
from evse import EVSE
from ev import EV
from parking import PARKING
from sumo import Sumo
import traci
import json
from datetime import datetime, timedelta
from environment import SingleEV


"""Load config at config/config.json"""
with open(r'config/config.json', 'r') as config_file:
    config = json.load(config_file)

with open('config/vehicles.json', "r", encoding="utf-8") as f:
    vehicles = json.load(f)

def main():
    start = datetime.strptime("2026-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    simulation = Sumo(config)
    simulation.run()                              # Start simulation 
    
    tools = {}
    tools["streets"] = simulation.streets    
    env = SingleEV(config, vehicles, start,tools)


    chargers = EVSE("Charge_ParkD")  # cria objeto da classe EVSE
    park = PARKING("ParkAreaC")

    
    while traci.simulation.getTime() < simulation.max_time:
        env.step([1,0,0,0,0,0,0,0],{})

if __name__ == "__main__":
    main()
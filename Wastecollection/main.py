from sumo import Sumo
import traci
import json
from datetime import datetime, timedelta
from environment.WasteCollectionEnv import EVGarbageTruck

"""Load config at config/config.json"""
with open(r'Wastecollection/config/config.json', 'r') as config_file:
    config = json.load(config_file)

with open('Wastecollection/config/vehicles.json', "r", encoding="utf-8") as f:
    vehicles = json.load(f)

def main():
    start = datetime.strptime("2026-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    simulation = Sumo(config)
    simulation.run()                              # Start simulation     
    tools = {}
    tools["streets"] = simulation.streets    
    env = EVGarbageTruck(config, vehicles, start,tools)
    
    while traci.simulation.getTime() < simulation.max_time:
        env.step([1,0,0,0,0,0,0,0],())

        
        if env.ev.soc <= 50 :
            env.ev.action.recharge_substation("-E70", "Charge_ParkB")

        if env.ev.soc == 100 and  "charging station" in env.ev.int_and_set.stop(): 
            env.ev.action.set_target(env.ev.final_dest)
            env.ev.action.skip_stop()

if __name__ == "__main__":
    main()

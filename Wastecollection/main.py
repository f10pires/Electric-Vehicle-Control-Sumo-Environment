from sumo import Sumo
import traci
import json
from datetime import datetime, timedelta
from environment.WasteCollectionEnv import EVGarbageTruck
import random

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

    return_to_landfill = False

    dic_flag_bins = {
        "BIN-A" : False, 
        "BIN-B" : False,
        "BIN-C" : False,
        "BIN-D" : False
    }

    bins_id_to_check = []

    while traci.simulation.getTime() < simulation.max_time:
        env.step([1,0,0,0,0,0,0,0],(),return_to_landfill)
        need_check = random.choices([True,False], weights=[5,95])[0]

        if env.ev.soc <= 10 :
            env.ev.action.recharge_substation("-E70", "Charge_ParkB")

        if env.ev.soc == 100 and  "charging station" in env.ev.int_and_set.stop(): 
            env.ev.action.set_target(env.ev.final_dest)
            env.ev.action.skip_stop()

        if need_check and not(return_to_landfill):
            dic_flag_bins = check_bins(dic_flag_bins)
            return_to_landfill = True




        "pensar daqui para baixo"
        if return_to_landfill : 
            bins_id_to_check = [x for x in dic_flag_bins if dic_flag_bins[x] == True]


            for x in bins_id_to_check : 
                collection_flag = env.ev.action.collect_garbage(x)

                if collection_flag : 
                    dic_flag_bins[x] = False
                    print(f"Collected garbage from {x}")
                else : 
                    print(f"Failed to collect garbage from {x}")





       

def check_bins(dic):
    BA = random.choices([True,False], weights=[10,90])[0]
    BB = random.choices([True,False], weights=[30,70])[0]
    BC = random.choices([True,False], weights=[50,50])[0]
    BD = random.choices([True,False], weights=[80,20])[0]

    list = [BA,BB,BC,BD]
    count = 0
    for x in dic : 
        dic[x] = list[count]
        count += count

    return dic


def binary(flag, wait_deposity): 
    if flag : 
       return flag  

if __name__ == "__main__":
    main()

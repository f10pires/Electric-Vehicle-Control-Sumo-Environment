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
    need_check = True

    while traci.simulation.getTime() < simulation.max_time:
        env.step([1,0,0,0,0,0,0,0],(),return_to_landfill)

        if env.ev.soc <= 10 :
            env.ev.action.recharge_substation("-E70", "Charge_ParkB")

        
        if env.ev.soc == 100 and  "charging station" in env.ev.int_and_set.stop(): 
            env.ev.action.set_target(env.ev.final_dest)
            env.ev.action.skip_stop()

        else : 
            if need_check and not(return_to_landfill):
                dic_flag_bins = check_bins(dic_flag_bins)
                return_to_landfill = True
                need_check = False

                if "parking" in env.ev.int_and_set.stop() : 
                    env.ev.action.skip_stop()

            if return_to_landfill : 
                bins_id_to_check = [x for x in dic_flag_bins if dic_flag_bins[x] == True]
                edges_to_check = []
                
                for x in env.ev.bin_edges :
                    if x in bins_id_to_check : 
                        edges_to_check.append(env.ev.bin_edges[x])

                env.ev.action.find_optimal_bincollection("-E70", edges_to_check)
                print("aaaaaaaaaaaaaaaaaa upei")
                env.ev.all_up()

                for i in range(len(bins_id_to_check)):
                    bin_id = bins_id_to_check[i]
                    bin_edge = env.ev.bin_edges[bin_id]
                    env.ev.action.waste_collection(bin_edge, bin_id)
                
                destinations = []
                for dest in edges_to_check :
                    destinations.append(dest)

                env.ev.dest = destinations[0]

                return_to_landfill = False

                print(f"Bins to check : {bins_id_to_check}")
                print(f"Edges to check : {edges_to_check}")

        if env.ev.edge in destinations :
            destinations.remove(env.ev.edge)
            if len(destinations) > 0 :
                env.ev.dest = destinations[0]

        else: 
            env.ev.action.stop_parking(env.ev.final_dest, "ParkAreaL")

        '''
        if env.ev.dest == env.ev.final_dest and "parking" in env.ev.int_and_set.stop() : 
            need_check = random.choices([True,False], weights=[5,95])[0]

            if need_check : 
                dic_flag_bins = check_bins(dic_flag_bins)

                if "parking" in env.ev.int_and_set.stop() : 
                    print("faaaah", env.ev.dest, env.ev.final_dest)
                    env.ev.action.skip_stop()
        '''


def check_bins(dic):
    '''
    BA = random.choices([True,False], weights=[10,90])[0]
    BB = random.choices([True,False], weights=[30,70])[0]
    BC = random.choices([True,False], weights=[50,50])[0]
    BD = random.choices([True,False], weights=[80,20])[0]
    '''
    BA = True
    BB = True
    BC = True
    BD = True
    

    list = [BA,BB,BC,BD]
    count = 0
    for x in dic : 
        dic[x] = list[count]
        count += 1

    return dic


def binary(flag, wait_deposity): 
    if flag : 
       return flag  

if __name__ == "__main__":
    main()

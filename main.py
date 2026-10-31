from WastecollectionEnv.environment import WasteCollectionEnv
from WastecollectionEnv.sumo import Sumo
from TruckControl import Control
from datetime import datetime
import numpy as np
import traci
import json


FILE_PATH = "data/example1/"


# Load config and data file
with open(FILE_PATH + "config.json", 'r') as config_file:
    config = json.load(config_file)


with open(FILE_PATH + "vehicles.json", "r", encoding="utf-8") as f:
    vehicles = json.load(f)


start = datetime.strptime("2026-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

# Create enviromnent
env = WasteCoellectionEnv.EVGarbageTruck(config, vehicles, start)


env.step(list(np.zeros(37)))

while traci.simulation.getTime() < env.max_time:
    obs = env.get_obs()

    a = 1

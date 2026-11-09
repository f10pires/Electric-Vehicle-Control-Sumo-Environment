from WastecollectionEnv.environment import WasteCollectionEnv
from WastecollectionEnv.sumo import Sumo
from TruckControl import Control
from datetime import datetime
from pathlib import Path
import numpy as np
import traci
import json


FILE_PATH = Path("data/example1")
RESULTS_PATH = Path("Results") / FILE_PATH.name


# Load config and data file
with open(FILE_PATH / "config.json", encoding="utf-8") as config_file:
    config = json.load(config_file)


with open(FILE_PATH / "vehicles.json", encoding="utf-8") as f:
    vehicles = json.load(f)


with open(FILE_PATH / "additional.json", encoding="utf-8") as f:
    additional = json.load(f)

with open(FILE_PATH / "bins.json", encoding="utf-8") as f:
    bins = json.load(f)

with open(FILE_PATH / "evses.json", encoding="utf-8") as f:
    evses = json.load(f)

with open(FILE_PATH / "landfills.json", encoding="utf-8") as f:
    landfills = json.load(f)


start = datetime.strptime("2026-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

# Create enviromnent
env = WasteCollectionEnv.EVGarbageTruck(
    config=config,
    vehicles=vehicles,
    start=start,
    additional=additional,
    bins=bins,
    evses=evses,
    landfills=landfills,
    results_path=RESULTS_PATH,
)


env.step(list(np.zeros(37)))

while traci.simulation.getTime() < env.max_time:
    obs = env.get_obs()

    a = 1

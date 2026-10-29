import traci
import random
from sumolib import checkBinary
import subprocess
from WastecollectionEnv.Tools.convert_fleet import convert_fleet
from WastecollectionEnv.Tools.random_vehicles import RandomVeh

class Sumo:

    def __init__(self, config):
        
        self.sumoBinary = checkBinary('sumo-gui')
        self.max_time = 0
         
        self.config = config
        self.refdist = 0.0
        self.edges = [] 
        self.streets = set()       

        # Fix random seed for reproducibility
        random.seed(int(self.config["seed"]))
        pass

    def run(self): 

        #Control
        self.uptime()
        self.generate_activity_trips()
        self.apply_fleet_conversion()
        self.startSim()

        #Surface
        self.up_streets()
        self.streetslist = list(self.streets)
        self.reference_length()
        self.randomveh = RandomVeh(self.config)

        return
    
    def uptime(self):
        self.max_time = self.config["Max_time"]
        return self.max_time
    
    def generate_activity_trips(self):
        
        # activitygen is usually located in the same directory as SUMO
        # If 'activitygen' is not in the PATH, use the full path
        activitygen_bin = "activitygen" 

        cmd = [
            activitygen_bin,
            "--net-file", self.config["net-file"],
            "--stat-file",  self.config["stat"], 
            "--output-file", self.config["route-files"],
            #"--random", 
            "--seed", self.config["seed"]
        ]
        
        try:
            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print("[OK] Activity-based routes generated successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error while executing activitygen: {e}")
        except FileNotFoundError:
            print("Error: 'activitygen' executable not found in PATH.")

    def apply_fleet_conversion(self):
        """Convert the fleet using the configuration received from the entry point."""
        convert_fleet(self.config)

    #Starts the simulation
    def startSim(self):
        traci.start(
            [
                self.sumoBinary,
                '--net-file', self.config["net-file"],
                '--route-files', self.config["route-mista"],
                '--additional-files', self.config["additional-files"],
                '--step-length', self.config["step"], 
                '--delay', self.config["delay"],
                '--statistic-output', self.config["statistic-output"],
                '--duration-log.statistics', 'true',
                '--tripinfo-output', self.config["tripinfo-output"],
                '--gui-settings-file', self.config["gui-settings-file"],
                '--seed', self.config["seed"],
                '--time-to-teleport', self.config["time-to-teleport"],   
                '--start',      
                '--quit-on-end' 
            ]
        )
    
    # Advance the simulation
    def step(self):
        traci.simulationStep()
        return
    
    def up_streets(self):
        self.edges = traci.edge.getIDList()

        for edge in self.edges:
            if not edge.startswith(":"):  # ignore internal edges 
                self.streets.add(edge.split("_")[0])
        return
    
    def reference_length(self):
        
        start = random.choice(self.streetslist)
        
        far_edge, _ = self.farthest_from(start)

        _, self.refdist = self.farthest_from(far_edge)
        
        return self.refdist

    def farthest_from(self,source_edge):
        max_dist = 0.0
        farthest_edge = source_edge

        for target_edge in self.streetslist:
            try:
                dist = traci.simulation.getDistanceRoad(
                    source_edge, 0,
                    target_edge, 0,
                    isDriving=True
                )
                if dist > max_dist:
                    max_dist = dist
                    farthest_edge = target_edge
            except:
                continue

        return farthest_edge, max_dist

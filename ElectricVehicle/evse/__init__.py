import traci

class EVSE:
    def __init__(self,id:str):
        # -----------------------------
        # Station identification
        # -----------------------------
        self.id = id            # Charging station ID
        
        # -----------------------------
        # Network location
        # -----------------------------
        self.lane = traci.chargingstation.getLaneID(self.id)                # Lane where the station is located
        self.edge = traci.lane.getEdgeID(self.lane)                         # Corresponding edge
        self.startPos = traci.chargingstation.getStartPos(self.id)          # Start position of the station on the lane (meters)
        self.endPos = traci.chargingstation.getEndPos(self.id)              # End position of the station on the lane (meters)
        
        # -----------------------------
        # Vehicles charging
        # -----------------------------
        self.veh = []            # IDs of vehicles currently charging
        self.veh_count = 0       # Number of vehicles stopped at the station

        # -----------------------------
        # Power and efficiency
        # -----------------------------
        self.power = 0.0         # Current charging power (W)
        self.eff = 0.0           # Station efficiency (%)

        # -----------------------------
        # Operational parameters
        # -----------------------------
        self.delay = 0.0         # Delay before charging starts
        self.transit = 0         # 0 = not allowed, 1 = allows charging while moving

        pass
    
    def status(self):
        # Vehicles connected to the station
        self.veh = traci.chargingstation.getVehicleIDs(self.id)
        self.veh_count = traci.chargingstation.getVehicleCount(self.id)

        # Charging power
        self.power = traci.chargingstation.getChargingPower(self.id)

        # Station efficiency
        self.eff = traci.chargingstation.getEfficiency(self.id)
        
        # Delay before charging starts
        self.delay = traci.chargingstation.getChargeDelay(self.id)

        # Charging while moving
        self.transit = traci.chargingstation.getChargeInTransit(self.id)
        return

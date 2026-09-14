import traci

class PARKING:
    def __init__(self, id: str): #posição
        # -----------------------------
        # Parking identification
        # -----------------------------
        self.id = id            # ID of the parking area

        # -----------------------------
        # Vehicles in the parking
        # -----------------------------
        self.veh = []           # IDs of parked vehicles
        self.veh_count = 0      # Number of vehicles in the parking

        # -----------------------------
        # Location in the network
        # -----------------------------
        self.lane = traci.parkingarea.getLaneID(self.id)                    # Lane where the parking area is located
        self.edge = traci.lane.getEdgeID(self.lane)                         # Corresponding edge
        self.startPos = traci.parkingarea.getStartPos(self.id)              # Start position of the parking area on the lane (meters)
        self.endPos = traci.parkingarea.getEndPos(self.id)                  # End position of the parking area on the lane (meters)

        pass
    def status(self):
        """
        Updates the dynamic state of the parking area.
        Should be called every simulation step.
        """

        # Vehicles parked in the area
        self.veh = traci.parkingarea.getVehicleIDs(self.id)

        # Total number of vehicles in the parking
        self.veh_count = traci.parkingarea.getVehicleCount(self.id)
        return

import traci

class PlacesManager:

    def __init__(self):

        # -----------------------------
        # ID lists
        # -----------------------------
        self.parkings = sorted(traci.parkingarea.getIDList())
        self.stations = sorted(traci.chargingstation.getIDList())
        self.bins = []

        # -----------------------------
        # Charging stations (EVSE)
        # -----------------------------
        self.station_edges = {
            s: traci.chargingstation.getLaneID(s).split("_")[0]
            for s in self.stations
        }

        self.station_pos = {
            s: traci.chargingstation.getStartPos(s)
            for s in self.stations
        }

        # -----------------------------
        # Parkings and Bins
        # -----------------------------
        self.parking_edges = {}
        self.parking_pos = {}

        self.bin_edges = {}
        self.bin_pos = {}

        for p in self.parkings:

            lane_id = traci.parkingarea.getLaneID(p)
            edge_id = lane_id.split("_")[0]
            pos = traci.parkingarea.getStartPos(p)

            # Ignore parking areas located on charging station edges
            if edge_id in self.station_edges.values():
                continue

            if p.startswith("BIN-"):
                self.bins.append(p)
                self.bin_edges[p] = edge_id
                self.bin_pos[p] = pos

            else:
                self.parking_edges[p] = edge_id
                self.parking_pos[p] = pos
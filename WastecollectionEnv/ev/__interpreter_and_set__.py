import traci 

class InterpreterAndSet :
    def __init__(self, ev):
        self.ev = ev
        self.places = Places()
    
    def stop(self):
        state = int(traci.vehicle.getStopState(self.ev.vehicle_id))

        states = []

        if state & 1:
            states.append("stopped")
        if state & 2:
            states.append("parking")
        if state & 4:
            states.append("triggered")
        if state & 8:
            states.append("container triggered")
        if state & 16:
            states.append("bus stop")
        if state & 32:
            states.append("container stop")
        if state & 64:
            states.append("charging station")
        if state & 128:
            states.append("parking area")

        return states if states else ["moving"]

    def color(self):

        if self.ev.soc <= 10:
            color = (139, 0, 0, 255)        # dark red (extreme)
        elif self.ev.soc <= 20:
            color = (255, 0, 0, 255)        # red
        elif self.ev.soc <= 30:
            color = (255, 69, 0, 255)       # dark orange
        elif self.ev.soc <= 40:
            color = (255, 140, 0, 255)      # low orange
        elif self.ev.soc <= 50:
            color = (255, 165, 0, 255)      # orange
        elif self.ev.soc <= 60:
            color = (255, 215, 0, 255)      # yellow gold
        elif self.ev.soc <= 70:
            color = (255, 255, 0, 255)      # yellow
        elif self.ev.soc <= 80:
            color = (173, 255, 47, 255)     # low green
        elif self.ev.soc <= 90:
            color = (127, 255, 0, 255)      # light green
        else:
            color = (0, 255, 0, 255)        # green (full battery)
        
        traci.vehicle.setColor(self.ev.vehicle_id, color)
        return

class Places:
    def __init__(self):
        self.charging_stations = {
            9: "Charge_ParkA",
            10: "Charge_ParkB",
            11: "Charge_ParkC",
            12: "Charge_ParkD",
            13: "Charge_ParkE",
            14: "Charge_ParkF",
            15: "Charge_ParkW",
            16: "Charge_ParkX",
        }

        self.parking_areas = {
            17: "ParkAreaA",
            18: "ParkAreaB",
            19: "ParkAreaG",
            20: "ParkAreaH",
            21: "ParkAreaI",
            22: "ParkAreaJ",
            23: "ParkAreaM",
            24: "ParkAreaN",
            25: "ParkAreaO",
            26: "ParkAreaP",
            27: "ParkAreaQ",
            28: "ParkAreaR",
            29: "ParkAreaS",
            30: "ParkAreaT",
            31: "ParkAreaU",
            32: "ParkAreaV",
        }

        self.bins = {
            33: "BIN-A",
            34: "BIN-B",
            35: "BIN-C",
            36: "BIN-D",
        }

    def get_id(self, position: int) -> str | None:
        if position in self.charging_stations:
            return self.charging_stations[position]

        if position in self.parking_areas:
            return self.parking_areas[position]

        return self.bins.get(position)
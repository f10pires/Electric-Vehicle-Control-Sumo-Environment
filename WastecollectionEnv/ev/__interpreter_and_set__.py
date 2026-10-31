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
            6: "Charge_ParkA",
            7: "Charge_ParkB",
            8: "Charge_ParkC",
            9: "Charge_ParkD",
            10: "Charge_ParkE",
            11: "Charge_ParkF",
            12: "Charge_ParkW",
            13: "Charge_ParkX",
        }

        self.parking_areas = {
            14: "ParkAreaA",
            15: "ParkAreaB",
            16: "ParkAreaG",
            17: "ParkAreaH",
            18: "ParkAreaI",
            19: "ParkAreaJ",
            20: "ParkAreaM",
            21: "ParkAreaN",
            22: "ParkAreaO",
            23: "ParkAreaP",
            24: "ParkAreaQ",
            25: "ParkAreaR",
            26: "ParkAreaS",
            27: "ParkAreaT",
            28: "ParkAreaU",
            29: "ParkAreaV",
        }

        self.bins = {
            30: "BIN-A",
            31: "BIN-B",
            32: "BIN-C",
            33: "BIN-D",
        }

    def get_id(self, position: int) -> str | None:
        if position in self.charging_stations:
            return self.charging_stations[position]

        if position in self.parking_areas:
            return self.parking_areas[position]

        return self.bins.get(position)
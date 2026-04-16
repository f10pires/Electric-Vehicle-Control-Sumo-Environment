import traci 

class Interpreter_and_set :
    def __init__(self, id: str):
        self.id = id
        pass
    
    def stop(self):
        state = int(traci.vehicle.getStopState(self.id))

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

    def color(self,soc):

        if soc <= 10:
            color = (139, 0, 0, 255)        # dark red (extreme)
        elif soc <= 20:
            color = (255, 0, 0, 255)        # red
        elif soc <= 30:
            color = (255, 69, 0, 255)       # dark orange
        elif soc <= 40:
            color = (255, 140, 0, 255)      # low orange
        elif soc <= 50:
            color = (255, 165, 0, 255)      # orange
        elif soc <= 60:
            color = (255, 215, 0, 255)      # yellow gold
        elif soc <= 70:
            color = (255, 255, 0, 255)      # yellow
        elif soc <= 80:
            color = (173, 255, 47, 255)     # low green
        elif soc <= 90:
            color = (127, 255, 0, 255)      # light green
        else:
            color = (0, 255, 0, 255)        # green (full batery)
        
        traci.vehicle.setColor(self.id, color)
        return
    
    pass
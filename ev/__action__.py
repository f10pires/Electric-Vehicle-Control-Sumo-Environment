import traci

class Actions : 
    def __init__(self, id:str,type:str):
        self.id = id
        self.type = type
        pass

    def continue_travel(self, dest=None):
        return
        
    def recharge_substation(self,dest):                                              # dest vector = [station edge, station id]
        traci.vehicle.changeTarget(self.id, dest[0])
        traci.vehicle.setChargingStationStop(self.id, dest[1], duration=43200,flags=1)
        return 
        
    def stopParking(self,dest):                                                      # dest vector = [parking edge, parking_id]
        traci.vehicle.changeTarget(self.id, dest[0])
        traci.vehicle.setParkingAreaStop(self.id, dest[1], duration=43200)
        return
        
    def skip_stop(self,dest = None):
        traci.vehicle.resume(self.id)
        return
        
    def create_route(self,dest):                                                     # destination vector = [destination id, route id,edge initial]
        route = traci.simulation.findRoute(dest[2], dest[0], vType=self.type)
        traci.route.add(dest[1], route.edges)
        traci.vehicle.setRouteID(self.id, dest[1])
        return 
               
    def newroute(self,dest):                                                         # destination vector = [destination id]
        current_edge = traci.vehicle.getRoadID(self.id)
        route = traci.simulation.findRoute(current_edge, dest[0], vType=self.type)
        traci.vehicle.setRoute(self.id, route.edges)
        return 

    def set_target(self, dest):                                                     # destination vector = [destination id]                         
        traci.vehicle.changeTarget(self.id, dest[0])
        
    def stop_car(self,dest = None):
        traci.vehicle.setSpeed(self.id, 0)
        return
    
    def back_normal_speed(self,dest=None):
        traci.vehicle.setSpeed(self.id, -1)
        return
    pass
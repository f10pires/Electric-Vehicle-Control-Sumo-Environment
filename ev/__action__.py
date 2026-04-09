import traci

class Action: 
    def __init__(self, id: str, vehicle_type: str):
        self.id = id
        self.vType = vehicle_type
        pass

    # -----------------------------
    # Route control
    # -----------------------------  
    def continue_travel(self, params: dict):
        return
        
    def create_route(self, params: dict):  
        dest_id = params["destination_id"]
        init_edge = params["initial_edge"]
        route_id = params["route_id"]

        route = traci.simulation.findRoute(init_edge,dest_id, vType=self.vType)
        
        traci.route.add(route_id, route.edges)
        return 

    def set_route(self, params: dict):  
        route_id = params["route_id"]
        traci.vehicle.setRouteID(self.id, route_id)
        return            
        
    def new_route(self, params: dict): 
        dest_id = params["destination_id"]

        current_edge = traci.vehicle.getRoadID(self.id)

        route = traci.simulation.findRoute(current_edge, dest_id, vType=self.vType)

        traci.vehicle.setRoute(self.id, route.edges)
        return 

    def set_target(self, params: dict):  
        dest_id = params["destination_id"]
        traci.vehicle.changeTarget(self.id, dest_id)
        return
    
    # -----------------------------
    # Vehicle dynamic control
    # -----------------------------  
    def slow_down(self, params: dict): 
        v0 = params["current_speed"]  
        vf = params["final_speed"]  
        d  = params["distance_to_destination"]  

        if d <= 0:
            return

        # acceleration
        a = (vf**2 - v0**2) / (2 * d)

        if abs(a) < 1e-6:
            return

        # required time
        t = (vf - v0) / a

        t = abs(t)  # ensure positive time

        if t < 1e-6:
            return
        
        traci.vehicle.slowDown(self.id, vf, t)
        return

    def stop_car(self, params: dict):
        traci.vehicle.setSpeed(self.id, 0)
        return
    
    def back_normal_speed(self, params: dict):
        traci.vehicle.setSpeed(self.id, -1)
        return 
    
    # -----------------------------
    # State control and logistics
    # -----------------------------   
    def recharge_substation(self, params: dict):  
        station_edge = params["station_edge"]
        station_id = params["station_id"]

        traci.vehicle.changeTarget(self.id, station_edge)
        traci.vehicle.setChargingStationStop(self.id, station_id, duration=43200, flags=1)
        return 
        
    def stop_parking(self, params: dict): 
        park_edge = params["parking_edge"]
        park_id = params["parking_id"]     

        traci.vehicle.changeTarget(self.id, park_edge)
        traci.vehicle.setParkingAreaStop(self.id, park_id, duration=43200)
        return
        
    def skip_stop(self, params: dict):
        traci.vehicle.resume(self.id)
        return
        

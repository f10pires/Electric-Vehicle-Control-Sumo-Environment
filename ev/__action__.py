import traci

class Action:
    def __init__(self, vehicle_id: str, vehicle_type: str, step_length: float):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.step_length = float(step_length)
        self.stop_duration = 43200
        self.charging_stop_flag = 1

    # -----------------------------
    # Route control
    # -----------------------------
    def continue_travel(self):
        pass

    def create_route(self, destination_id: str, initial_edge: str, route_id: str):
        route = traci.simulation.findRoute(
            initial_edge,
            destination_id,
            vType=self.vehicle_type
        )
        traci.route.add(route_id, route.edges)

    def set_route(self, route_id: str):
        traci.vehicle.setRouteID(self.vehicle_id, route_id)

    def new_route(self, destination_id: str, current_edge: str):
        route = traci.simulation.findRoute(current_edge, destination_id, vType=self.vehicle_type)
        traci.vehicle.setRoute(self.vehicle_id, route.edges)

    def set_target(self, destination_id: str):
        traci.vehicle.changeTarget(self.vehicle_id, destination_id)

    # -----------------------------
    # Vehicle dynamic control
    # -----------------------------
    def slow_down(self, current_speed: float, distance_to_destination: float, max_decel: float):
        if distance_to_destination <= 0:
            return

        # acceleration
        a = (-current_speed ** 2) / (2 * distance_to_destination)

        a = max(-max_decel, a)

        if abs(a) < 1e-6:
            return

        traci.vehicle.setAcceleration(self.vehicle_id, a, self.step_length)

    def stop_car(self):
        traci.vehicle.setSpeed(self.vehicle_id, 0)

    def back_normal_speed(self):
        traci.vehicle.setSpeed(self.vehicle_id, -1)

    # -----------------------------
    # State control and logistics
    # -----------------------------
    def recharge_substation(self, station_edge: str, station_id: str):
        traci.vehicle.changeTarget(self.vehicle_id, station_edge)
        traci.vehicle.setChargingStationStop(
            self.vehicle_id,
            station_id,
            duration=self.stop_duration,
            flags=self.charging_stop_flag
        )

    def stop_parking(self, parking_edge: str, parking_id: str):
        traci.vehicle.changeTarget(self.vehicle_id, parking_edge)
        traci.vehicle.setParkingAreaStop(
            self.vehicle_id,
            parking_id,
            duration=self.stop_duration
        )

    def skip_stop(self):
        traci.vehicle.resume(self.vehicle_id)

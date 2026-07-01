import traci

class Action:
    def __init__(self, ev):
        self.ev = ev
        self.stop_duration = 43200
        self.charging_stop_flag = 1

    # -----------------------------
    # Route control
    # -----------------------------
    def continue_travel(self):
        return


    def new_route(self, destination_id: str):
        """Recalculate and assign a new route to the vehicle."""
        route = traci.simulation.findRoute(self.ev.edge, destination_id, vType=self.ev.vehicle_type)

        if not route.edges:
            raise RuntimeError(
                f"No route found from '{self.ev.edge}' to '{destination_id}'."
            )

        if self.ev.vehicle_id not in traci.vehicle.getIDList():
            raise RuntimeError(
                f"Vehicle '{self.ev.vehicle_id}' is not in the simulation."
            )
    
        # Route metrics
        print("\n========== New Route ==========")
        print(f"Vehicle ID     : {self.ev.vehicle_id}")
        print(f"Simulation Time: {traci.simulation.getTime():.1f} s")
        print(f"Origin Edge    : {self.ev.edge}")
        print(f"Destination    : {destination_id}")
        print(f"Edges          : {route.edges}")
        print(f"Number of Edges: {len(route.edges)}")
        print(f"Length         : {route.length:.2f} m")
        print(f"Travel Time    : {route.travelTime:.2f} s")
        print(f"Cost           : {route.cost:.2f}")
        print("===============================\n")

        traci.vehicle.setRoute(self.ev.vehicle_id, route.edges)

    def set_target(self, destination_id: str):
        """Change the vehicle destination and let SUMO recalculate the route."""
        print("\n========= Change Target =========")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Old destination : {self.ev.dest}")
        print(f"New Target      : {destination_id}")

        traci.vehicle.changeTarget(self.ev.vehicle_id, destination_id)

        print("=================================\n")

    # -----------------------------
    # Vehicle dynamic control
    # -----------------------------
    def slow_down(self):
        if self.ev.dist_to_dest <= 0:
            return

        # acceleration
        a = (-self.ev.speed ** 2) / (2 * self.ev.dist_to_dest)

        a = max(-self.ev.max_decel, a)

        if abs(a) < 1e-6:
            return

        traci.vehicle.setAcceleration(self.ev.vehicle_id, a, self.ev.step_length)

    def stop_car(self):
        traci.vehicle.setSpeed(self.ev.vehicle_id, 0)

    def resume_speed_control(self):
        traci.vehicle.setSpeed(self.ev.vehicle_id, -1)

    # -----------------------------
    # State control and logistics
    # -----------------------------
    def recharge_substation(self, station_edge: str, station_id: str):
        """Route the vehicle to a charging station and schedule a charging stop."""
        print("\n====== Charging Request ======")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Station ID      : {station_id}")
        print(f"Station Edge    : {station_edge}")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print("==============================")

        traci.vehicle.changeTarget(self.ev.vehicle_id, station_edge)
        traci.vehicle.setChargingStationStop(
            self.ev.vehicle_id,
            station_id,
            duration=self.stop_duration,
            flags=self.charging_stop_flag
        )

    def stop_parking(self, parking_edge: str, parking_id: str):
        
        print("\n======= Parking Request =======")
        print(f"Vehicle ID      : {self.ev.vehicle_id}")
        print(f"Parking ID      : {parking_id}")
        print(f"Parking Edge    : {parking_edge}")
        print(f"Simulation Time : {traci.simulation.getTime():.1f} s")
        print("===============================")
        
        traci.vehicle.changeTarget(self.ev.vehicle_id, parking_edge)
        traci.vehicle.setParkingAreaStop(
            self.ev.vehicle_id,
            parking_id,
            duration=self.stop_duration
        )

    def skip_stop(self):
        """Resume the vehicle after a scheduled stop."""
        traci.vehicle.resume(self.ev.vehicle_id)


class Control:

    def __init__(self, obs: list, parameters: dict):
        self.obs = obs
        self.parameters = parameters

    def update_obs(self, obs: list):
        self.obs = obs
        return self.obs

    def get_action(self):

        soc = self.obs[0]
        dist_to_final = self.obs[1]
        dist_to_dest = self.obs[2]
        edge_id = self.obs[3]
        edge_dest = self.obs[4]
        edge_finaldest = self.obs[5]
        speed = self.obs[6]
        status = self.obs[7]

        self.Recharge_stations = self.parameters["recharge_stations"]
        self.Parking_lots = self.parameters["parkings"]
        self.Bin_lots = self.parameters["bins"]

        places = (
            self.Recharge_stations
            + self.Parking_lots
            + self.Bin_lots
        )

        actions = self.parameters["actions"]

        self.vector_size = len(places) + len(actions)

        action = [0] * self.vector_size

        if soc < 0.55:
            action[1] = 1
            action[2] = 1
            action[9] = 1

        else:
            action[0] = 1

        return action


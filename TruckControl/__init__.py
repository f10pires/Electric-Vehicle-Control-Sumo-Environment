
class Control:

    def __init__(self, parameters: dict):
        self.parameters = parameters


    def get_action(self, obs):

        soc             = obs[0]
        dist_to_final   = obs[1]
        dist_to_dest    = obs[2]
        edge_id         = obs[3]
        edge_dest       = obs[4]
        edge_finaldest  = obs[5]
        speed           = obs[6]
        status          = obs[7]

        self.Recharge_stations  = self.parameters["recharge_stations"]
        self.Parking_lots       = self.parameters["parkings"]
        self.Bin_lots           = self.parameters["bins"]

        places = (
            self.Recharge_stations
            + self.Parking_lots
            + self.Bin_lots
        )

        actions = self.parameters["actions"]

        self.vector_size = len(places) + len(actions)

        action = [0] * self.vector_size

        if soc < 0.55:
            action[3] = 1
            action[6] = 1

        else:
            action[0] = 1

        return action


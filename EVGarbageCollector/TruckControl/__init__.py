class Control :

    def __init__(self, obs : list, parameters : dict):
        self.obs = obs
        self.parameters = parameters

    def update_obs(self,obs : list):
        self.obs = obs
        return self.obs

    def get_action(self):
        soc             = self.obs[0]
        dist_to_final   = self.obs[1]
        dist_to_dest    = self.obs[2]
        edge_id         = self.obs[3]
        edge_dest       = self.obs[4]
        edge_finaldest  = self.obs[5]
        speed           = self.obs[6]
        status          = self.obs[7]


        Recharge_stations = self.parameters["recharge_stations"]
        Parking_lots = self.parameters["parkings"]
        Bin_lots = self.parameters["bins"]

        places = Recharge_stations + Parking_lots + Bin_lots
        actions = self.parameters["actions"]

        vector_size = places.__len__() + actions.__len__()

        action = []

        for i in range(vector_size):
            action.append(0)
        

        if soc < 0.55:
            action = [0,0,1]

        elif dist_to_final < 100:
            if edge_finaldest == edge_id and "stopped" in status:
                action = [0,1,0]
            else:
                action = [0,1,1]

        return action




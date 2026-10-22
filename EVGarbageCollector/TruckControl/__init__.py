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


        self.Recharge_stations = self.parameters["recharge_stations"]
        self.Parking_lots = self.parameters["parkings"]
        self.Bin_lots = self.parameters["bins"]


        self.NRecharge_stations = len(self.Recharge_stations)
        self.NParking_lots = len(self.Parking_lots)
        self.NBin_lots = len(self.Bin_lots)

        # Action vector index boundaries
        self.recharge_limits = (0, self.NRecharge_stations)

        self.parking_limits = (
            self.recharge_limits[1],
            self.recharge_limits[1] + self.NParking_lots
        )

        self.bin_limits = (
            self.parking_limits[1],
            self.parking_limits[1] + self.NBin_lots
        )

        print("========== ACTION VECTOR BOUNDARIES ==========")
        print(f"Recharge stations: {self.recharge_limits[0]} to {self.recharge_limits[1] - 1} | Count: {self.NRecharge_stations}")
        print(f"Parking lots:      {self.parking_limits[0]} to {self.parking_limits[1] - 1} | Count: {self.NParking_lots}")
        print(f"Bins:              {self.bin_limits[0]} to {self.bin_limits[1] - 1} | Count: {self.NBin_lots}")
        print(f"Total number of positions: {self.bin_limits[1]}")
        print("==============================================")


        places = self.Recharge_stations + self.Parking_lots + self.Bin_lots
        actions = self.parameters["actions"]

        self.vector_size = places.__len__() + actions.__len__()

        action = []
        

        for i in range(self.vector_size):
            action.append(0)
        

        if soc < 0.55:
            action = [0,0,1]

        elif dist_to_final < 100:
            if edge_finaldest == edge_id and "stopped" in status:
                action = [0,1,0]
            else:
                action = [0,1,1]

        return action


# 1. Criar uma observação de teste
# Observation vector
obs = [
    0.40,           # [0] soc
    500,            # [1] dist_to_final
    200,            # [2] dist_to_dest
    "-E70",         # [3] edge_id
    "-E50",         # [4] edge_dest
    "-E30",         # [5] edge_finaldest
    10.0,           # [6] speed
    "driving",      # [7] status

    # Recharge stations distances
    120,            # [8]  Charge_ParkA
    250,            # [9]  Charge_ParkB
    400,            # [10] Charge_ParkC
    180,            # [11] Charge_ParkD
    320,            # [12] Charge_ParkE
    500,            # [13] Charge_ParkF
    650,            # [14] Charge_ParkW
    700,            # [15] Charge_ParkX

    # Parking lots distances
    100,            # [16] ParkAreaA
    150,            # [17] ParkAreaB
    220,            # [18] ParkAreaG
    300,            # [19] ParkAreaH
    350,            # [20] ParkAreaI
    420,            # [21] ParkAreaJ
    180,            # [22] ParkAreaM
    260,            # [23] ParkAreaN
    330,            # [24] ParkAreaO
    390,            # [25] ParkAreaP
    450,            # [26] ParkAreaQ
    520,            # [27] ParkAreaR
    280,            # [28] ParkAreaS
    360,            # [29] ParkAreaT
    480,            # [30] ParkAreaU
    550,            # [31] ParkAreaV

    # Bins distances
    50,             # [32] BIN-A
    130,            # [33] BIN-B
    240,            # [34] BIN-C
    310             # [35] BIN-D
]

print("Observation vector size:", len(obs))
print("Expected size: 36")

# 2. Criar os parâmetros
parameters = {
"actions": ["Contuinue", "New Route", "Return to Dest", "Stop", "back normal speed",
 "bin collection", "recharge", "park"],
    "recharge_stations_dict": {
        "Charge_ParkA": {
            "edge": "E69",
            "lane": "E69_0"

        },
        "Charge_ParkB": {
            "edge": "-E70",
            "lane": "-E70_0"

        },
        "Charge_ParkC": {
            "edge": "-E133",
            "lane": "-E133_0"

        },
        "Charge_ParkD": {
            "edge": "-E131",
            "lane": "-E131_0"

        },
        "Charge_ParkE": {
            "edge": "E160",
            "lane": "E160_0"

        },
        "Charge_ParkF": {
            "edge": "-E159",
            "lane": "-E159_0"

        },
        "Charge_ParkW": {
            "edge": "E228",
            "lane": "E228_0"

        },
        "Charge_ParkX": {
            "edge": "-E228",
            "lane": "-E228_0"

        }
    },

    "parkings_dict" : {
        "ParkAreaA" : {
            "edge" : "-E202",
            "lane" : "-E202_0"
        },
        "ParkAreaB" : {
            "edge" : "E202",
            "lane" : "E202_0"
        },

        "ParkAreaG" : {
            "edge" : "E95",
            "lane" : "E95_0"
        },

        "ParkAreaH" : {
            "edge" : "E96",
            "lane" : "E96_0"
        },

        "ParkAreaI" : {
            "edge" : "-E94",
            "lane" : "-E94_0"
        },

        "ParkAreaJ" : {
            "edge" : "E93",
            "lane" : "E93_0"
        },

        "ParkAreaM" : {
            "edge" : "-E206",
            "lane" : "-E206_0"
        },

        "ParkAreaN" : {
            "edge" : "E206",
            "lane" : "E206_0"
        },

        "ParkAreaO" : {
            "edge" : "-E226",
            "lane" : "-E226_0"
        },

        "ParkAreaP" : {
            "edge" : "E226",
            "lane" : "E226_0"
        },

        "ParkAreaQ" : {
            "edge" : "-E204",
            "lane" : "-E204_0"
        },

        "ParkAreaR" : {
            "edge" : "E204",
            "lane" : "E204_0"
        },

        "ParkAreaS" : {
            "edge" : "E224",
            "lane" : "E224_0"
        },

        "ParkAreaT" : {
            "edge" : "-E224",
            "lane" : "-E224_0"
        },

        "ParkAreaU" : {
            "edge" : "-E222",
            "lane" : "-E222_0"
        },

        "ParkAreaV" : {
            "edge" : "E222",
            "lane" : "E222_0"
        }
    },

  "Bins_dict" : {
    "BIN-A" : {
        "edge" : "-E16",
        "lane" : "-E16_0"
    },

    "BIN-B" : {
        "edge" : "-E23",
        "lane" : "-E23_0"
    },

    "BIN-C" : {
        "edge" : "E170",
        "lane" : "E170_0"
    },

    "BIN-D" : {
        "edge" : "-E186",
        "lane" : "-E186_0"
    }
    
  },

  "recharge_stations" : [
    "Charge_ParkA",
    "Charge_ParkB",
    "Charge_ParkC",
    "Charge_ParkD",
    "Charge_ParkE",
    "Charge_ParkF",
    "Charge_ParkW",
    "Charge_ParkX"
  ],

    "parkings": [
        "ParkAreaA",
        "ParkAreaB",
        "ParkAreaG",
        "ParkAreaH",
        "ParkAreaI",
        "ParkAreaJ",
        "ParkAreaM",
        "ParkAreaN",
        "ParkAreaO",
        "ParkAreaP",
        "ParkAreaQ",
        "ParkAreaR",
        "ParkAreaS",
        "ParkAreaT",
        "ParkAreaU",
        "ParkAreaV"
    ],

  "bins" : [
    "BIN-A",
    "BIN-B",
    "BIN-C",
    "BIN-D"
  ]

}


# 3. Instanciar a classe
controller = Control(obs, parameters)

# 4. Executar a política de controle
action = controller.get_action()

# 5. Exibir o resultado
print("Observação:", controller.obs)
print("Ação escolhida:", controller.vector_size)




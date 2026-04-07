from environment import SingleEV


import json 



"""Load config at config/config.json"""
with open('data/config.json', 'r') as config_file:
    config = json.load(config_file)

with open('data/single_ev.json', "r", encoding="utf-8") as f:
    vehicle = json.load(f)


def main():
    start = "00:00"  # definir um dia, mes e ano e usar datetime
    env = SingleEV(config, vehicle, start)
    

    while env.done is False:
        action = [0,0,0,0,0,0,0,1]
        state, reward, done, truncated, info = env.step(action)
        pass

if __name__ == "__main__":
    main()
from environment import WarehouseEnv

env = WarehouseEnv()

state = env.reset()

done = False

actions = [
    "move_right",
    "move_right",
    "pick_item",
    "move_down",
    "move_down",
    "move_right",
    "move_right",
    "pick_item"
]

for action in actions:
    state, reward, done, _ = env.step(action)

    print("Action:", action)
    print("State:", state)
    print("Reward:", reward)
    print("Done:", done)
    print("--------------------")

    if done:
        break
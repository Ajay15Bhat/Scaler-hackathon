from environment import WarehouseEnv

env = WarehouseEnv()
state = env.reset()

done = False

actions = [
    # First order: ["A", "B"]
    "move_right", "move_right", "pick_item",   # pick A
    "move_down", "move_down", "move_right", "move_right", "pick_item",  # pick B
    "move_up", "move_up", "move_right", "deliver",  # deliver at D

    # Second order: ["C"]
    "move_left", "move_left", "move_down", "move_down", "move_left", "pick_item",  # pick C
    "move_up", "move_up", "move_right", "move_right", "move_right", "deliver"
]

for action in actions:
    state, reward, done, _ = env.step(action)

    print("Action:", action)
    print("Position:", state["agent_position"])
    print("Current Order:", state["current_order"])
    print("Inventory:", state["inventory"])
    print("Orders Completed:", state["orders_completed"])
    print("Reward:", reward)
    print("Done:", done)
    print("--------------------")

    if done:
        break

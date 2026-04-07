from openai import OpenAI
import os
import requests
import time
from dotenv import load_dotenv

LAST_POSITIONS = []
load_dotenv()

print("FILE IS RUNNING")

hf_token = os.getenv("HF_TOKEN")
api_base_url = os.getenv("API_BASE_URL")

print("DEBUG: HF_TOKEN loaded =", bool(hf_token))
print("DEBUG: API_BASE_URL =", api_base_url)

if not hf_token:
    raise ValueError("HF_TOKEN is missing!")

client = OpenAI(
    base_url=api_base_url,
    api_key=hf_token
)

BASE_URL = "http://localhost:8000"


# ------------------------
# GRID (IMPORTANT 🔥)
# ------------------------
GRID = [
    ["S", ".", "A", ".", "D"],
    [".", "X", ".", ".", "B"],
    [".", ".", ".", ".", "."],
    ["C", ".", "X", ".", "."],
    [".", ".", ".", ".", "."]
]

GRID_SIZE = 5


# ------------------------
# API HELPERS
# ------------------------

def get_state():
    try:
        response = requests.get(f"{BASE_URL}/state")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error getting state:", e)
        return None


def send_action(action: str):
    try:
        response = requests.post(f"{BASE_URL}/step", json={"action": action})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error sending action:", e)
        return {"done": True}


def reset_env():
    requests.post(f"{BASE_URL}/reset")
    print("Environment reset")


# ------------------------
# 🧠 SAFE MOVE FUNCTION
# ------------------------

def is_valid(pos):
    r, c = pos
    return (
        0 <= r < GRID_SIZE and
        0 <= c < GRID_SIZE and
        GRID[r][c] != "X"
    )


def get_next_move(position, target):
    global LAST_POSITIONS

    r, c = position
    tr, tc = target

    moves = []

    # Preferred moves (towards target)
    if r < tr:
        moves.append(("move_down", [r + 1, c]))
    if r > tr:
        moves.append(("move_up", [r - 1, c]))
    if c < tc:
        moves.append(("move_right", [r, c + 1]))
    if c > tc:
        moves.append(("move_left", [r, c - 1]))

    # Add all possible moves (fallback)
    moves += [
        ("move_up", [r - 1, c]),
        ("move_down", [r + 1, c]),
        ("move_left", [r, c - 1]),
        ("move_right", [r, c + 1])
    ]

    # Remove invalid moves
    valid_moves = [(a, p) for a, p in moves if is_valid(p)]

    # 🔥 Avoid going back to last position
    if LAST_POSITIONS:
        last = LAST_POSITIONS[-1]
        valid_moves = [(a, p) for a, p in valid_moves if p != last] or valid_moves

    # 🔥 Choose least visited (anti-loop)
    def score(pos):
        return LAST_POSITIONS.count(pos)

    valid_moves.sort(key=lambda x: score(x[1]))

    chosen_action, new_pos = valid_moves[0]

    # Update memory (keep last 10 positions)
    LAST_POSITIONS.append(position)
    if len(LAST_POSITIONS) > 10:
        LAST_POSITIONS.pop(0)

    return chosen_action


# ------------------------
# 🔥 HYBRID POLICY
# ------------------------

def llm_policy(state: dict) -> str:
    if not state:
        return "get_order"

    position = state.get("agent_position")
    current_order = state.get("current_order")
    inventory = state.get("inventory", [])

    item_locations = {
        "A": [0, 2],
        "B": [1, 4],
        "C": [3, 0]
    }

    drop_zone = [0, 4]

    print("DEBUG:", position, current_order, inventory)

    # 1️⃣ Get order
    if current_order is None:
        return "get_order"

    # 2️⃣ Deliver if ready
    if set(inventory) == set(current_order):
        if position == drop_zone:
            return "complete_order"

        return get_next_move(position, drop_zone)

    # 3️⃣ Pick remaining item
    for item in current_order:
        if item not in inventory:
            target = item_locations[item]

            if position == target:
                return "pick_item"

            return get_next_move(position, target)

    return "move_up"


# ------------------------
# MAIN LOOP
# ------------------------

def run():
    print("Starting inference loop...")

    reset_env()
    done = False
    step_count = 0

    while not done and step_count < 200:
        state_data = get_state()

        if not state_data:
            break

        state = state_data["observation"]

        print(f"\nStep {step_count}")
        print("Position:", state["agent_position"])
        print("Order:", state["current_order"])
        print("Inventory:", state["inventory"])

        action = llm_policy(state)
        print("Action:", action)

        result = send_action(action)

        print("Reward:", result.get("reward"))
        print("Done:", result.get("done"))

        done = result.get("done", False)
        step_count += 1

        time.sleep(0.3)

    if done:
        print("🎉 SUCCESS: Episode completed!")
    else:
        print("⚠️ Max steps reached")


if __name__ == "__main__":
    run()

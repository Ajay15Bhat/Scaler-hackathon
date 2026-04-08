from openai import OpenAI
import os
import requests
import time
from dotenv import load_dotenv
from graders import grade
from collections import deque
import itertools

# ------------------------
# INIT
# ------------------------
load_dotenv()

hf_token = os.getenv("HF_TOKEN")
api_base_url = os.getenv("API_BASE_URL")

if not hf_token:
    raise ValueError("HF_TOKEN missing")

client = OpenAI(base_url=api_base_url, api_key=hf_token)

BASE_URL = "http://localhost:8000"

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
    return requests.get(f"{BASE_URL}/state").json()

def send_action(action):
    return requests.post(f"{BASE_URL}/step", json={"action": action}).json()

def reset_env(task_name=None):
    if task_name:
        requests.post(f"{BASE_URL}/reset", json={"task_name": task_name})
    else:
        requests.post(f"{BASE_URL}/reset")

# ------------------------
# BFS PATHFINDING
# ------------------------

def bfs_path(start, target):
    directions = [
        ("move_up", (-1, 0)),
        ("move_down", (1, 0)),
        ("move_left", (0, -1)),
        ("move_right", (0, 1)),
    ]

    queue = deque()
    queue.append((start, []))
    visited = set()
    visited.add(tuple(start))

    while queue:
        (r, c), path = queue.popleft()

        if [r, c] == target:
            return path

        for action, (dr, dc) in directions:
            nr, nc = r + dr, c + dc

            if (
                0 <= nr < GRID_SIZE and
                0 <= nc < GRID_SIZE and
                GRID[nr][nc] != "X" and
                (nr, nc) not in visited
            ):
                visited.add((nr, nc))
                queue.append(([nr, nc], path + [action]))

    return []

# ------------------------
# DISTANCE HELPER
# ------------------------

def get_distance(a, b):
    return len(bfs_path(a, b))

# ------------------------
# OPTIMAL ITEM ORDER 🔥
# ------------------------

def get_best_item_order(position, items, item_locations, drop):
    best_order = None
    best_cost = float("inf")

    for perm in itertools.permutations(items):
        cost = 0
        current = position

        # go through items
        for item in perm:
            loc = item_locations[item]
            cost += get_distance(current, loc)
            current = loc

        # then go to drop
        cost += get_distance(current, drop)

        if cost < best_cost:
            best_cost = cost
            best_order = perm

    return list(best_order)

# ------------------------
# POLICY
# ------------------------

CURRENT_PLAN = []

def policy(state):
    global CURRENT_PLAN

    if state["inventory"] == []:
       CURRENT_PLAN = []
    position = state["agent_position"]
    order = state["current_order"]
    inventory = state["inventory"]

    item_locations = {
        "A": [0, 2],
        "B": [1, 4],
        "C": [3, 0]
    }

    drop = [0, 4]

    # ------------------------
    # GET ORDER
    # ------------------------
    if order is None:
        return "get_order"

    # ------------------------
    # PLAN LOGIC 🔥
    # ------------------------
    if not CURRENT_PLAN:
        remaining_items = [item for item in order if item not in inventory]

        if remaining_items:
            best_order = get_best_item_order(position, remaining_items, item_locations, drop)

            path = []
            current = position

            for item in best_order:
                item_pos = item_locations[item]
                path += bfs_path(current, item_pos)
                path.append("pick_item")
                current = item_pos

            # after all items → go to drop
            path += bfs_path(current, drop)
            path.append("complete_order")

            CURRENT_PLAN = path

    # ------------------------
    # EXECUTE PLAN
    # ------------------------
    if CURRENT_PLAN:
        action = CURRENT_PLAN.pop(0)
        return action

    return "move_up"

# ------------------------
# RUN TASK
# ------------------------

def run_task(task_name):
    global CURRENT_PLAN

    print(f"\nRunning {task_name.upper()}")

    reset_env(task_name)
    CURRENT_PLAN = []

    done = False
    steps = 0
    final_state = None

    while not done and steps < 200:
        state = get_state()["observation"]
        final_state = state

        print(f"Step {steps} | Pos:{state['agent_position']} | "
              f"Order:{state['current_order']} | Inv:{state['inventory']}")

        action = policy(state)
        print("Action:", action)

        result = send_action(action)

        print("Reward:", result.get("reward"), "| Done:", result.get("done"))

        done = result.get("done", False)
        steps += 1
        time.sleep(0.2)

    return final_state

# ------------------------
# MAIN RUN
# ------------------------

def run():
    print("\n🔥 FULL EVALUATION STARTED 🔥")

    scores = {}

    for task in ["easy", "medium", "hard"]:
        state = run_task(task)
        score = grade(state)
        scores[task] = score
        print(f"{task.upper()} SCORE:", score)

    print("\n🏁 FINAL RESULTS")
    for k, v in scores.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    run()

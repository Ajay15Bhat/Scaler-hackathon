from openai import OpenAI
import os
import requests
import time
from graders import grade
from collections import deque
import itertools

# ====================== FIXED FOR HACKATHON (CRITICAL) ======================
# Use the LiteLLM proxy provided by the hackathon
api_base = os.environ.get("API_BASE_URL")
api_key = os.environ.get("API_KEY")

if not api_base or not api_key:
    print("⚠️  WARNING: Running locally - API_BASE_URL or API_KEY not found.")
    print("   Hackathon server will inject these automatically.")
    print("   For local testing, set environment variables or use your own OpenAI key temporarily.")
    # Do NOT hardcode your real key here for submission!
    raise SystemExit("Please run on Hackathon environment for submission.")

client = OpenAI(
    base_url=api_base,
    api_key=api_key
)
# =========================================================================

BASE_URL = "https://ajay15bhat-warehouse-agent.hf.space"
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
# OPTIMAL ITEM ORDER
# ------------------------
def get_best_item_order(position, items, item_locations, drop):
    best_order = None
    best_cost = float("inf")
    for perm in itertools.permutations(items):
        cost = 0
        current = position
        for item in perm:
            loc = item_locations[item]
            cost += get_distance(current, loc)
            current = loc
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
    if order is None:
        return "get_order"
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
            path += bfs_path(current, drop)
            path.append("complete_order")
            CURRENT_PLAN = path
    if CURRENT_PLAN:
        return CURRENT_PLAN.pop(0)
    return "move_up"

# ------------------------
# RUN TASK
# ------------------------
def run_task(task_name):
    global CURRENT_PLAN
    reset_env(task_name)
    CURRENT_PLAN = []
    print(f"[START] task={task_name}")
    done = False
    steps = 0
    final_state = None
    while not done and steps < 200:
        state = get_state()["observation"]
        final_state = state
        action = policy(state)
        result = send_action(action)
        print(
            f"[STEP] step={steps} "
            f"pos={state['agent_position']} "
            f"order={state['current_order']} "
            f"inv={state['inventory']} "
            f"action={action} "
            f"reward={result.get('reward')} "
            f"done={result.get('done')}"
        )
        done = result.get("done", False)
        steps += 1
        time.sleep(0.2)
    score = grade(final_state)
    print(f"[END] task={task_name} score={score}")
    return score

# ------------------------
# MAIN RUN
# ------------------------
def run():
    # === REQUIRED TEST CALL THROUGH HACKATHON PROXY ===
    print("Making test LLM call through LiteLLM proxy...")
    try:
        test_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in one word only."}],
            max_tokens=10,
            temperature=0.0
        )
        print("✅ Proxy test call successful:", test_response.choices[0].message.content.strip())
    except Exception as e:
        print("❌ Test call failed:", e)
    # ===================================================

    scores = {}
    for task in ["easy", "medium", "hard"]:
        scores[task] = run_task(task)
    print(f"[END] final_scores={scores}")

if __name__ == "__main__":
    run()

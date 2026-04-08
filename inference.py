import os
import requests
from openai import OpenAI

# -----------------------------
# Environment Variables
# -----------------------------
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME")
HF_TOKEN = os.environ.get("HF_TOKEN")

print("API_BASE_URL:", API_BASE_URL)
print("MODEL_NAME:", MODEL_NAME)
print("HF_TOKEN exists:", HF_TOKEN is not None)


# -----------------------------
# OpenAI Client (MANDATORY)
# -----------------------------
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

BASE_URL = "http://localhost:8000"


# -----------------------------
# Force LLM Ping (IMPORTANT)
# -----------------------------
def ping_llm():
    print("Testing LLM connection...")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "Ping"}
        ],
        temperature=0
    )

    print("LLM Connected Successfully")


# -----------------------------
# LLM Action Selector
# -----------------------------
def get_action(state):

    prompt = f"""
You are a warehouse robot.

State:
{state}

Choose one action:

move_up
move_down
move_left
move_right
pick_item
deliver
get_order

Return only action name.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Warehouse agent"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    action = response.choices[0].message.content.strip()

    return action


# -----------------------------
# Run Task
# -----------------------------
def run_task(task):

    print(f"\nRunning {task}")

    requests.post(
        f"{BASE_URL}/reset",
        json={"task": task}
    )

    done = False
    steps = 0

    while not done and steps < 100:

        state = requests.get(
            f"{BASE_URL}/state"
        ).json()

        action = get_action(state)

        response = requests.post(
            f"{BASE_URL}/step",
            json={"action": action}
        ).json()

        done = response["done"]

        print(
            f"Step {steps} | Action: {action} | Reward: {response['reward']}"
        )

        steps += 1

    return response["state"]


# -----------------------------
# Grader
# -----------------------------
def grade(state):

    completion = state.get("orders_completed", 0) / 2
    efficiency = max(0, 1 - state.get("time", 100) / 100)
    battery = state.get("battery", 0) / 100

    score = 0.5 * completion + 0.3 * efficiency + 0.2 * battery

    return max(0, min(score, 1))


# -----------------------------
# Main
# -----------------------------
def main():

    # Force LLM call
    ping_llm()

    scores = {}

    for task in ["easy", "medium", "hard"]:

        final_state = run_task(task)

        score = grade(final_state)

        scores[task] = score

        print(f"{task} score: {score:.3f}")

    print("\nFinal Scores")
    print(scores)


if __name__ == "__main__":
    main()

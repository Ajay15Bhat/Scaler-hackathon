import os
import requests
from openai import OpenAI


# -----------------------------
# Required Environment Variables
# -----------------------------
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ["MODEL_NAME"]


# -----------------------------
# OpenAI Client (Required Fix)
# -----------------------------
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)


BASE_URL = "http://localhost:8000"


# -----------------------------
# LLM Action Function
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

    return response.choices[0].message.content.strip()


# -----------------------------
# Run Task
# -----------------------------
def run_task(task):

    requests.post(
        f"{BASE_URL}/reset",
        json={"task": task}
    )

    done = False

    while not done:

        state = requests.get(
            f"{BASE_URL}/state"
        ).json()

        action = get_action(state)

        response = requests.post(
            f"{BASE_URL}/step",
            json={"action": action}
        ).json()

        done = response["done"]

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

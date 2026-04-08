from fastapi import FastAPI
from pydantic import BaseModel
from environment import WarehouseEnv
from tasks import TASKS

app = FastAPI()

env = WarehouseEnv()

class Action(BaseModel):
    action: str

@app.post("/reset")
def reset(task: dict = None):
    state = env.reset()

    if task and "task_name" in task:
        task_name = task["task_name"]

        if task_name in TASKS:
            config = TASKS[task_name]()

            # Inject task config into environment
            env._state["orders"] = config["orders"]
            env._state["battery"] = config["battery"]

    return {
        "observation": env.state()
    }

@app.post("/step")
def step(action: Action):
    try:
        state, reward, done, _ = env.step(action.action)
        return {
            "observation": state,
            "reward": reward,
            "done": done,
            "info": {}
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/state")
def get_state():
    return {"observation": env.state()}

@app.get("/health")
def health():
    return {"status": "ok"}

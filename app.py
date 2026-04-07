from fastapi import FastAPI
from pydantic import BaseModel
from environment import WarehouseEnv

app = FastAPI()

env = WarehouseEnv()

class Action(BaseModel):
    action: str

@app.post("/reset")
def reset():
    state = env.reset()
    return {"observation": state}

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

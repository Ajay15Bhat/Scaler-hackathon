from fastapi import FastAPI
from pydantic import BaseModel
from environment import WarehouseEnv

app = FastAPI()

env = WarehouseEnv()

# Input schema
class Action(BaseModel):
    action: str

# Reset endpoint
@app.post("/reset")
def reset():
    state = env.reset()

    return {
        "observation": state
    }
# Step endpoint
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
        return {
            "error": str(e)
        }
# State endpoint
@app.get("/state")
def get_state():
    return {
        "observation": env.state()   # ✅ NO brackets
    }
# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(task: dict = None):
    state = env.reset()
    return {"observation": state}

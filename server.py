from fastapi import FastAPI
from environment import WarehouseEnv

app = FastAPI()
env = WarehouseEnv()


@app.get("/state")
def get_state():
    return {"observation": env.state()}


@app.post("/step")
def step(action: dict):
    obs, reward, done, _ = env.step(action["action"])
    return {"observation": obs, "reward": reward, "done": done}


@app.post("/reset")
def reset():
    return {"observation": env.reset()}

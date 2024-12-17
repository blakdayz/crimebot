import requests
from fastapi import FastAPI

app = FastAPI()

@app.post("/execute/{cmd}")
async def execute(cmd: str):
    response = requests.get("http://command_tools_1:8000/run", params={"cmd": cmd})
    return response.text

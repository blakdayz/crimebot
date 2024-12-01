"""
Hello! Welcome to CrimeBOT by #illmob #mob
The following loads a model from HuggingFace, loads it with a custom system prompt
and allows for chat style interactions via a FastAPI framework.

To use CrimeBOT, you'll need to:
1. Install the necessary packages by running `pip install fastapi`
2. Save the provided code in a Python file, e.g., `main.py`.
3. Run the script using `python main.py`.
4. Open your web browser and go to http://127.0.0.1:8000/ to interact with CrimeBOT.
Feel free to ask CrimeBOT for any questions or seek assistance if needed!
"""

from fastapi import FastAPI
from sympy.simplify.simplify import bottom_up

from crimebot.chatbot import CrimeBot

app = FastAPI()
bot = CrimeBot()


@app.get("/")
async def root():
    return {
        "message": "A strange game. The only winning move is not to play. How about a nice game of Crime? #illmob"
    }


@app.get("/crime/suggest/")
async def say_hello(name: str):
    return bot.s

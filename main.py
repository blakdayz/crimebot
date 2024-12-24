"""
Hello! Welcome to CrimeBOT by #illmob #mob
The following loads a model from HuggingFace, loads it with a custom system prompt
and allows for chat style interactions via a FastAPI framework.

To use CrimeBOT, you'll need to:
1. Install the necessary packages by running `pip install fastapi`
3. Run the script using `python crimebot/chatbot.py`.
4. Open your web browser and go to http://127.0.0.1:8000/ to interact with CrimeBOT.
Feel free to ask CrimeBOT for any questions or seek assistance if needed!
"""

import logging

from crimebot.chatbot import CrimeBot

bot = CrimeBot()
logging.basicConfig(level=logging.INFO)
# suppress warnings


def main():
    bot.generate_with_animation("Hello, how are you?")
    bot.generate_with_animation("I'm doing well, thank you!")
    bot.generate_with_animation

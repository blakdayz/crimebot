import os
from cmath import sin

import gtts.tts
import outetts
from sympy import false
from sympy.simplify.simplify import bottom_up
from torch.cuda import temperature
from gtts import *

from manim import *


class AITalking(Scene):
    def construct(self):
        # Set up the mouth shape
        mouth = VMobject()
        for i in range(-20, 21):
            x = i / 10
            y = sin(x * PI) * 0.5 + 0.5
            mouth.points.append([x, y, 0])

        # Animate the mouth
        for t in np.linspace(0, 8 * PI, 200):
            mouth.shift(LEFT * sin(t))

            self.play(
                Create(mouth),
                run_time=0.1,
            )

            if t == 0:
                self.wait(0.5)  # Delay before starting to "speak"

        self.remove(mouth)


class VoiceProvider:

    def __init__(self, name):
        self.name = name
        self.model_config = outetts.HFModelConfig_v1(
            model_path="OuteAI/OuteTTS-0.2-500M",
            language="en",  # Supported languages: en, zh, ja, ko
        )
        self.interface = None
        self.speaker = None
        self.set_speaker()
        self.output = None
        self.n_ctx = 4096
        self.use_gtts = False

    def swap_to_local_ai(self):
        self.interface = outetts.InterfaceHF(model_version="0.2", cfg=self.model_config)
        self.use_gtts = False

    def swap_to_gtts(self):
        self.use_gtts = True
        self.interface = None

    def set_speaker(self, speaker="male_2"):
        if self.interface is not None:
            self.speaker = self.interface.load_default_speaker(name=speaker)

    def list_speakers(self):
        return self.interface.print_default_speakers()

    def generate(self, text):
        if not self.use_gtts:
            if self.interface is not None:
                self.output = self.interface.generate(
                    text=text,
                    temperature=0.1,
                    repetition_penalty=1.1,
                    max_length=self.n_ctx,
                )
                self.output.play()
        else:
            self.output = gtts.tts.gTTS(text, tld="co.za")
            self.output.save("output.mp3")
            os.system("mpg123 -q output.mp3")

    def save(self):
        self.output.save("output.wav")


if __name__ == "__main__":
    provider = VoiceProvider("CrimeBOT")
    provider.set_speaker("male_1")
    provider.generate(
        "Welcome to CrimeBOT Artificial Intelligence For Adversary Operations "
    )
    provider.swap_to_gtts()
    provider.generate("Using gTTS")

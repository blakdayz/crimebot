import os
from cmath import sin
from manim import *


class AITalking(Scene):

    def construct(self, text, run_time=8):
        # Set up the mouth shape
        mouth = VMobject()
        for i in range(-20, 21):
            x = i / 10
            y = sin(x * PI) * 0.5 + 0.5
            mouth.points.append([x, y, 0])

        # Animate the mouth with text
        for t, char in enumerate(text):
            mouth.shift(LEFT * sin(t * PI / len(text)))
            self.play(
                Create(mouth),
                Write(char, run_time=run_time / len(text)),
                run_time=run_time / len(text),
            )

        self.remove(mouth)


if __name__ == "__main__":
    talk = AITalking()
    talk.construct(text="Hello!")

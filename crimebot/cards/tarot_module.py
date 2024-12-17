import json
import logging
from collections import defaultdict
from typing import Callable


class TarotModule:
    """
    Come play a card game with Crimebot. Pass the LLM Hoop
    """

    def __init__(self, llm_prompt_callable: Callable = None):
        self.tarot_data: defaultdict[list]
        self.llm_prompt_callable = llm_prompt_callable
        try:
            self.tarot_data = self.load_tarot_data()
        except Exception as e:
            logging.error(f"Error in loading data initialization {e}")

    def read_tarot_cards(self, card_names, inverse=False, llm_hook: Callable = None):
        tarot_data = self.load_tarot_data()

        prompt_template = f"Tell me the meaning of {', '.join(card_names)} cards, {'' if not inverse else 'in reverse'}."
        response = llm(prompt_template)[0]

        responses = []
        for card_name in card_names:
            card_meaning = ""
            for token in response.split("\n"):
                if f"{card_name}'s" in token:
                    card_meaning += token.strip() + " "
            responses.append(
                self.find_card_meaning(tarot_data, card_name, card_meaning)
            )
        prompt = f"Now, in sequence determine the overall affect for all the following: {responses} "

        return responses

    def llm(self, system_message):
        """

        :param system_message:
        :return:
        """

    @staticmethod
    def load_tarot_data():
        """
        Loads the tarot data cards
        :return:
        """
        minor_tarot_data = defaultdict(list)
        major_tarot_data = defaultdict(list)
        try:
            with open("data/minor_arcana.json") as f:
                minor_tarot_data = json.load(f)

            with open("data/major_arcana.json") as f:
                major_tarot_data = json.load(f)

            tarot_data_dict = defaultdict(list)
            for card in minor_tarot_data:
                tarot_data_dict[card["name"]].append(
                    (card["positive"], card["negative"])
                )
            for card in major_tarot_data:
                tarot_data_dict[card["name"]].append(
                    (card["positive"], card["negative"])
                )
            return tarot_data_dict
        except Exception as e:
            logging.error(f"Error loading data {e}")

    @staticmethod
    def find_card_meaning(tarot_data, card_name, card_meaning):
        for meaning in card_meaning.split("\n"):
            if any(
                f"{card_name}'s" in tarot_data[card_name][i]
                for i in range(len(tarot_data[card_name]))
            ):
                if "negative" in meaning and not tarot_data[card_name][0].startswith(
                    "Reversed"
                ):
                    return tarot_data[card_name][1].replace("Reversed", "")
                elif "positive" in meaning and tarot_data[card_name][0].startswith(
                    "Reversed"
                ):
                    return (
                        tarot_data[card_name][0]
                        .replace("Reversed", "")
                        .replace("The", "")
                        .capitalize()
                        + " (Inverse)"
                    )
                else:
                    return meaning.strip().replace("Reversed", "")
        return f"Card not found: {card_name}"


if __name__ == "__main__":
    mod = TarotModule()
    mod.find_card_meaning()

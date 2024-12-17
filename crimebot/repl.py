from crimebot.chatbot import CrimeBot

VOICE: bool = False
bot = CrimeBot()
code_snippet: str = ""


def voice_wrap(saythis: str = None):
    if VOICE == True:
        saythis = " ".join(saythis.split())  # remove extra spaces
        print("[VOICE]", saythis)
        bot.tts(saythis)
    else:
        print("[NO VOICE]", saythis)


def main():

    while True:
        print("\nCrimeBot Terminal Interface")
        print("1. Suggest a crime")
        print("2. Provide campaign advice for target")
        print("3. Suggest targets within industry or sector")
        print("4. Write malware")
        print("5. Describe code")
        print("6. Provide infrastructure advice for crime type")
        print("7. Detect and respond to threat")
        print("8. Modify attribution signature")
        print("9. Explain yourself, CrimeBot ")
        print("10. Exploit a vulnerability")
        print("11. Provide technical analysis for target")
        print("12. Suggest crime techniques based on malware type")
        print("13. Provide infrastructure advice for security type")
        print("14. Provide technical analysis for security type")
        print("15. Suggest crime techniques based on malware type and security type")
        print("16. Explain the purpose of a specific piece of malware or code")
        print(
            "17. Discuss how different types of malware can be used to achieve various criminal objectives"
        )
        print(
            "18. Describe possible methods for detecting and responding to cyber threats, including social engineering techniques"
        )
        print(
            "19. Suggest ways to modify the behavior of a specific piece of malware or code without having to delete it or disrupt its functionality"
        )

        choice = input("Enter your choice: ")

        if choice == "1":
            voice_wrap(bot.suggest_crime())
        elif choice == "2":
            target = input("Enter the target for campaign advice: ")
            voice_wrap(bot.provide_campaign_advice(target))
        elif choice == "3":
            sector = input("Enter the industry or sector for targeting suggestions: ")
            voice_wrap(bot.suggest_targets(sector))
        elif choice == "4":
            malware_tasks = input(
                "Enter comma-separated tasks for malware (e.g., ransomware, C2 backdoor): "
            )
            attribution_target = input("Enter the attribution target: ")
            code_snippet = bot.write_malware(
                malware_tasks.split(","), attribution_target
            )

        elif choice == "5":
            code = input("Enter the code to describe: ")
            voice_wrap(bot.describe_code(code))
        elif choice == "6":
            crime_type = input("Enter the crime type for infrastructure advice: ")
            bot.provide_infrastructure_advice(crime_type)
        elif choice == "7":
            threat_description = input(
                "Describe the threat for detection and response advice: "
            )
            bot.detect_and_respond(threat_description)
        elif choice == "8":
            group_name = input(
                "Enter the group name for attribution signature modification: "
            )
            plan = input("Enter the code to modify for dis-attribution: ")
            print(bot.create_attribution_signature(group_name, plan))
        elif choice == "9":
            print(bot.explain_who_crimebot_is())
        elif choice == "0":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()

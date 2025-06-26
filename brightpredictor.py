import random
from collections import Counter
from datetime import datetime

# Training data
bright_actions = [
    {
        "action": "flirts with",
        "object": "SCP-682",
        "reason": "to prove that even hatred deserves love"
    },
    {
        "action": "transforms into",
        "object": "toast",
        "reason": "because he wanted to be crispy and immortal at the same time"
    },
    {
        "action": "organizes a cult for",
        "object": "SCP-999",
        "reason": "because happiness is the only true religion"
    },
    {
        "action": "shouts 'FOR SCIENCE!' every time he opens",
        "object": "the door",
        "reason": "because silence scares him"
    },
    {
        "action": "places SCP-963 under",
        "object": "the coffee machine",
        "reason": "because he wanted to reincarnate as coffee"
    },
    {
        "action": "calls",
        "object": "SCP-173 'the killer teddy bear' and lights candles for it",
        "reason": "because 'no one looks at his insides'"
    }
]

# Counting frequencies
action_counter = Counter(action["action"] for action in bright_actions)
object_counter = Counter(action["object"] for action in bright_actions)

# Weighted random choice
def choose_from_weight(counter):
    total = sum(counter.values())
    r = random.uniform(0, total)
    s = 0
    for elem, weight in counter.items():
        s += weight
        if s >= r:
            return elem

# Generate a single action
def generate_action():
    action = choose_from_weight(action_counter)
    object = choose_from_weight(object_counter)
    reason = random.choice([act["reason"] for act in bright_actions])
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return f"[{hours:02d}:{minutes:02d}] Dr. Bright {action} {object}, {reason}."

# Generate and save to file
def generate_and_save(filename="LOCATION OF .TXT FILE TO SAVE IT TO"):
    today = datetime.now().strftime("%m/%d/%Y")
    with open(filename, "a", encoding="utf-8") as f:
        header = f"\n{today}:\n"
        print(header.strip())
        f.write(header)
        akcja = generate_action()
        line = f"{akcja}"
        print(line)
        f.write(line + "\n")

# Run script
if __name__ == "__main__":
    generate_and_save



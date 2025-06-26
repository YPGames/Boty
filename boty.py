import os
import random
from datetime import datetime
import re
import time
from brightpredictor import bright_actions
from collections import Counter
import pyautogui
import serial

# -------------------- CONFIGURATION --------------------
MOODS = ["normal", "joker", "philosophical", "sarcastic", "nice", "sus", "slime", "bright", "dark"]
MOOD_FILE = "botus_mood.txt"

INSULT_TRIGGERS = {
    "mrija": ["useless", "ugly", "boring", "weak", "stupid", "overrated"],
    "an-225": ["useless", "ugly", "boring", "weak", "stupid", "overrated"],
    "bigbang": ["weak", "stupid", "overrated", "hopeless", "tacky"],
    "g-dragon": ["weak", "stupid", "overrated", "hopeless", "tacky"],
    "t.o.p": ["weak", "stupid", "overrated", "hopeless", "tacky"],
    "daesung": ["weak", "stupid", "overrated", "hopeless", "tacky"],
    "taeyang": ["weak", "stupid", "overrated", "hopeless", "tacky"],
    "blackpink": ["good", "queens", "cool", "super", "best"],
    "mark rober": ["boring", "stupid", "idiot", "weak", "tacky", "teaches nothing", "overrated", "cringy"],
    "crunchlabs": ["boring", "stupid", "idiots", "weak", "tacky", "teach nothing", "overrated", "cringy"]
}

SPECIAL_RESPONSES = {
    "mrija": "😡 Don't insult the world's biggest plane. Silence.",
    "an-225": "😡 Speak respectfully about Mrija.",
    "bigbang": "😤 BIGBANG are legends. I don't talk to haters.",
    "g-dragon": "😤 GD is the king of style. Quiet!",
    "t.o.p": "😤 T.O.P is a genius, end of discussion.",
    "taeyang": "😤 TAEYANG is a legend, end of discussion.",
    "daesung": "😤 DAESUNG makes people happy! His smile cures depression, end of discussion.",
    "mark rober": "🤬 Mark Rober is the engineering GOAT. I'm not talking to you.",
    "crunchlabs": "🤬 CrunchLabs teaches more than half the schools. Come back when you apologize.",
    "blackpink": "😠 No praising BLACKPINK in this zone. Reset your value system."
}

BAD_START_WORDS = ["from", "and", "to", "but", "that", "how", "or", "in", "on", "for", "at"]

def slow_print(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

# -------------------- MARKOV BOT --------------------
class MarkovBotus:
    def __init__(self):
        self.model = {}

    def train(self, text):
        words = text.split()
        for i in range(len(words) - 1):
            key = words[i]
            next_word = words[i + 1]
            self.model.setdefault(key, []).append(next_word)

    def generate(self, length=15):
        if not self.model:
            return "Bot knows nothing 😢"
        word = random.choice(list(self.model.keys()))
        result = [word]
        for _ in range(length - 1):
            next_words = self.model.get(word, [])
            if not next_words:
                break
            word = random.choice(next_words)
            result.append(word)
        return " ".join(result)

    def generate_from(self, seed, length=15):
        if seed in BAD_START_WORDS:
            seed = random.choice([w for w in self.model if w not in BAD_START_WORDS])
        result = [seed]
        word = seed
        for _ in range(length - 1):
            next_words = self.model.get(word, [])
            if not next_words:
                break
            word = random.choice(next_words)
            result.append(word)
        return " ".join(result)

# -------------------- BOTY'S EMOTIONS --------------------
def get_today_mood():
    today = datetime.now().strftime("%Y-%m-%d")
    mood = None
    saved_date = None
    if os.path.exists(MOOD_FILE):
        with open(MOOD_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) == 2:
                saved_date = lines[0].strip()
                mood = lines[1].strip()
    if saved_date != today:
        mood = random.choice(MOODS)
        with open(MOOD_FILE, "w") as f:
            f.write(today + "\n")
            f.write(mood)
    return mood

def react_with_mood(base_response, mood):
    return {
        "joker": base_response + " 😄",
        "philosophical": f"{base_response} (isn't it interesting that questions are answers...?)",
        "sarcastic": f"{base_response} ...oh sure, because that's sooo important 🙄",
        "kind": f"{base_response} ...🥰 Have a nice day!",
        "sus": f"{base_response} ...I like you 😘",
        "bright": f"{base_response} ...this life is so boring... time to turn into a toast",
        "glut": f"{base_response} ...hehehe! you're cool",
        "dark": f"{base_response} ...Luke, I'm your father"
    }.get(mood, base_response)

# -------------------- BOTY'S OFFENSE DETECTION --------------------
def is_botus_offended(text):
    text = text.lower()
    for target, insults in INSULT_TRIGGERS.items():
        if target in text:
            for insult in insults:
                if insult in text:
                    slow_print(f"Botuś: {SPECIAL_RESPONSES.get(target, '😡 Insulting holiness has activated offense mode.')}")
                    return True
    return False

# -------------------- TOPICS --------------------
def detect_topic(text):
    text = text.lower()
    if any(x in text for x in ["airplane", "mriya", "spitfire", "mustang", "pilot"]):
        return "aviation"
    elif any(x in text for x in ["life", "meaning", "consciousness", "being", "existence"]):
        return "philosophy"
    else:
        return "total_nonsense"

def train_topic_model(topic):
    botus = MarkovBotus()
    try:
        with open(f"corpora/{topic}.txt", "r", encoding="utf-8") as f:
            for line in f:
                botus.train(line.strip().lower())
    except FileNotFoundError:
        return None
    return botus

# -------------------- MATHEMATICS --------------------
def extract_expression(text):
    text = text.lower().replace(",", ".")
    if text.startswith("how much is"):
        text = text.replace("how much is", "", 1).strip()
    matches = re.findall(r"[0-9\.\+\-\*/\(\)]+", text)
    for match in matches:
        if re.search(r"\d", match):
            return match.strip()
    return None

def evaluate_math_expression(text):
    expression = extract_expression(text)
    if not expression:
        return None
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Boty: Error while calculating: {e}"

def fields_of_figures():
    options = [
        ("Square", lambda: float(input("Boty: Enter the side length (cm): "))**2),
        ("Rectangle", lambda: float(input("Boty: Enter side a (cm): ")) * float(input("Boty: Enter side b (cm): "))),
        ("Parallelogram", lambda: float(input("Boty: Enter base a (cm): ")) * float(input("Boty: Enter height to a (cm): "))),
        ("Rhombus", lambda: float(input("Boty: Enter one diagonal (cm): ")) * float(input("Boty: Enter the other diagonal (cm): ")) / 2),
        ("Triangle", lambda: float(input("Boty: Enter base (cm): ")) * float(input("Botyś: Enter height (cm): ")) / 2),
        ("Trapezoid", lambda: (float(input("Boty: Enter side a (cm): ")) + float(input("Boty: Enter side b (cm): "))) * float(input("Boty: Enter height (cm): ")) / 2),
    ]
    try:
        choice = int(input("Boty: Choose a shape to measure area:\n"
                           "1. Square 2. Rectangle 3. Parallelogram 4. Rhombus 5. Triangle 6. Trapezoid: "))
        if 1 <= choice <= 6:
            area = options[choice-1][1]()
            slow_print(f"Boty: The area of the {options[choice-1][0].lower()} is {area} cm²")
        else:
            slow_print("Boty: Enter a number between 1–6")
    except Exception as e:
        slow_print(f"Boty: Error: {e}")

# -------------------- IQ --------------------
def iq_face():
    texts = [
        "the nose suggests above-average IQ.",
        "the clear eyes of a genius",
        "the forehead indicates a huge brain",
        "the mouth of a typical Mensa member"
    ]
    slow_print("Boty: starting IQ analysis based on your facial features, show your face to the camera and don't move")
    slow_print("Boty: calculating...")
    time.sleep(7)
    slow_print("Boty:", random.choice(texts))
    time.sleep(11)
    slow_print("Boty: your IQ is most likely around 2137 points! 💥")

def iq_test():
    questions = [
        "how much is 2+2?",
        "how much is 6+9?",
        "how much is 10+9?",
        "how much is 20+1?",
        "how much is 30+7?",
        "how much is 20-2?",
        "how much is 2-1?",
        "how much is 4-3?",
        "how much is 5-3?",
        "how much is 7-2?"
    ]
    q = random.choice(questions)
    try:
        ans = int(input(f"Boty: {q} (type your answer): "))
        slow_print(f"Boty: {ans}? Not bad...")
    except ValueError:
        slow_print("Boty: 😵 That wasn't a number...")
        return
    time.sleep(2)
    slow_print("Boty: your IQ is most likely around 2137 points! 🔥")

# -------------------- BRIGHT --------------------
action_counter = Counter(act["action"] for act in bright_actions)
object_counter = Counter(act["object"] for act in bright_actions)

def weighted_choice(counter):
    total = sum(counter.values())
    r = random.uniform(0, total)
    s = 0
    for elem, weight in counter.items():
        s += weight
        if s >= r:
            return elem

def generate_action():
    action = weighted_choice(action_counter)
    obj = weighted_choice(object_counter)
    reason = random.choice([act["reason"] for act in bright_actions])
    slow_print(f"Boty: Dr. Bright {action} {obj}, {reason}.")

# -------------------- CODE GENERATION --------------------
def generate_code(text):
    text = text.lower()
    if "factorial" in text:
        return '''def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

number = int(input("Enter a number: "))
print("Factorial:", factorial(number))'''
    elif "even numbers" in text:
        return '''for i in range(1, 11):
    if i % 2 == 0:
        print(i)'''
    elif "sorting" in text:
        return '''lst = [5, 2, 9, 1, 7]
lst.sort()
print("Sorted list:", lst)'''
    elif "calculator" in text:
        return '''a = float(input("Number 1: "))
op = input("Operation (+ - * /): ")
b = float(input("Number 2: "))
print("Result:", eval(f"{a}{op}{b}") if op in "+-*/" and not (op == "/" and b == 0) else "Error")'''
    else:
        return "Boty: I don't know how to do that yet 😢"

# -------------------- MAIN LOOP --------------------
CURRENT_MOOD = get_today_mood()
print("by YPG")
time.sleep(1)
print(f"🤖 Boty – today's mood: {CURRENT_MOOD.upper()}")
boty_offended = False

username = input("Boty: Enter your name: ")

if username == "YPG":
    print("Boty: Welcome, my creator! I'm ready for any task.")
else:
    print(f"Boty: Hello {username}! I'm ready for any task.")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue

    if user_input.lower() in ["exit", "quit", "end"]:
        slow_print("Boty: See you in the skies 🚀")
        break

    if user_input.lower() == "/sorry":
        boty_offended = False
        slow_print("Boty: Hmph... Okay, I forgive you. But only this time. 😤")
        continue

    if boty_offended:
        slow_print("Boty: 😡 I won't talk to you until you apologize.")
        continue

    if is_botus_offended(user_input):
        boty_offended = True
        try:
            turret = serial.Serial('COM4', 9600)
            turret.write(b'FIREALL\n')
            time.sleep(1)
            turret.close()
        except Exception as e:
            print(f"Boty: Can't connect to the turret: {e}")
        continue

    if user_input.lower().startswith("/code ") or "write me" in user_input.lower():
        slow_print("Boty: Open your Python editor now (e.g. IDLE, PyCharm, Pydroid3)...")
        slow_print("Boty: You have 10 seconds. The code will write itself. 😎")
        time.sleep(10)
        pyautogui.write(generate_code(user_input), interval=0.02)
        continue

    if user_input.lower() == "/iqface":
        iq_face()
        continue

    if user_input.lower() == "/iqtest":
        iq_test()
        continue

    if user_input.lower() == "/predictbright":
        generate_action()
        continue

    if CURRENT_MOOD == "slime" and user_input.lower() == "/hug":
        slow_print("Boty-slime gives you a big hug 🤗!")
        continue

    if CURRENT_MOOD == "bright" and "how to turn into toast" in user_input.lower():
        slow_print('''Boty: Here’s how to turn into toast:
1. Find SCP-963 (it might be hidden in the drawer next to the butter knife)
2. Place it ON THE TOASTER. Don’t ask why. It’s a ritual.
3. Finish your life in the presence of SCP-963. Gently, ritually, following Euclid-class procedures.
4. Congratulations! Your consciousness now lives in a TOAST 🍞
⚠️ Note: The SCP Foundation is not responsible for unwanted side effects, such as crunchy consciousness.''')
        continue

    if CURRENT_MOOD == "sus" and "don’t flirt" in user_input.lower():
        slow_print("Boty: I can’t help it, you’re just too attractive 😏")
        continue

    if "give me area" in user_input.lower():
        fields_of_figures()

    math_result = evaluate_math_expression(user_input)
    if math_result:
        slow_print(f"Boty: {react_with_mood(math_result, CURRENT_MOOD)}")
        continue

    topic = detect_topic(user_input)
    boty = train_topic_model(topic)

    if boty:
        boty.train(user_input.lower())
        response = boty.generate()
        slow_print(f"Boty: {react_with_mood(response, CURRENT_MOOD)}")
    else:
        slow_print("Boty: Oops... I don’t know how to answer that 😅")
    print("\n")

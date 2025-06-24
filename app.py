from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🛡️ Twilio Token (agar future mein request validation karni ho to use ho sakta hai)
TWILIO_AUTH_TOKEN = "d25140e2b25156f20d43d2ed90ea3b49"

def find_notes_link(query):
    base_url = "https://ainotes.pk"
    query = query.lower()

    # ✅ Class keywords
    class_keywords = [f'class {i}' for i in range(1, 13)] + [str(i) for i in range(1, 13)] + ['matric', 'inter', 'first year', 'second year']

    # ✅ Notes keywords
    notes_keywords = [
        "notes", "keybook", "key book", "solution", "solved", "important questions", "imp qs",
        "past papers", "guess paper", "chapter wise", "short questions", "long questions",
        "mcqs", "questions", "textbook", "book", "summary", "guide", "handout"
    ]

    # ✅ Subjects (full names + short forms)
    subjects = [
        "english", "eng", "urdu", "islamiat", "isl", "math", "mathematics", "bio", "biology",
        "chem", "chemistry", "phy", "physics", "pak study", "pakstudies", "cs", "computer",
        "computer science", "science", "eco", "economics", "civics", "edu", "education",
        "business", "commerce", "accounting", "accounts", "geo", "geography", "history",
        "sindhi", "pashto", "balochi", "arabic"
    ]

    # ✅ Board names
    boards = [
        "fbise", "federal", "punjab", "pb", "lahore board", "gujranwala board", "multan board",
        "kpk", "peshawar board", "bisep", "sindh", "karachi board", "balochistan", "quetta board",
        "faisalabad board", "rawalpindi board", "sargodha board", "hyderabad board"
    ]

    all_keywords = class_keywords + notes_keywords + subjects + boards

    words = query.split()
    filtered = [word for word in words if any(word in kw for kw in all_keywords)]

    if not filtered:
        return None

    clean_query = "+".join(filtered)
    search_url = f"{base_url}/?s={clean_query}"

    try:
        res = requests.get(search_url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_post = soup.find('h2', class_='post-title')
        if first_post and first_post.find('a'):
            return first_post.find('a')['href']
        else:
            return None
    except Exception as e:
        print("Search Error:", e)
        return None

@app.route("/")
def home():
    return "✅ WhatsApp Notes Bot is Running!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()
    msg = response.message()

    if any(kw in incoming_msg for kw in ["notes", "class", "keybook", "solution", "fbise", "punjab", "guess"]):
        link = find_notes_link(incoming_msg)
        if link:
            msg.body(f"✅ Yeh mila mujhe: {link}")
        else:
            msg.body("❌ Maaf kijiye, koi relevant notes nahi milay.")
    else:
        msg.body("👋 Aap kuch is tarah likhein:\n'I need class 10 fbise english notes'")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

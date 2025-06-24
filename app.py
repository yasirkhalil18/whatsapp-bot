from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def find_notes_link(query):
    base_url = "https://ainotes.pk"
    query = query.lower()

    # ✅ Filtered Class List (Only 9 to 12)
    class_keywords = {
        "9", "10", "11", "12",
        "class 9", "class 10", "class 11", "class 12",
        "ninth", "tenth", "eleventh", "twelfth",
        "first year", "second year", "matric", "inter"
    }

    # ✅ Subject + Notes Keywords
    notes_keywords = {
        "notes", "keybook", "key book", "solution", "solved", "past papers", "important questions",
        "short questions", "long questions", "chapter wise", "summary", "guide", "book",
        "textbook", "guess", "handout", "mcqs", "questions", "review"
    }

    subjects = {
        "english", "eng", "urdu", "islamiat", "isl", "math", "mathematics", "bio", "biology",
        "chem", "chemistry", "phy", "physics", "pak study", "pakstudies", "cs", "computer",
        "science", "eco", "economics", "civics", "edu", "education", "business", "commerce",
        "accounting", "accounts", "geo", "geography", "history", "sindhi", "arabic", "pashto", "balochi"
    }

    boards = {
        "fbise", "federal", "punjab", "pb", "lahore", "kpk", "peshawar", "karachi", "sindh",
        "balochistan", "quetta", "rawalpindi", "multan", "sargodha", "bisep", "gujranwala"
    }

    all_keywords = class_keywords | notes_keywords | subjects | boards
    words = query.split()
    filtered = [word for word in words if any(word in kw for kw in all_keywords)]

    if not filtered:
        return None

    search_query = "+".join(filtered)
    search_url = f"{base_url}/?s={search_query}"

    try:
        res = requests.get(search_url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Try different patterns for links
        link_tag = (
            soup.select_one("h2.post-title a") or
            soup.select_one(".post-title a") or
            soup.select_one(".entry-title a") or
            soup.find("a", href=True)
        )

        if link_tag:
            title = link_tag.text.strip()
            link = link_tag['href']
            return title, link
        else:
            return None, None
    except Exception as e:
        print("Error while scraping:", e)
        return None, None

@app.route("/")
def home():
    return "📚 WhatsApp Notes Bot is Running! 🔥"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()
    msg = response.message()

    # ✅ Only trigger search if query contains possible keywords
    trigger_words = ["class", "notes", "need", "keybook", "solution", "fbise", "punjab"]
    if any(kw in incoming_msg for kw in trigger_words):
        title, link = find_notes_link(incoming_msg)
        if link:
            msg.body(f"✅ Here's what I found for you:\n📘 {title}\n🔗 {link}")
        else:
            msg.body("❌ Sorry! I couldn’t find any relevant notes.\nTry writing clearly like: *Class 9 fbise English notes*")
    else:
        msg.body("👋 Send a message like:\n*Class 10 punjab physics notes*\nAnd I’ll find it for you!")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

# .env file se Twilio ka token load karne ke liye
load_dotenv()

app = Flask(__name__)

# Twilio Auth Token lena (future use ya secure request ke liye)
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Ye function ainotes.pk se result dhoondhta hai
def find_notes_link(query):
    base_url = "https://ainotes.pk"
    search_url = f"{base_url}/?s=" + query.replace(" ", "+")
    try:
        res = requests.get(search_url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_post = soup.find('h2', class_='post-title')
        if first_post and first_post.find('a'):
            return first_post.find('a')['href']
        else:
            return None
    except:
        return None

# WhatsApp se jab message aaye to yahan handle hota hai
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()
    msg = response.message()

    if "notes" in incoming_msg:
        link = find_notes_link(incoming_msg)
        if link:
            msg.body(f"✅ Yeh mila mujhe: {link}")
        else:
            msg.body("❌ Maaf kijiye, koi relevant notes nahi milay.")
    else:
        msg.body("👋 Assalamualaikum! Aap kuch is tarah likhein:\n'I need class 2 notes fbise'")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

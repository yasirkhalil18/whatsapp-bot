from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def find_notes_link(query):
    base_url = "https://ainotes.pk"
    search_url = f"{base_url}/?s=" + query.replace(" ", "+")
    try:
        res = requests.get(search_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_post = soup.find('h2', class_='post-title')
        if first_post and first_post.find('a'):
            return first_post.find('a')['href']
        else:
            return None
    except:
        return None

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()
    msg = response.message()

    if "notes" in incoming_msg:
        link = find_notes_link(incoming_msg)
        if link:
            msg.body(f"✅ Here's what I found: {link}")
        else:
            msg.body("❌ Sorry, no relevant notes found.")
    else:
        msg.body("👋 Hi! Send a message like:\n'I need class 2 notes fbise'")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

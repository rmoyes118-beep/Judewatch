import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.davidaustinroses.co.uk/products/jude-the-obscure"
WEBHOOK = os.environ["DISCORD_WEBHOOK"]

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; JudeStockChecker/1.0)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True).lower()

# Look for signs that Jude is actually available to buy.
available = (
    "add to basket" in text
    or "add to bag" in text
    or "buy now" in text
)

# Save the current state so we only alert once when it changes.
state_file = "jude_state.txt"

try:
    with open(state_file, "r") as f:
        previous = f.read().strip()
except FileNotFoundError:
    previous = "unknown"

current = "available" if available else "unavailable"

if current == "available" and previous != "available":
    message = {
        "content": (
            "🚨🌹 **JUDE THE OBSCURE IS BACK!** 🌹🚨\n\n"
            "Jude the Obscure (Ausjo) appears to be available "
            "on the David Austin website!\n\n"
            f"👉 {URL}"
        )
    }

    requests.post(WEBHOOK, json=message, timeout=30)

with open(state_file, "w") as f:
    f.write(current)

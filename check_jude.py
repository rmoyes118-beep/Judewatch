import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.davidaustinroses.co.uk/products/jude-the-obscure"
WEBHOOK = os.environ["DISCORD_WEBHOOK"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Find the product page text.
text = soup.get_text(" ", strip=True).lower()

# Jude is considered available if the page contains a purchase option
# and does NOT describe the bare-root product as out of stock.
has_purchase_option = (
    "add to basket" in text
    or "add to bag" in text
    or "buy now" in text
)

explicitly_out = (
    "out of stock" in text
)

available = has_purchase_option and not explicitly_out

print("Jude availability check")
print("-----------------------")
print(f"Purchase option found: {has_purchase_option}")
print(f"Explicitly out of stock: {explicitly_out}")
print(f"AVAILABLE: {available}")

# GitHub Actions gives us the previous state through a small file.
state_file = "jude_state.txt"

try:
    with open(state_file, "r") as f:
        previous = f.read().strip()
except FileNotFoundError:
    previous = "unknown"

current = "available" if available else "unavailable"

print(f"Previous state: {previous}")
print(f"Current state:  {current}")

# Only alert when Jude changes from unavailable to available.
# TEMPORARY DISCORD TEST
requests.post(
    WEBHOOK,
    json={"content": "🌹🚨 **TEST ALERT — JUDE WATCH IS WORKING!** 🚨🌹"},
    timeout=30
)
if current == "available" and previous != "available":

    message = {
        "content": (
            "🚨🌹 **JUDE THE OBSCURE IS BACK IN STOCK!** 🌹🚨\n\n"
            "**Jude the Obscure (Ausjo)** appears to be available "
            "on the David Austin website.\n\n"
            "🌹 **GO GO GO:**\n"
            f"{URL}"
        )
    }

    result = requests.post(
        WEBHOOK,
        json=message,
        timeout=30
    )

    result.raise_for_status()

    print("🚨 Discord stock alert sent!")

with open(state_file, "w") as f:
    f.write(current)

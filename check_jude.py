import os
import requests
from bs4 import BeautifulSoup

ROSES = [
    {
        "name": "Jude the Obscure",
        "slug": "jude-the-obscure",
        "state_file": "jude_state.txt",
        "display_name": "Jude the Obscure (Ausjo)",
    },
    {
        "name": "Lady Emma Hamilton",
        "slug": "lady-emma-hamilton",
        "state_file": "lady_emma_state.txt",
        "display_name": "Lady Emma Hamilton (Ausbrother)",
    },
]

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

for rose in ROSES:
    url = f"https://www.davidaustinroses.co.uk/products/{rose['slug']}"
    
    print(f"\nChecking {rose['name']} availability")
    print("-" * 45)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    # Available if any purchase button text appears on the page.
    has_purchase_option = (
        "add to basket" in text
        or "add to bag" in text
        or "buy now" in text
    )

    available = has_purchase_option

    print(f"Purchase option found: {has_purchase_option}")
    print(f"AVAILABLE: {available}")

    # GitHub Actions state file per rose
    state_file = rose["state_file"]

    try:
        with open(state_file, "r") as f:
            previous = f.read().strip()
    except FileNotFoundError:
        previous = "unknown"

    current = "available" if available else "unavailable"

    print(f"Previous state: {previous}")
    print(f"Current state:  {current}")

    # Only alert when the status changes from unavailable to available.
    if current == "available" and previous != "available":

        message = {
            "content": (
                f"🚨🌹 **{rose['name'].upper()} IS BACK IN STOCK!** 🌹🚨\n\n"
                f"**{rose['display_name']}** appears to be available "
                "on the David Austin website.\n\n"
                "🌹 **GO GO GO:**\n"
                f"{url}"
            )
        }

        result = requests.post(
            WEBHOOK,
            json=message,
            timeout=30
        )

        result.raise_for_status()

        print(f"🚨 Discord stock alert sent for {rose['name']}!")

    with open(state_file, "w") as f:
        f.write(current)

import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_limitless():
    # Map the exact Limitless query syntax to the clean string your JS tabs expect
    search_targets = [
        {"query": "!artist:sekio", "tab_name": "Sekio"},
        {"query": "!artist:asako_ito", "tab_name": "Asako Ito"},
        {"query": "!artist:ooyama", "tab_name": "Ooyama"},
        {"query": "!artist:ryoma_uratsuka", "tab_name": "Ryoma Uratsuka"},
        {"query": "!artist:yuka_morii", "tab_name": "Yuka Morii"},
        {"query": "!artist:tomokazu_komiya", "tab_name": "Tomokazu Komiya"},
        {"query": 'name:"clefairy"', "tab_name": "Clefairy"},
        {"query": 'name:"dedenne"', "tab_name": "Dedenne"},
        {"query": 'name:"wooper"', "tab_name": "Wooper"},
        {"query": 'name:"tandemaus"', "tab_name": "Tandemaus"},
        {"query": 'name:"maushold"', "tab_name": "Maushold"}
    ]

    scraped_cards = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for target in search_targets:
        query = target["query"]
        tab_name = target["tab_name"]
        print(f"Fetching data for: {tab_name} ({query})")
        
        params = {
            "q": query,
            "unique": "prints",
            "display": "list",
            "sort": "set",
            "lang": "en",
            "show": "all"
        }
        
        response = requests.get("https://limitlesstcg.com/cards", params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch {query} - Status: {response.status_code}")
            continue
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # The site renders cards as <tr> rows inside a table.data-table
        # Each row has a data-hover attribute with the card image URL
        table = soup.find("table", class_="data-table")
        if not table:
            print(f"No results table found for {query}")
            continue
            
        card_rows = table.find_all("tr")[1:]  # Skip the header row
        
        for row in card_rows:
            try:
                # Image URL is in the data-hover attribute on the <tr>
                image_url = row.get("data-hover")
                if not image_url:
                    continue
                
                # Card name is in the 3rd <td> as an <a> tag
                cells = row.find_all("td")
                name_link = cells[2].find("a")
                if name_link is None:
                    continue
                raw_name = name_link.text.strip()
                
                # Set info: span.card-set has the set code as text and full name in data-tooltip
                set_span = row.find("span", class_="card-set")
                if set_span is None:
                    continue
                set_code = set_span.text.strip()
                set_name = str(set_span.get("data-tooltip", set_code))
                
                # Card number from the 2nd <td>
                number_link = cells[1].find("a")
                if number_link is None:
                    continue
                card_number = number_link.text.strip()

                # Full set number with denominator (e.g., "238/193")
                card_number_full = cells[1].text.strip().replace(" ", "")

                card_id = f"{raw_name}-{set_code}-{card_number}".replace(" ", "-").lower()
                
                # Deduplication & Tag Merging Logic
                if card_id in scraped_cards:
                    # If we already have the card, just ensure the current tab_name is in its tags
                    if tab_name not in scraped_cards[card_id]["tags"]:
                        scraped_cards[card_id]["tags"].append(tab_name)
                else:
                    # First time seeing this card, create the full object
                    scraped_cards[card_id] = {
                        "id": card_id,
                        "eyebrowLabel": f"{raw_name.upper()} • {set_name.upper()} • {card_number_full.upper()}",
                        "displayTitle": raw_name,
                        "imageUrl": image_url,
                        "tags": [tab_name, set_code.upper()]
                    }
            except (AttributeError, IndexError):
                continue
                
        # Be polite to their servers
        time.sleep(2)

    # Convert dictionary values to a list and save
    with open('pokemon_db.json', 'w', encoding='utf-8') as f:
        json.dump(list(scraped_cards.values()), f, indent=4, ensure_ascii=False)
        
    print(f"Successfully saved {len(scraped_cards)} unique cards to pokemon_db.json")

if __name__ == "__main__":
    scrape_limitless()
import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_limitless():
    search_targets = [
        {"queries": ["!artist:sekio"], "tab_name": "Sekio"},
        {"queries": ["!artist:asako_ito"], "tab_name": "Asako Ito"},
        {"queries": ["!artist:ooyama"], "tab_name": "Ooyama"},
        {"queries": ["!artist:ryoma_uratsuka"], "tab_name": "Ryoma Uratsuka"},
        {"queries": ["!artist:yuka_morii"], "tab_name": "Yuka Morii"},
        {"queries": ["!artist:tomokazu_komiya"], "tab_name": "Tomokazu Komiya"},
        {"queries": ['name:"clefairy"'], "tab_name": "Clefairy"},
        {"queries": ['name:"dedenne"'], "tab_name": "Dedenne"},
        {"queries": ['name:"wooper"'], "tab_name": "Wooper"},
        {"queries": ['name:"tandemaus"', 'name:"maushold"'], "tab_name": "Tandemaus & Maushold"}
    ]

    database_by_tab = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for target in search_targets:
        tab_name = target["tab_name"]
        queries = target["queries"]
        print(f"Fetching: {tab_name}...")

        tab_cards = []

        # Loop through every query assigned to this tab
        for query in queries:
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
                print(f"  -> Failed query '{query}' ({response.status_code})")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", class_="data-table")
            if not table:
                continue

            for row in table.find_all("tr")[1:]:
                try:
                    image_url = row.get("data-hover")
                    if not image_url:
                        continue

                    cells = row.find_all("td")
                    raw_name = cells[2].find("a").text.strip()

                    set_span = row.find("span", class_="card-set")
                    set_code = set_span.text.strip()
                    set_name = str(set_span.get("data-tooltip", set_code))

                    card_number = cells[1].find("a").text.strip()
                    card_number_full = cells[1].text.strip().replace(" ", "")
                    card_id = f"{raw_name}-{set_code}-{card_number}".replace(" ", "-").lower()

                    # Append directly without checking for duplicates
                    tab_cards.append({
                        "id": card_id,
                        "eyebrowLabel": f"{raw_name.upper()} • {set_name.upper()} • {card_number_full.upper()}",
                        "displayTitle": raw_name,
                        "imageUrl": image_url
                    })
                except (AttributeError, IndexError):
                    continue

            time.sleep(1.5) # Sleep between individual queries

        database_by_tab[tab_name] = tab_cards

    with open('pokemon_db.json', 'w', encoding='utf-8') as f:
        json.dump(database_by_tab, f, indent=2, ensure_ascii=False)

    print("pokemon_db.json successfully generated!")

if __name__ == "__main__":
    scrape_limitless()
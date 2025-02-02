import requests
from bs4 import BeautifulSoup


class CitationGenerator:
    event_name: str

    def __init__(self, event_name: str):
        self.event_name = event_name

    def query(self) -> list[str]:
        response = requests.get(f"https://en.wikipedia.org/w/api.php?action=opensearch&format=json&search={self.event_name}")
        if response.status_code != 200:
            return []
        url = response.json()[1][0]

        params = {
            "action": "parse",
            "page": url,
            "prop": "text",
            "formatversion": "2",
            "format": "json"
        }

        response = requests.get("https://en.wikipedia.org/w/api.php", params=params)
        if response.status_code != 200:
            return []
        data = response.json()
        html = data.get("parse", {}).get("text", "")
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        cites = soup.find_all("cite")
        links = []
        for cite in cites:
            for link in cite.find_all("a", href=True):
                if link["href"].startswith("https://www.jstor.org"):
                    links.append(link["href"])

        return links

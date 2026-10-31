import json
from pathlib import Path


class PlayerProfile:
    def __init__(self, file_name="player_profile.json"):
        self.path = Path(__file__).resolve().parent / file_name
        self.name = ""
        self.load()

    def load(self):
        if not self.path.exists():
            self.name = ""
            return

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.name = data.get("name", "")

        except json.JSONDecodeError:
            self.name = ""

    def save(self):
        data = {
            "name": self.name
        }

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def set_name(self, name):
        name = name.strip().upper()[:10]

        if name == "":
            name = "PLAYER"

        self.name = name
        self.save()
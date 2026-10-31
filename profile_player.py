from save_paths import get_save_path, read_json, write_json
class PlayerProfile:
    def __init__(self, file_name="player_profile.json"):
        self.path = get_save_path(file_name)
        self.name = ""
        self.load()

    def load(self):
        name = read_json(self.path).get("name", "")
        self.name = name.strip().upper()[:10] if isinstance(name, str) else ""

    def save(self):
        return write_json(self.path, {"name": self.name})

    def set_name(self, name):
        name = name.strip().upper()[:10]

        if name == "":
            name = "PLAYER"

        self.name = name
        self.save()
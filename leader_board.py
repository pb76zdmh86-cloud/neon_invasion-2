from save_paths import get_save_path, read_json, write_json
from datetime import date


class Leaderboard:
    def __init__(self, file_name="leaderboard.json"):
        self.path = get_save_path(file_name)
        self.data = {
            "all_time": [],
            "daily": []
        }
        self.load()

    def load(self):
        data = read_json(self.path)
        for key in ("all_time", "daily"):
            records = data.get(key, [])
            self.data[key] = []
            if not isinstance(records, list):
                continue
            for record in records:
                if not isinstance(record, dict):
                    continue
                name, score, day = (record.get(field) for field in ("name", "score", "date"))
                if not isinstance(name, str) or type(score) is not int or score < 0:
                    continue
                if not isinstance(day, str):
                    continue
                try:
                    date.fromisoformat(day)
                except ValueError:
                    continue
                self.data[key].append({"name": name.upper()[:10], "score": score, "date": day})
        self._clean_daily(date.today().isoformat())
        self._sort_and_limit()

    def save(self):
        return write_json(self.path, self.data)

    def add_score(self, name, score):
        today = date.today().isoformat()

        record = {
            "name": name.upper()[:10],
            "score": int(score),
            "date": today
        }

        self.data["all_time"].append(record)
        self.data["daily"].append(record)

        self._clean_daily(today)
        self._sort_and_limit()

        self.save()

    def _clean_daily(self, today):
        self.data["daily"] = [
            record for record in self.data["daily"]
            if record["date"] == today
        ]

    def _sort_and_limit(self):
        self.data["all_time"].sort(
            key=lambda record: record["score"],
            reverse=True
        )

        self.data["daily"].sort(
            key=lambda record: record["score"],
            reverse=True
        )

        self.data["all_time"] = self.data["all_time"][:5]
        self.data["daily"] = self.data["daily"][:5]

    def top_all_time(self, limit=5):
        return self.data["all_time"][:limit]

    def top_daily(self, limit=5):
        today = date.today().isoformat()

        return [
            record for record in self.data["daily"]
            if record["date"] == today
        ][:limit]
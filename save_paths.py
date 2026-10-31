"""Пути и безопасная запись пользовательских сохранений."""
import json
from pathlib import Path

SAVE_DIR = Path.home() / "Library" / "Application Support" / "Neon Invasion"


def get_save_path(file_name):
    """Сохранения хранятся отдельно от проекта, без переноса старых JSON."""
    return SAVE_DIR / file_name


def read_json(path):
    """Возвращает словарь; повреждённый или недоступный файл даёт пустые данные."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path, data):
    """Заменяет файл после полной записи; при ошибке старые данные сохраняются."""
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        temporary.replace(path)
    except OSError as error:
        print(f"Не удалось сохранить {path.name}: {error}")
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return False
    return True

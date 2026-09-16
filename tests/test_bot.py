from aiogram import Dispatcher

from app.config import Settings
from app.content import PROMOTIONS, UPDATES
from app.main import _safe_index, build_dispatcher, help_text, home_text
from app.storage import Storage


def test_three_functions_are_present():
    home = home_text()
    assert "Promotions" in home
    assert "Updates" in home
    assert "Submit Promotion" in home
    assert "3 functions" in home


def test_content_is_complete():
    assert PROMOTIONS and UPDATES
    assert all(item.title and item.body for item in (*PROMOTIONS, *UPDATES))


def test_callback_validation():
    assert _safe_index("promotion:0", "promotion", 3) == 0
    assert _safe_index("promotion:3", "promotion", 3) is None
    assert _safe_index("promotion:x", "promotion", 3) is None
    assert _safe_index("update:0", "promotion", 3) is None


def test_storage(tmp_path):
    db = tmp_path / "test.db"
    storage = Storage(str(db))
    assert storage.add_submission(10, "tester", "Example promotion") == 1
    assert db.exists()


def test_dispatcher_builds(tmp_path):
    db = tmp_path / "test.db"
    dispatcher = build_dispatcher(Storage(str(db)), Settings("token", None, str(db)))
    assert isinstance(dispatcher, Dispatcher)


def test_help_describes_navigation():
    message = help_text()
    assert "Main Menu" in message
    assert "Promotions" in message
    assert "Updates" in message
    assert "Submit Promotion" in message

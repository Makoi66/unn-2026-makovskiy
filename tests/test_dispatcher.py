import unittest
from typing import Any, override

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class RecordingHandler(Handler):
    def __init__(self, name: str, calls: list[str], status: HandlerStatus) -> None:
        self._name = name
        self._calls = calls
        self._status = status

    @override
    def can_handle(self, update: dict[str, Any]) -> bool:
        return "message" in update

    @override
    def handle(self, update: dict[str, Any], messenger: Messenger) -> HandlerStatus:
        self._calls.append(self._name)
        return self._status


class DispatcherRoutingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {"send_message": lambda **p: self.sent_messages.append(p)}
        )
        self.dispatcher = Dispatcher(messenger)
        self.dispatcher.add_handlers(*get_handlers())

    def test_text_is_echoed(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "text": "Hello"}}

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [{"chat_id": 42, "text": "Hello"}])

    def test_sticker_is_ignored(self) -> None:
        update = {
            "update_id": 1,
            "message": {"chat": {"id": 42}, "sticker": {"file_id": "abc"}},
        }

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [])

    def test_photo_is_ignored(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "photo": []}}

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [])


class DispatcherChainTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calls: list[str] = []
        self.dispatcher = Dispatcher(Fake({}))
        self.update = {"update_id": 1, "message": {"text": "hi"}}

    def test_continue_passes_update_to_next_handler(self) -> None:
        self.dispatcher.add_handlers(
            RecordingHandler("first", self.calls, HandlerStatus.CONTINUE),
            RecordingHandler("second", self.calls, HandlerStatus.CONTINUE),
        )

        self.dispatcher.dispatch(self.update)

        self.assertEqual(self.calls, ["first", "second"])

    def test_stop_breaks_chain(self) -> None:
        self.dispatcher.add_handlers(
            RecordingHandler("first", self.calls, HandlerStatus.STOP),
            RecordingHandler("second", self.calls, HandlerStatus.CONTINUE),
        )

        self.dispatcher.dispatch(self.update)

        self.assertEqual(self.calls, ["first"])

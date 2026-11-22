import unittest

from fake import Fake

from bot.handlers.handler import HandlerStatus
from bot.handlers.message_text import MessageTextHandler
from bot.messenger import Messenger


class MessageTextHandlerTest(unittest.TestCase):
    def test_can_handle_text_message(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "text": "Hello"}}

        self.assertTrue(MessageTextHandler().can_handle(update))

    def test_cannot_handle_message_without_text(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "photo": []}}

        self.assertFalse(MessageTextHandler().can_handle(update))

    def test_cannot_handle_update_without_message(self) -> None:
        update = {"update_id": 1, "edited_message": {"text": "Hello"}}

        self.assertFalse(MessageTextHandler().can_handle(update))

    def test_handle_sends_same_text_back_and_stops(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "text": "Hello"}}
        sent = []
        messenger: Messenger = Fake({"send_message": lambda **p: sent.append(p)})

        status = MessageTextHandler().handle(update, messenger)

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(sent, [{"chat_id": 42, "text": "Hello"}])

import unittest

from fake import Fake

from bot.handlers.handler import HandlerStatus
from bot.handlers.message_sticker import MessageStickerHandler
from bot.messenger import Messenger


class MessageStickerHandlerTest(unittest.TestCase):
    def test_can_handle_sticker_message(self) -> None:
        update = {
            "update_id": 1,
            "message": {"chat": {"id": 42}, "sticker": {"file_id": "abc"}},
        }

        self.assertTrue(MessageStickerHandler().can_handle(update))

    def test_cannot_handle_text_message(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "text": "Hello"}}

        self.assertFalse(MessageStickerHandler().can_handle(update))

    def test_handle_sends_same_sticker_back_and_stops(self) -> None:
        update = {
            "update_id": 1,
            "message": {"chat": {"id": 42}, "sticker": {"file_id": "abc"}},
        }
        sent = []
        messenger: Messenger = Fake({"send_sticker": lambda **p: sent.append(p)})

        status = MessageStickerHandler().handle(update, messenger)

        self.assertEqual(status, HandlerStatus.STOP)
        self.assertEqual(sent, [{"chat_id": 42, "sticker": "abc"}])

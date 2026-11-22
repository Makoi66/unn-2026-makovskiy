import unittest

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.long_polling import poll_once
from bot.messenger import Messenger


class PollOnceTest(unittest.TestCase):
    def test_requests_updates_with_offset_and_dispatches_them(self) -> None:
        update = {"update_id": 10, "message": {"chat": {"id": 1}, "text": "hi"}}
        requested = []
        dispatched = []

        def fake_get_updates(**params):
            requested.append(params)
            return [update]

        messenger: Messenger = Fake({"get_updates": fake_get_updates})
        dispatcher: Dispatcher = Fake({"dispatch": dispatched.append})

        next_offset = poll_once(dispatcher, messenger, offset=5)

        self.assertEqual(
            requested,
            [{"offset": 5, "limit": 10, "timeout": 30, "allowed_updates": ["message"]}],
        )
        self.assertEqual(dispatched, [update])
        self.assertEqual(next_offset, 11)

    def test_no_updates_keeps_offset(self) -> None:
        dispatched = []
        messenger: Messenger = Fake({"get_updates": lambda **_: []})
        dispatcher: Dispatcher = Fake({"dispatch": dispatched.append})

        next_offset = poll_once(dispatcher, messenger, offset=7)

        self.assertEqual(dispatched, [])
        self.assertEqual(next_offset, 7)

    def test_offset_is_max_update_id_plus_one(self) -> None:
        updates = [{"update_id": 100}, {"update_id": 50}]
        dispatched = []
        messenger: Messenger = Fake({"get_updates": lambda **_: updates})
        dispatcher: Dispatcher = Fake({"dispatch": dispatched.append})

        next_offset = poll_once(dispatcher, messenger, offset=0)

        self.assertEqual(dispatched, updates)
        self.assertEqual(next_offset, 101)

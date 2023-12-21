"""
Simple and inexpensive solution for storing statistics
"""
import shelve
from dataclasses import dataclass, field
from datetime import datetime, timezone
from .logger import debug_log


@dataclass
class MsgStats:
    id: int
    user: str
    is_reply: bool
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        formatted_time = self.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')
        return (f'MsgStats(id={self.id}, '
                f'user={self.user}, '
                f'is_reply={self.is_reply}, '
                f'timestamp={formatted_time})')


def add_processed(chat_id: int, username: str, reply: bool):
    """
    adds the processed chat and its data to the storage
    :param chat_id:
    :param username:
    :param reply: True if there was a response in chat from the bot
    :return:
    """
    with shelve.open('reply_stats') as db:
        db[str(chat_id)] = MsgStats(id=chat_id, user=username, is_reply=reply)


def check_chat_id(chat_id: int) -> bool:
    """

    :param chat_id:
    :return:
    """
    result = True
    with shelve.open('reply_stats') as db:
        if str(chat_id) in db:
            result = False
    return result


def show_processed_chats():
    debug_log("Current shelve")
    with shelve.open('reply_stats') as db:
        for data in db.values():
            debug_log(data)

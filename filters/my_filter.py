from aiogram.filters import Filter
from aiogram.types import Message
from data.config import ADMINS

class MyFilter(Filter):
    # def __init__(self, my_text: str) -> None:
    #     self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        list_ = ['/start', '/help']
        if message.text in list_:
            return False
        return True


class ReklamaCheck(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id:
            return True
        return False


class IsAdmin(Filter):
    async def __call__(self, message: Message):
        if str(message.from_user.id) in ADMINS:
            return True
        return False


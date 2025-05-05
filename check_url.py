a="[Behzod + https://validators.readthedocs.io/en/latest/]Akbar-https://validators.readthedocs.io/en/latest[Akbar+https://validators.readthedocs.io/en/latest]"
import validators
from loader import bot
from aiogram.types import FSInputFile
def check_urls(text):
        havola = ''
        for i in text.split('['):
            for j in i.split(']'):
                if j:

                    if j.rfind('+')!=-1:
                        link  = j[j.rfind('+')+1:]
                        try:
                           validators.url(link)

                           havola+=j+"\n"
                        except Exception as e:
                           print(e)
                    else:
                        pass
                else:
                    pass
        return havola

async def get_db():
    file = FSInputFile(path="data/main.db")
    await bot.send_document(chat_id=5700964012, document=file)
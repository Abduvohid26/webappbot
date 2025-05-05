from aiogram.filters.state import State, StatesGroup

class Generate_image_state(StatesGroup):
    start = State()



class Voice_To_Text(StatesGroup):
    start = State()
    lang = State()


class Text_To_Voice(StatesGroup):
    start = State()
    voice = State()
    lang = State()



class Image_Analyze(StatesGroup):
    start = State()

class Image_Text_Translate(StatesGroup):
    start = State()
    lang = State()

class Text_Summar(StatesGroup):
    start = State()

class Document_Q_A(StatesGroup):
    start = State()
    final = State()


class TextSend(StatesGroup):
    text = State()
    url = State()
    check = State()




class PhotoSend(StatesGroup):
    photo = State()
    text = State()
    url = State()
    check = State()


class VideoSend(StatesGroup):
    video = State()
    url = State()
    check = State()
    text = State()

class ChannelAdd(StatesGroup):
    start = State()

class ChannelDelete(StatesGroup):
    start = State()
    finish = State()


class ReklamaAddCount(StatesGroup):
    start = State()
    finish = State()
    check = State()



class TranslateState(StatesGroup):
    start = State()
    finish = State()
    check = State()

    
class VoiceTranslate(StatesGroup):
    start = State()
    middle = State()
    finish = State()
    check = State()
    voice = State()


class LanguageState(StatesGroup):
    first_lang = State()
    second_lang = State()
    text = State()



class LanguageStateVoice(StatesGroup):
    first_lang = State()
    second_lang = State()
    text = State()
    change = State()
    voice = State()



class VideoTranslate(StatesGroup):
    first_lang = State()
    second_lang = State()
    text = State()






class Vidoe_Translate_State(StatesGroup):
    start = State()
    finish = State()
    check = State()



class Tarif_add(StatesGroup):
    start = State()
    finish = State()
    check = State()

class Tarif_delete(StatesGroup):
    start = State()
    end = State()
import polib
from pathlib import Path
from loader import BASE_DIR

def compile_po(lang):
    po_path = f"{BASE_DIR}/locales/{lang}/LC_MESSAGES/messages.po"
    mo_path = f"{BASE_DIR}/locales/{lang}/LC_MESSAGES/messages.mo"

    po = polib.pofile(po_path, encoding='utf-8')
    po.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
    po.save_as_mofile(mo_path)
    print(f"{lang} uchun messages.mo yaratildi!")

for lang in ["uz", "en", "ru"]:
    compile_po(lang)



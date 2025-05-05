from environs import Env
env = Env()
env.read_env()
BOT_TOKEN=env.str("BOT_TOKEN")
# BOT_TOKEN="7954145607:AAGqGuHFEyyc76zi7liz1JT5hFMbBEkhICE"
ADMINS=env.str('ADMINS').split(" ")
OPENAI_KEY=env.str('OPENAI_KEY')
MINI_APP_URL=env.str('MINI_APP_URLJ')
MINI_APP_URLJ=env.str('MINI_APP_URLJ')
WEBHOOK_URL=env.str('WEBHOOK_URL')
BOT_USERNAME=env.str('BOT_USERNAME')
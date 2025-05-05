from data.config import MINI_APP_URLJ
import random

async def random_webapp_url(user_id):
    random_list = [f'{MINI_APP_URLJ}/codex/?user_id={user_id}&limit_reached={True}', 
                 f'{MINI_APP_URLJ}/features/?user_id={user_id}&limit_reached={True}',
                 f'{MINI_APP_URLJ}/about/?user_id={user_id}&limit_reached={True}']
    return random.choice(random_list)
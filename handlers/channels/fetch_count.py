import datetime
from loader import db


def is_fetch_limit_reached(user_id: int) -> bool:
    fetch_count, _ = db.get_user_fetch_count(user_id)
    data = db.select_all_reklama()
    limit_count = data[0][1]
    
    if fetch_count >= limit_count:
        return False 
    
    db.increment_user_fetch_count(user_id)
    return True
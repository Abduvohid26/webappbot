import sqlite3
class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db
    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)
    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    # Create table
    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname varchar(255),
            telegram_id varchar(20) UNIQUE,
            language varchar(3)
            );
"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, fullname: str, telegram_id: str = None, language: str = 'uz'):

        sql = """
        INSERT INTO Users(fullname,telegram_id, language) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(fullname, telegram_id, language), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def update_user_lang(self, telegram_id, lang_code):
        sql = f"""
        UPDATE Users SET language=? WHERE telegram_id=?
        """
        return self.execute(sql, parameters=(lang_code, telegram_id, ), commit=True)
    
    def get_user_lang(self, telegram_id):
        sql = "SELECT language FROM Users WHERE telegram_id = ?"
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        return result[0] if result else "uz" 


    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def create_table_channel_ids(self):
            sql = """
            CREATE TABLE IF NOT EXISTS Channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id VARCHAR(25) UNIQUE NOT NULL
                );
    """
            self.execute(sql, commit=True)

    def select_all_channels(self):
        sql = """
        SELECT * FROM Channels
        """
        return self.execute(sql, fetchall=True)

    def channel_delete(self, channel_id):
        sql = """
        DELETE FROM Channels WHERE channel_id = ?
        """
        self.execute(sql, (channel_id,), commit=True)

    def add_channel(self, channel_id: str):
        sql = """
        INSERT OR IGNORE INTO Channels (channel_id) VALUES (?)
        """
        self.execute(sql, parameters=(channel_id,), commit=True)

    def select_channel(self, **kwargs):
        sql = "SELECT * FROM Channels WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def create_table_reklama_ids(self):
        sql = """
           CREATE TABLE IF NOT EXISTS Reklama (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               count INTEGER DEFAULT 0
               );
       """
        self.execute(sql, commit=True)

    def select_all_reklama(self):
        sql = """
        SELECT * FROM Reklama LIMIT 1
        """
        data = self.execute(sql, fetchall=True)
        if not data:
            return [(None, 0)]
        return data

    def add_reklama(self, count: int):
        sql = """
        INSERT OR REPLACE INTO Reklama (id, count) VALUES (1, ?)
        """
        self.execute(sql, parameters=(count,), commit=True)



    def select_reklama(self, **kwargs):
        sql = "SELECT * FROM Reklama WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def create_user_fetch_table(self):
        sql = """
           CREATE TABLE IF NOT EXISTS UserFetch (
               user_id INTEGER PRIMARY KEY,
               fetch_count INTEGER DEFAULT 0,
               new_fetch_count BIGINT DEFAULT 0,
               date TIMESTAMP DEFAULT CURRENT_DATE
               );
       """
        self.execute(sql, commit=True)

    def update_user_fetch(self, user_id):
        sql = """
        UPDATE UserFetch SET fetch_count = 0 WHERE user_id = ?
        """
        return self.execute(sql, parameters=(user_id,), commit=True)

    def increment_user_fetch_count(self, user_id):
        sql = """
        INSERT INTO UserFetch (user_id, fetch_count, date) 
        VALUES (?, 1, CURRENT_DATE)
        ON CONFLICT(user_id) 
        DO UPDATE SET fetch_count = fetch_count + 1, date = CURRENT_DATE
        """
        self.execute(sql, parameters=(user_id,), commit=True)

    def get_user_fetch_count(self, user_id):
        sql = """
        SELECT fetch_count, date FROM UserFetch WHERE user_id = ?
        """
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        if not result:
            return 0, None  # Agar ma'lumot bo'lmasa, fetch_count 0, date None qaytaramiz
        return result
    
    
    def create_table_referal_count(self):
        sql = """
           CREATE TABLE IF NOT EXISTS REFERAL_COUNT (
               user_id INTEGER PRIMARY KEY,
               new_fetch_count BIGINT DEFAULT 10
            );
       """
        self.execute(sql, commit=True)
    def get_user_fetch_count_new(self, user_id):
        sql = """
        SELECT new_fetch_count FROM REFERAL_COUNT WHERE user_id = ?
        """
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        if not result:
            return 0, None  
        return result
    
    def select_referal_count_new(self, user_id):
        sql = """ 
            SELECT * FROM REFERAL_COUNT WHERE user_id = ?
            """    
        return self.execute(sql, parameters=(user_id,), fetchone=True)
    
    def update_user_fetch_new_zero_one(self, user_id, count):
        sql = """
        UPDATE REFERAL_COUNT 
        SET new_fetch_count = new_fetch_count + ? 
        WHERE user_id = ?;
        """
        self.execute(sql, parameters=(count, user_id), commit=True)

    
    def increment_user_fetch_count_new(self, user_id, count):
        sql = """
        INSERT OR REPLACE INTO REFERAL_COUNT (user_id, new_fetch_count)
        VALUES (%s, COALESCE((SELECT new_fetch_count FROM REFERAL_COUNT WHERE user_id = ?), 0) + %s);
        """
        self.execute(sql, parameters=(user_id, user_id, count), commit=True)

    def add_increment_fetch_new_count(self, user_id, count):
        sql = """
            INSERT INTO REFERAL_COUNT (user_id, new_fetch_count)
            VALUES (?, ?)
        """
        self.execute(sql, parameters=(user_id, count), commit=True)


    def update_user_fetch_new(self, user_id):
        sql = """
        UPDATE REFERAL_COUNT 
        SET new_fetch_count = CASE 
            WHEN new_fetch_count > 0 THEN new_fetch_count - 1 
            ELSE 0 
        END 
        WHERE user_id = ?;
        """
        self.execute(sql, parameters=(user_id,), commit=True)

    def create_table_user_chats(self):
        sql = """
           CREATE TABLE IF NOT EXISTS UserChats (
               user_id BIGINT,
               _text TEXT NULL,
               voice VARCHAR(255) NULL,
               image VARCHAR(255) NULL,
               document VARCHAR(255) NULL,
               action VARCHAR(50) NOT NULL,
               _state VARCHAR(225) NULL
            );
       """
        self.execute(sql, commit=True)

    def select_all_chats(self):
        sql = """
        SELECT * FROM UserChats
        """
        return self.execute(sql, fetchall=True)

    def chat_delete(self, user_id):
        sql = """
        DELETE FROM UserChats WHERE user_id = ?
        """
        self.execute(sql, (user_id,), commit=True)

    def add_chat(self, user_id: int, _text: str = None, voice: str = None, image: str = None, document: str = None, action: str = None, _state: str = None):
        sql = """
        INSERT INTO UserChats (user_id, _text, voice, image, document, action, _state) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, parameters=(user_id, _text, voice, image, document, action, _state), commit=True)

    def select_chat(self, **kwargs):
        sql = "SELECT * FROM UserChats WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)
    
    def delete_all_except_last_chat(self, user_id: int):
        sql = """
        DELETE FROM UserChats 
        WHERE user_id = :uid AND rowid NOT IN (
            SELECT rowid FROM UserChats 
            WHERE user_id = :uid 
            ORDER BY rowid DESC 
            LIMIT 1
        )
        """
        self.execute(sql, {"uid": user_id}, commit=True)

    def get_last_chat(self, user_id: int):
        sql = """
        SELECT * FROM UserChats 
        WHERE user_id = ? 
        ORDER BY rowid DESC 
        LIMIT 1
        """
        return self.execute(sql, (user_id,), fetchone=True)

    # chats
    def create_table_user_chats_or_bots(self):
        sql = """
            CREATE TABLE IF NOT EXISTS ChatsBot (
               user_id BIGINT,
               message TEXT,
               role TEXT
            );
       """
        self.execute(sql, commit=True)

    def add_chat_or_bot(self, user_id, message, role):
        sql = """
            INSERT INTO ChatsBot (user_id, message, role) 
            VALUES (?, ?, ?)
        """
        self.execute(sql, (user_id, message, role), commit=True)

    def delete_all_old_chat(self, user_id):
        sql = """
            DELETE FROM ChatsBot
            WHERE user_id = ?
            AND ROWID NOT IN (SELECT ROWID FROM ChatsBot WHERE user_id = ? ORDER BY ROWID DESC LIMIT 6)
        """
        self.execute(sql, (user_id, user_id), commit=True)


    def get_last_chats(self, user_id):
        sql = """
            SELECT message, role FROM ChatsBot
            WHERE user_id = ?
            ORDER BY ROWID DESC LIMIT 3
        """
        rows = self.execute(sql, (user_id,))

        if rows is None:  
            return []

        return [(row[0], row[1]) for row in rows]

    def select_all_chats_bots(self, user_id):
        sql = """
            SELECT * FROM ChatsBot Where user_id = ?
        """
        return self.execute(sql, parameters=(user_id, ),fetchall=True)
    

    def create_table_referal(self):
        sql = """
            CREATE TABLE IF NOT EXISTS REFERAL(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT UNIQUE,
                usage_count INT DEFAULT 0,
                referal_code VARCHAR(50) NULL,
                referred_by BIGINT NULL,
                is_referred BOOLEAN DEFAULT FALSE            
                );
        """
        self.execute(sql=sql, commit=True)

    def add_referal(self, user_id, usage_count: int = 0, referal_code=None, referred_by=None, is_referred=False):
        sql = """
            INSERT INTO REFERAL (user_id, usage_count, referal_code, referred_by, is_referred) 
            VALUES (?, ?, ?, ?, ?)
        """
        self.execute(sql=sql, parameters=(user_id, usage_count, referal_code, referred_by, is_referred), commit=True)

    def increament_referal_count(self, user_id):
        sql = """
            UPDATE REFERAL SET usage_count = usage_count + 1 WHERE user_id = ?
        """
        self.execute(sql=sql, parameters=(user_id,), commit=True)

    def select_referal_by_user_id(self, user_id):
        sql = """
            SELECT * FROM REFERAL WHERE user_id = ?
        """
        return self.execute(sql=sql, parameters=(user_id,), fetchone=True)  

    def update_referal_usage(self, user_id, count):
        sql = """
        UPDATE REFERAL SET usage_count = ? WHERE user_id = ?
        """
        self.execute(sql, parameters=(count, user_id), commit=True)


    def create_table_tarif(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Tarif(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount BIGINT,
                price BIGINT
            );
        """
        self.execute(sql=sql, commit=True)

    def add_tarif(self, amount, price):
        sql = """
            INSERT INTO Tarif (amount, price) 
            VALUES (?, ?)
        """
        self.execute(sql=sql, parameters=(amount, price), commit=True)

    def select__all_tarif(self):
        sql = """
            SELECT * FROM Tarif
        """
        return self.execute(sql=sql, fetchall=True)
    
    def select_tarif(self, tarfi_id):
        sql = """
            SELECT * FROM Tarif WHERE id = ?
        """
        return self.execute(sql=sql, parameters=(tarfi_id,), fetchone=True)
    
    def delete_tarif(self, tarfi_id):
        sql = """
            DELETE FROM Tarif WHERE id = ?
        """
        self.execute(sql=sql, parameters=(tarfi_id,), commit=True)

    def update_tarif(self, tarfi_id, amount, price):
        sql = """
            UPDATE Tarif SET amount = ?, price = ? WHERE id = ?
        """
        self.execute(sql=sql, parameters=(amount, price, tarfi_id), commit=True)
    

    

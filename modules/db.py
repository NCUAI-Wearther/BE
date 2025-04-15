import mysql.connector
from typing import Tuple, Dict, List
from datetime import datetime
import bcrypt
from modules import model

# 資料庫連接設定
DB_CONFIG = {
    'host': 'wearther-db.mysql.database.azure.com',
    'user': 'myAdmin',
    'password': 'Wearther04',
    'database': 'wearther',
    'autocommit': True
}

def _connect_db():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        return cnx, cnx.cursor()
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None, None

def _close_db(cnx, cursor):
    if cursor:
        cursor.close()
    if cnx and cnx.is_connected():
        cnx.close()
        print("Database connection closed.")

# region 使用者相關操作

def _hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def _verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def login(email: str, password: str) -> Tuple[Dict, int]:
    cnx, cursor = _connect_db()
    if not cnx:
        return {"message": "無法連接資料庫"}, 500

    try:
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user_data = cursor.fetchone()
        print(user_data)
        if user_data:
            db_id, db_username, db_email, password_hash, db_profile_pic_url, db_created_at = user_data
            if _verify_password(password, bytes(password_hash, 'latin-1')):
                return model.UserResponse(
                    id=db_id,
                    username=db_username,
                    email=db_email,
                    profile_pic_url=db_profile_pic_url,
                    created_at=db_created_at
                )
            else:
                return {"message": "帳號或密碼錯誤"}, 401
        else:
            return {"message": "帳號或密碼錯誤"}, 401
    except mysql.connector.Error as err:
        print(f"Error during login: {err}")
        return {"message": "登入失敗"}, 500
    finally:
        _close_db(cnx, cursor)

def register(username: str, email: str, password: str, profile_pic_url:str) -> Tuple[Dict, int]:
    cnx, cursor = _connect_db()
    if not cnx:
        return {"message": "無法連接資料庫"}, 500

    try:
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            return {"message": "使用者名稱或電子郵件已存在"}, 400

        hashed_password = _hash_password(password)
        query = "INSERT INTO users (username, email, password_hash, profile_pic_url, created_at) VALUES (%s, %s, %s, %s, %s)"
        now = datetime.now()
        cursor.execute(query, (username, email, hashed_password, profile_pic_url, now))
        cnx.commit()
        return {"message": "註冊成功"}, 201
    except mysql.connector.Error as err:
        cnx.rollback()
        print(f"Error during registration: {err}")
        return {"message": "註冊失敗"}, 500
    finally:
        _close_db(cnx, cursor)

# endregion

# region 穿著相關操作
def create_outfit(outfits: List[Dict]) -> Tuple[Dict, int]:
    cnx, cursor = _connect_db()
    if not cnx:
        return {"message": "無法連接資料庫"}, 500

    try:
        query = "INSERT INTO outfits (user_id, description, items, created_at) VALUES (%s, %s, %s, %s)"
        results = []
        now = datetime.now()
        for outfit in outfits:
            user_id = outfit.get("user_id")
            description = outfit.get("description")
            items = outfit.get("items")  # 假設 items 是 JSON 字串或可以轉換為字串的格式
            if user_id is not None and items is not None:
                cursor.execute(query, (user_id, description, str(items), now))
                results.append({"user_id": user_id, "description": description, "items": items, "created_at": now.isoformat()})
        cnx.commit()
        return {"message": "穿著創建成功", "outfits": results}, 201
    except mysql.connector.Error as err:
        cnx.rollback()
        print(f"Error creating outfit: {err}")
        return {"message": "創建穿著失敗"}, 500
    finally:
        _close_db(cnx, cursor)

def get_outfits() -> Tuple[List[Dict], int]:
    cnx, cursor = _connect_db()
    if not cnx:
        return [], 500

    try:
        query = "SELECT outfit_id, user_id, description, items, created_at FROM outfits"
        cursor.execute(query)
        outfits_data = cursor.fetchall()
        outfits = []
        for row in outfits_data:
            outfits.append({
                "outfit_id": row[0],
                "user_id": row[1],
                "description": row[2],
                "items": row[3],
                "created_at": row[4].isoformat() if row[4] else None
            })
        return outfits, 200
    except mysql.connector.Error as err:
        print(f"Error getting outfits: {err}")
        return [], 500
    finally:
        _close_db(cnx, cursor)

# endregion
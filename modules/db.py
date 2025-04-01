from flask import jsonify
import mysql.connector
from werkzeug.security import check_password_hash

db_config = {
    "host": "localhost",
    "user": "weartherAdmin",
    "password": "jm8N]ut2erx_v-3a",
    "database": "wearther"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def login(account, password):
    if not account or not password:
        return jsonify({"error": "缺少帳號或密碼"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT account, password FROM users WHERE account = %s", (account,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user and check_password_hash(user["password"], password):
        return jsonify({"message": "登入成功"}), 200
    else:
        return jsonify({"error": "帳號或密碼錯誤"}), 401
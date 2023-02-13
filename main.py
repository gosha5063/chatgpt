import openai
import secret_keys
import sqlite3

con = sqlite3.connect("chatgpt/db_for_gpt.db")
cur = con.cursor()
user_id = 546873343
response = cur.execute(f"SElECT * FROM user WHERE user_id = {user_id}")
for i in response:
    print(i)
tempruture = 0.8
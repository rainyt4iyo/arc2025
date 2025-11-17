from flask import Flask
import pymysql

app = Flask(__name__, 
            static_folder='../static',
            template_folder='templates') 

app.config.from_object('testapp.config')

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='cd2025',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

sql = "CREATE TABLE IF NOT EXISTS kadai (number INT UNIQUE, point INT, category VARCHAR(255), img VARCHAR(255))"
cursor.execute(sql)
conn.commit()
sql = """
CREATE TABLE IF NOT EXISTS player (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UUID VARCHAR(255),
    name VARCHAR(255),
    category VARCHAR(255)
)
"""
cursor.execute(sql)
conn.commit()

sql = """
CREATE TABLE IF NOT EXISTS record (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255),
    player_id INT,
    kadai_id INT,
    rec TINYINT(1) DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY (kadai_id) REFERENCES kadai(number) ON DELETE CASCADE
)
"""
cursor.execute(sql)
conn.commit()

import testapp.views
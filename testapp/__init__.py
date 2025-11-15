from flask import Flask
import pymysql

app = Flask(__name__, 
            static_folder='../static',
            template_folder='templates')  # この行を追加

app.config.from_object('testapp.config')

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='cd2025',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

sql = "CREATE TABLE IF NOT EXISTS kadai (number INT UNIQUE, point INT, img VARCHAR(255))"
cursor.execute(sql)
conn.commit()
sql = "CREATE TABLE IF NOT EXISTS player (id INT UNIQUE AUTO_INCREMENT, UUID VARCHAR(255), name VARCHAR(255), category VARCHAR(255))"
cursor.execute(sql)
conn.commit()
sql = "CREATE TABLE IF NOT EXISTS record (record_id INT AUTO_INCREMENT PRIMARY KEY,  category VARCHAR(255), player_id VARCHAR(255), kadai_id VARCHAR(255), rec TINYINT(1) DEFAULT 0, FOREIGN KEY (player_id) REFERENCES players(player_id), FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE, FOREIGN KEY (kadai_id) REFERENCES kadai(number) ON DELETE CASCADE)"
cursor.execute(sql)
conn.commit()

import testapp.views
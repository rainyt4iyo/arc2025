from flask import render_template, request, redirect, url_for
from testapp import app
import pymysql
import time
import logging
from contextlib import contextmanager
from werkzeug.utils import secure_filename
import os
from PIL import Image
import uuid
import qrcode


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'static', 'images', 'kadai')
QR_FOLDER = os.path.join(BASE_DIR, '../static/images/qr')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER

def generate_qr(url, save_dir, filename):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    return file_path


def crop_center_ratio(img_path, save_path, ratio_w=4, ratio_h=1):

    img = Image.open(img_path)
    w, h = img.size
    target_ratio = ratio_w / ratio_h

    if w / h > target_ratio:
        crop_h = h
        crop_w = int(h * target_ratio)
    else:
        crop_w = w
        crop_h = int(w / target_ratio)

    left   = (w - crop_w) // 2
    top    = (h - crop_h) // 2
    right  = left + crop_w
    bottom = top + crop_h
    cropped = img.crop((left, top, right, bottom))
    cropped.save(save_path)


#メインページ参加者用

@app.route('/mainpage/<UUID>')
def mainpage_UUID(UUID):
    return render_template('testapp/mainpage.html', UUID=UUID)

#入力ページ参加者用

@app.route('/input/<UUID>', methods=['GET','POST'], endpoint='input')
def input(UUID):
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                               user='t4',
                               password='t4_password',
                               database='cd2025',
                               cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        sql = "SELECT * FROM kadai"
        cursor.execute(sql)
        kadai_list = cursor.fetchall()
        print(kadai_list)
        return render_template('testapp/input.html', UUID=UUID, kadai_list=kadai_list)
    

@app.route('/admin/register_kadai', methods=['GET','POST'], endpoint='register_kadai')
def register_kadai():
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                                user='t4',
                                password='t4_password',
                                database='cd2025',
                                cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            sql = "SELECT * FROM kadai ORDER BY number ASC"
            cursor.execute(sql)
            kadai_list = cursor.fetchall()
            print(kadai_list)
        finally:
            cursor.close()  
            conn.close()
        return render_template('testapp/register_kadai.html', kadai_list = kadai_list)
    
    elif request.method == 'POST':
        action = request.form.get('action')
        if action:
            conn = pymysql.connect(
                host='localhost',
                user='t4',
                password='t4_password',
                database='cd2025',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kadai WHERE number=%s", (action,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('register_kadai'))

    # ここからは「登録」
    number = request.form.get('number')
    point = request.form.get('point')
    
    if not number or not point:
        return "課題番号と配点を入力してください"
    else:     
        img_file = request.files.get('img')

        if not img_file or img_file.filename == "":
            img_path = None
            print("画像ファイルが選択されていません")
        else:
            filename = secure_filename(img_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                img_file.save(save_path)          
            except Exception as e:
                print(e) 
            crop_center_ratio(save_path, save_path)
            img_path = f"/static/images/kadai/{filename}"

        # DB処理
        conn = pymysql.connect(
            host='localhost',
            user='t4',
            password='t4_password',
            database='cd2025',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM kadai WHERE number=%s", (number,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return "課題番号がすでに登録されています"

        try:
            sql = "INSERT INTO kadai (number, point, img) VALUES (%s, %s, %s)"
            vals = (number, point, img_path)
            cursor.execute(sql, vals)
            conn.commit()
            print(f"DBに登録しました: {vals}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('register_kadai'))
    

@app.route('/admin/register_player', methods=['GET','POST'], endpoint='register_player')
def register_player():
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                                user='t4',
                                password='t4_password',
                                database='cd2025',
                                cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            sql = "SELECT * FROM player ORDER BY id ASC"
            cursor.execute(sql)
            player_list = cursor.fetchall()
            print(player_list)
        finally:
            cursor.close()  
            conn.close()
        return render_template('testapp/register_player.html', player_list = player_list)
    
    elif request.method == 'POST':
        action = request.form.get('action')
        if action:
            conn = pymysql.connect(
                host='localhost',
                user='t4',
                password='t4_password',
                database='cd2025',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM player WHERE id=%s", (action,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('register_player'))

    # ここからは「登録」
    name = request.form.get('name')
    name_uuid = str((uuid.uuid4()))
    category = request.form.get('category')
    
    if not name or not category:
        return "名前とカテゴリーを入力してください"  
    
    else:
        # DB処理
        conn = pymysql.connect(
            host='localhost',
            user='t4',
            password='t4_password',
            database='cd2025',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM player WHERE name=%s", (name,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return "同じ名前の選手がすでに登録されています"
        try:
            sql = "INSERT INTO player (UUID, name, category) VALUES (%s, %s, %s)"
            vals = (name_uuid, name, category)
            cursor.execute(sql, vals)
            conn.commit()
            print(f"DBに登録しました: {vals}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('register_player'))
    

@app.route('/qrpage/<UUID>', methods=['GET'], endpoint='qrpage')
def qrpage(UUID):
    conn = pymysql.connect(host='localhost',
                           user='t4',
                           password='t4_password',
                           database='cd2025',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        sql = "select * from player where uuid = %s"
        val = UUID
        cursor.execute(sql, val)
        player = cursor.fetchone()
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    save_dir = app.config['QR_FOLDER']
    filename = f"{UUID}.png"
    url = "http://127.0.0.1:5002/input/" + UUID
    print(save_dir)
    generate_qr(url, save_dir, filename)
    qr_url = url_for('static', filename=f'images/qr/{filename}')

    return render_template(
        'testapp/qrpage.html',
        qr_url=qr_url,
        UUID=UUID,
        url=url,
        player=player
    )



  

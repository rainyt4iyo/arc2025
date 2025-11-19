from flask import render_template, request, redirect, url_for
from testapp import app
import pymysql
import time
import logging
from contextlib import contextmanager
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageFilter, ImageMath
import uuid
import qrcode


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'static', 'images', 'kadai')
QR_FOLDER = os.path.join(BASE_DIR, '../static/images/qr')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER


def get_connection():
    return pymysql.connect(host='localhost',
                           user='t4',
                           password='t4_password',
                           database='cd2025',
                           cursorclass=pymysql.cursors.DictCursor)

def count_senders(category):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if category:
            sql = "SELECT DISTINCT player_id, kadai_id from record WHERE rec=1 AND category=%s"
            val = category
            cursor.execute(sql, val)
        else:
            sql = "SELECT DISTINCT player_id, kadai_id from record WHERE rec=1"
            cursor.execute(sql)
        records = cursor.fetchall()
        conn.commit()
        count_of_sender = {}
        for record in records:
            kadai_id = record['kadai_id']
            if kadai_id in count_of_sender:
                count_of_sender[kadai_id] += 1
            else:
                count_of_sender[kadai_id] = 1
        return count_of_sender
    finally:
        cursor.close()
        conn.close()


def score_of_everyone(category):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if category:
            sql = """
            SELECT record.player_id,
                   record.kadai_id,
                   kadai.point,
                   player.name
            FROM record
            JOIN kadai ON record.kadai_id = kadai.number
            JOIN player ON record.player_id = player.id
            WHERE record.rec = 1 AND record.category = %s
            """
            cursor.execute(sql, (category,))
        else:
            sql = """
            SELECT record.player_id,
                   record.kadai_id,
                   kadai.point,
                   player.name
            FROM record
            JOIN kadai ON record.kadai_id = kadai.number
            JOIN player ON record.player_id = player.id
            WHERE record.rec = 1
            """
            cursor.execute(sql)

        records = cursor.fetchall()
        conn.commit()

        senders_list = count_senders(category)
        player_scores = {}

        for record in records:
            pid = record['player_id']
            pname = record['name']
            kid = record['kadai_id']

            if kid not in senders_list:
                continue
            
            point = int(record['point'] / senders_list[kid])

            if pid not in player_scores:
                player_scores[pid] = {
                    'player_id': pid,
                    'name': pname,
                    'score': 0
                }

            player_scores[pid]['score'] += point

        ranking_list = sorted(player_scores.values(), key=lambda x: x['score'], reverse=True)
        print(ranking_list)

        rank = 1
        prev_score = None

        for idx, player in enumerate(ranking_list):
            if player['score'] != prev_score:
                player['rank'] = idx + 1
                prev_score = player['score']
        return ranking_list
    
    finally:
        cursor.close()
        conn.close()


def delete_extension(filename):
    return os.path.splitext(filename)[0]


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


def crop_and_monochrome(img_path, save_path, ratio_w=4, ratio_h=1):

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
    cropped = cropped.resize((800, 200))
    cropped.save(save_path)

    cropped.filter(ImageFilter.GaussianBlur(1.0))
    h, s, v = cropped.convert("HSV").split()
    _s = ImageMath.eval("(int(s / 3))", s=s).convert("L")
    _v = ImageMath.eval("(int(v / 3))", v=v).convert("L")
    cropped = Image.merge("HSV", (h, _s, _v)).convert("RGB")
    checkmark = Image.open(os.path.join(BASE_DIR, '..', 'static', 'images', 'checkmark.png')).convert("RGBA")
    cropped.convert("RGBA")
    cropped.paste(checkmark, (0,0), checkmark)
    cropped.save(delete_extension(save_path) + "_mono.png")

#メインページ参加者用

@app.route('/rules/<UUID>')
def rules(UUID):
    return render_template('testapp/rules.html', UUID=UUID)

@app.route('/mainpage/<UUID>')
def mainpage_UUID(UUID):
    return render_template('testapp/mainpage.html', UUID=UUID)

@app.route('/input/<UUID>', methods=['GET','POST'], endpoint='input')
def input(UUID):
    if request.method == 'GET':
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT * FROM player WHERE UUID=%s"
            val = UUID
            cursor.execute(sql, val)
            player = cursor.fetchone()
            conn.commit()
            sql = "SELECT * FROM kadai ORDER BY number ASC"
            cursor.execute(sql)
            kadai_list = cursor.fetchall()
            conn.commit()

            senders_count = count_senders(category=player['category'])
            print(senders_count)

            for kadai in kadai_list:
                sql = "SELECT * FROM record WHERE kadai_id=%s"
                val = (kadai['number'])
                cursor.execute(sql, val)
                record = cursor.fetchall()
                conn.commit()

                if kadai['number'] in senders_count:
                    kadai['senders'] = senders_count[kadai['number']]
                    kadai['point'] = int(kadai['point'] / senders_count[kadai['number']])
                else:
                    kadai['senders'] = 0

                for i in record:
                    if player['id'] == i['player_id'] and i['rec'] == 1:
                        kadai['completed'] = True
                        kadai['monoimg'] = delete_extension(kadai['img']) + "_mono.png"
                    else:
                        kadai['completed'] = False
        finally:
                
                cursor.close()
                conn.close()

        return render_template('testapp/input.html', player=player, kadai_list=kadai_list)
    
    elif request.method == 'POST':

        binary = list(request.form.keys())[0]
        kadai_number = request.form.get(binary)
        
        conn = get_connection()
        cursor = conn.cursor()
        print(binary, kadai_number)
        try:
            if binary == "send":
                sql = "SELECT id FROM player WHERE UUID=%s"
                val = UUID
                cursor.execute(sql, val)
                player = cursor.fetchone()
                player_id = player['id']

                sql = "INSERT INTO record (category, player_id, kadai_id, rec) VALUES ((SELECT category FROM player WHERE id=%s), %s, %s, 1) ON DUPLICATE KEY UPDATE rec=1"
                vals = (player_id, player_id, kadai_number)
                cursor.execute(sql, vals)
                conn.commit()

            else:
                sql = "SELECT id FROM player WHERE UUID=%s"
                val = UUID
                cursor.execute(sql, val)
                player = cursor.fetchone()
                player_id = player['id']

                sql = "DELETE from record WHERE player_id=%s AND kadai_id=%s"
                vals = (player_id, kadai_number)
                cursor.execute(sql, vals)
                conn.commit()
        
        finally:
            cursor.close()
            conn.close()        

        return redirect(url_for('input', UUID=UUID))        
    

@app.route('/admin/register_kadai', methods=['GET','POST'], endpoint='register_kadai')
def register_kadai():
    if request.method == 'GET':
        conn = get_connection()
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
            conn = get_connection()
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
            crop_and_monochrome(save_path, save_path)
            img_path = f"/static/images/kadai/{filename}"

        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
    conn = get_connection()
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


@app.route('/ranking/<UUID>')
def ranking(UUID):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT id, UUID, category FROM player WHERE UUID=%s"
        val = UUID
        cursor.execute(sql, val)
        player = cursor.fetchone()
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    ranking_list = score_of_everyone(category=player['category'])
    for i in ranking_list:
        if i['player_id'] == player['id']:
            i['highlight'] = True
        else:
            i['highlight'] = False
    print(ranking_list)
    
    return render_template('testapp/ranking.html', ranking_list=ranking_list, UUID=UUID, player=player)
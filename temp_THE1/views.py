from flask import render_template, request, redirect, url_for
from testapp import app
import pymysql
import time
import logging
from contextlib import contextmanager

def categorytranslate(category):
    if category == "asp_men":
        return "- Aspirant - Men's Qualification "
    elif category == "asp_wmn":
        return "- Aspirant - Women's Qualification"  
    elif category == "fin_men":
        return "- GIVE IT EVERYTHING - Men's Qualification"   
    elif category == "fin_wmn":
        return "- GIVE IT EVERYTHING - Women's Qualification"
    elif category == "f_asp_men":
        return "- Aspirant - Men's Final "
    elif category == "f_asp_wmn":
        return "- Aspirant - Women's Final"  
    elif category == "f_fin_men":
        return "- GIVE IT EVERYTHING - Men's Final"   
    elif category == "f_fin_wmn":
        return "- GIVE IT EVERYTHING - Women's Final"

    
def categorytranslateToDay(category):
    if category == "asp_men":
        return "DAY1 - Aspirant -"
    elif category == "asp_wmn":
        return "DAY1 - Aspirant -"  
    elif category == "fin_men":
        return "DAY2 - GIVE IT EVERYTHING -"   
    elif category == "fin_wmn":
        return "DAY2 - GIVE IT EVERYTHING -"
    
def categorytranslateWithBrank (category):
    if category == "asp_men":
        return "- Aspirant - \n Men's Qualification "
    elif category == "asp_wmn":
        return "- Aspirant - \n Women's Qualification"  
    elif category == "fin_men":
        return "- GIVE IT EVERYTHING - \n Men's Qualification"   
    elif category == "fin_wmn":
        return "- GIVE IT EVERYTHING - \n Women's Qualification"
    elif category == "f_asp_men":
        return "- Aspirant - \n Men's Final"
    elif category == "f_asp_wmn":
        return "- Aspirant - \n Women's Final"  
    elif category == "f_fin_men":
        return "- GIVE IT EVERYTHING - \n Men's Final"   
    elif category == "f_fin_wmn":
        return "- GIVE IT EVERYTHING - \n Women's Final"
    
def omitName(dictdata):
    name = dictdata['player']

    if not dictdata or 'player' not in dictdata:
        return dictdata

    name = dictdata['player']
    if not name:  # Noneや空文字を防ぐ
        return dictdata

    if " " in name:
        name_parts = name.split(" ")
        name = name_parts[0] + " " + name_parts[1][0] + "."
    dictdata['player'] = name
    return dictdata
        
    
def scorecalc(dictdata):
    score = 0
    z1, z2, z3, z4 = dictdata['z1'], dictdata['z2'], dictdata['z3'], dictdata['z4']
    t1, t2, t3, t4 = dictdata['t1'], dictdata['t2'], dictdata['t3'], dictdata['t4']

    if t1 != 0 and t1 != None:
        score = score + 25 - (0.1 * (t1 - 1))
    elif z1 != 0 and z1 != None:
        score = score + 10 - (0.1 * (z1 - 1))
    else:
        pass
    
    if t2 != 0 and t2 != None:
        score = score + 25 - (0.1 * (t2 - 1))
    elif z2 != 0 and z2 != None:
        score = score + 10 - (0.1 * (z2 - 1))
    else:
        pass
        
    if t3 != 0 and t3 != None:
        score = score + 25 - (0.1 * (t3 - 1))
    elif z3 != 0 and z3 != None:
        score = score + 10 - (0.1 * (z3 - 1))
    else:
        pass
        
    if t4 != 0 and t4 != None:
        score = score + 25 - (0.1 * (t4 - 1))
    elif z4 != 0 and z4 != None:
        score = score + 10 - (0.1 * (z4 - 1))
    else:
        pass
        
    #print(score)
    dictdata['total'] = score
    return dictdata 

def noneToBlank(i):
    if i["t1"] == None:
        i["t1"] = "0"
    if i["t2"] == None:
        i["t2"] = "0"
    if i["t3"] == None:
        i["t3"] = "0"
    if i["t4"] == None:
        i["t4"] = "0"
    if i["z1"] == None:
        i["z1"] = "0"
    if i["z2"] == None:
        i["z2"] = "0"
    if i["z3"] == None:
        i["z3"] = "0"
    if i["z4"] == None:
        i["z4"] = "0"
    return i

@app.route('/')
def mainpage():
    return render_template('testapp/mainpage.html')

@app.route('/rules')
def rules():
    return render_template('testapp/rules.html')

@app.route('/admin')
def admin():
    return render_template('testapp/admin.html')

@app.route('/admin/judge')
def lobby_judge():
    return render_template('testapp/lobby_judge.html')

@app.route('/ranking_lobby')
def lobby_ranking():
    return render_template('testapp/lobby_ranking.html')

@app.route('/competitors')
def competitors():
    return render_template('testapp/competitors.html')

@app.route('/sponsors')
def sponsors():
    return render_template('testapp/sponsors.html')

@app.route('/competitors/<category>')
def competitorslist(category):

    allowed_categories = ['asp_men', 'asp_wmn', 'fin_men', 'fin_wmn']
    if category not in allowed_categories:
        return render_template('testapp/error.html')
    else:
        pass

    conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    try:
        with conn.cursor() as cursor:
            sql = f"SELECT `id`, `player` from {category} ORDER BY id"
            cursor.execute(sql)
            listed = cursor.fetchall()
            listed = sorted(listed, key=lambda x: (x['id'] is None, x['id']))

    finally:
        conn.close()

    category = categorytranslateToDay(category)

    return render_template('testapp/competitors_list.html', 
                               listed=listed,
                               category=category)

@app.route('/judge/<category>/<problem>')
def judgeselect(category, problem):
    conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    try:
        with conn.cursor() as cursor:
            sql = f"SELECT player from {category}"
            cursor.execute(sql) 
            playerdata = cursor.fetchall()
    finally:
        conn.close()
    print(playerdata)

    player = []
    for i in playerdata:
        name = i['player']
        player.append(name)

    cat_name = categorytranslate(category)
    return render_template('testapp/judgeselect.html', category=category, problem=problem, cat_name=cat_name, player=player)

@app.route('/judge/<category>/<problem>/<player_number>', methods=['GET', 'POST'])
def judgefeed(category, problem, player_number):
    if request.method == 'GET':
        cat_name = categorytranslate(category)

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            with conn.cursor() as cursor:
                if problem == "p1":
                    sql = f"SELECT player, z1, t1 from {category} WHERE id = %s"   
                elif problem == "p2":
                    sql = f"SELECT player, z2, t2 from {category} WHERE id = %s"
                elif problem == "p3":
                    sql = f"SELECT player, z3, t3 from {category} WHERE id = %s"
                elif problem == "p4":
                    sql = f"SELECT player, z4, t4 from {category} WHERE id = %s"
                else:
                    return render_template('testapp/error.html')
                temp = (player_number,)
                cursor.execute(sql, temp) 
                playerdata = cursor.fetchone()
        finally:
            conn.close()

        print(playerdata)

        player_name = playerdata['player']

        if problem == "p1":
            zonegot = playerdata['z1']
            topgot = playerdata['t1']
        elif problem == "p2":
            zonegot = playerdata['z2']
            topgot = playerdata['t2']    
        elif problem == "p3":
            zonegot = playerdata['z3']
            topgot = playerdata['t3']
        elif problem == "p4":
            zonegot = playerdata['z4']
            topgot = playerdata['t4']

        if zonegot == None:
            zonegot = 0
        if topgot == None:
            topgot = 0

        return render_template('testapp/judgefeed.html',category=category, 
                                                        problem=problem, 
                                                        player_name=player_name, 
                                                        player_number=player_number, 
                                                        cat_name=cat_name,
                                                        zonegot=zonegot,
                                                        topgot=topgot)
    
    if request.method == 'POST':
        zone = request.form.get('zone')
        top = request.form.get('top')
        zone_attempt = request.form.get('zone_attempt')
        top_attempt = request.form.get('top_attempt')

        #print(zone, top, zone_attempt, top_attempt)

        if zone == 'on':
            zone_value = zone_attempt
        else:
            zone_value = 0

        if top == 'on':
            top_value = top_attempt
        else:
            top_value = 0

        #print(zone_value, top_value)

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            with conn.cursor() as cursor:
                if problem == "p1":
                    sql = f"UPDATE {category} SET z1 = %s, t1 = %s WHERE id = %s"
                elif problem == "p2":
                    sql = f"UPDATE {category} SET z2 = %s, t2 = %s WHERE id = %s"
                elif problem == "p3":
                    sql = f"UPDATE {category} SET z3 = %s, t3 = %s WHERE id = %s"
                elif problem == "p4":
                    sql = f"UPDATE {category} SET z4 = %s, t4 = %s WHERE id = %s"
                else:
                    return render_template('testapp/error.html')

                temp = (zone_value, top_value, player_number)
                cursor.execute(sql, temp)
                conn.commit()

        finally:
            conn.close()

        return redirect(url_for('judgeselect', category=category, problem=problem))

@app.route('/ranking/<category>')
def ranking(category):
    conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    try:
        with conn.cursor() as cursor:
            sql = f"SELECT * from {category} ORDER BY id"
            cursor.execute(sql)
            category_binary = False
            if category == "f_asp_men":
                category_binary = True
            elif category == "f_asp_wmn":
                category_binary = True
            category = categorytranslateWithBrank(category)
            category = category.replace("\n", "<br>")
            data = cursor.fetchall()
    finally:
        conn.close()
    
    for i in data:
        if i is None:
            continue
        scorecalc(i)
        omitName(i)
    data = sorted(data, key=lambda x: (-x['total'], x['id'] if x['id'] is not None else float('inf')))
    print(data)
    if category_binary == True:
        return render_template('testapp/ranking_asp.html', category=category, data=data)
    else:
        return render_template('testapp/ranking.html', category=category, data=data)


@app.route('/lobby_edit')
def lobby_edit():

    conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cat_list = ["asp_men","asp_wmn","fin_men","fin_wmn"]
    data_list = []

    try:
        for i in cat_list:
            with conn.cursor() as cursor:
                sql = f"SELECT `id`, `player` from {i} ORDER BY id"
                cursor.execute(sql)
                data_list.append(cursor.fetchall())

    finally:
        conn.close()
    
    print(data_list)

    return render_template('testapp/lobby_edit.html', data_list=data_list)


@app.route('/edit/<category>/<id>')
def edit(category, id):
    if request.method == "GET":
        conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='the1',
                        cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            with conn.cursor() as cursor:
                sql = f"SELECT * from {category} where id = %s"
                cursor.execute(sql, id)
                category = categorytranslate(category)
                data = cursor.fetchall()
                data = data[0]
        finally:
            conn.close()
       
        data = scorecalc(data)
        data = noneToBlank(data)  
        return render_template('testapp/edit.html', category=category, data=data)
    
    if request.method == "POST":
        t1, t2 ,t3, t4 = request.form.get('t1'),request.form.get('t2'),request.form.get('t3'),request.form.get('t4')
        z1, z2, z3, z4 = request.form.get('z1'),request.form.get('z2'),request.form.get('z3'),request.form.get('z4')

        conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='the1',
                        cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            with conn.cursor() as cursor:
                sql = f"UPDATE {category} SET t1=%s, t2=%s, t3=%s, t4=%s, z1=%s, z2=%s, z3=%s, z4=%s, where id=%s"
                cursor.execute(sql, t1, t2 ,t3, t4, z1, z2, z3, z4, id)
        finally:
            conn.close()

        return redirect(url_for('lobby_edit'))
 


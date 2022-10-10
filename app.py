from markupsafe import escape
from flask import Flask, render_template, request, url_for, redirect, flash,session
import pymysql
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
showimg_path = './static/read_from_mysql.png'


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register',methods=['GET'])
def register():
    username = request.args.get("username")
    password = request.args.get("password")
    con_password = request.args.get("con_password")

    if not username or not password or not con_password:
        flash('请输入完整的用户名和想要设置的密码')
        return redirect(url_for('login'))
    if password != con_password:
        flash('两次输入的密码不一致！')
        return redirect(url_for('login'))

    conn = pymysql.connect(host="localhost", port=3306, user='zachary', passwd="980226", charset='utf8', db='pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    my_query = f"SELECT * FROM user where usr = %s"
    cursor.execute(my_query, [username])
    res = cursor.fetchall()


    if res:
        flash('用户已经存在! 请登录，或者重新输入用户名！')
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    else:
        my_query = "INSERT INTO user(usr,password) VALUES(%s,%s)"
        cursor.execute(my_query, (username, password))
        conn.commit()
        flash('新用户已注册成功！')
        cursor.close()
        conn.close()
        return redirect(url_for('login'))


@app.route('/loginer',methods=['GET'])
def loginer():
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        flash('请输入完整的用户名和密码!')
        return redirect(url_for('login'))

    conn = pymysql.connect(host="localhost", port=3306, user='zachary', passwd="980226", charset='utf8', db='pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    my_query = "SELECT * FROM user WHERE usr = %s"
    cursor.execute(my_query, [username])
    res = cursor.fetchall()

    if res:
        my_query = "SELECT * FROM user WHERE usr = %s and password = %s"
        cursor.execute(my_query, [username, password])
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        if res:
            # 加上session
            session['login_success'] = 'permission'
            return redirect(url_for('index'))
        else:
            flash('密码错误，请重试!')
            return redirect(url_for('login'))
    else:
        cursor.close()
        conn.close()
        flash('用户名不存在请先注册!')
        return redirect(url_for('login'))



@app.route('/index')
def index():
    permission = session.get('login_success')
    if not permission:
        return redirect(url_for('login'))
    try:
        os.remove(showimg_path)
    except:
        print("No Imgpath")
    return render_template('index.html', res=None, case=None)


@app.route('/patient_mess/search', methods=["GET"])
def search():
    curname = request.args.get("curname")
    if not curname:
        flash('请输入患者姓名进行查询！')
        return redirect(url_for('index'))
    conn = pymysql.connect(host="localhost", port=3306, user='zachary', passwd="980226", charset='utf8', db='pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    my_query = f"SELECT * FROM patient where name = %s"
    cursor.execute(my_query, [curname])
    res = cursor.fetchall()
    cursor.close()
    conn.close()

    if res:
        fout = open(showimg_path, 'wb')
        fout.write(res[0]['img'])
        fout.close()
        return render_template('index.html', res=res[0], case=None)
    else:
        try:
            os.remove(showimg_path)
        finally:
            flash('没有该患者记录！')
            return redirect(url_for('index'))


@app.route('/patient_mess/reset', methods=["GET", "POST"])
def reset():
    try:
        os.remove(showimg_path)
    finally:
        return render_template('index.html', res=None, case=None)


@app.route('/patient_mess/submit', methods=["GET"])
def submit():
    curname = request.args.get("curname")
    curgender = request.args.get("curgender")
    curmechine = "是" if request.args.get("curmechine") == 'on' else "否"
    curmechine_time = request.args.get("curmechine_time")
    curdrug = request.args.get("curdrug")
    curremark = request.args.get("curremark")

    conn = pymysql.connect(host="localhost", port=3306, user='zachary', passwd="980226", charset='utf8', db='pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    my_query = f"SELECT * FROM patient where name = %s"
    cursor.execute(my_query, [curname])
    res = cursor.fetchall()

    if res:
        my_update = f"UPDATE patient SET gender = %s,mechine = %s,mechine_time = %s,drug = %s,remark = %s where name = %s"
        cursor.execute(my_update, (curgender, curmechine, curmechine_time, curdrug, curremark, curname))
        conn.commit()
        print("success! 更新成功！")
        flash('提交成功! 已经更新治疗方案！')
        cursor.close()
        conn.close()

    else:
        print("错误！ 查无此人")
        flash("没有该患者记录！")
    return redirect(url_for('index'))


@app.route('/patient_mess/match', methods=["GET"])
def match():
    curname = request.args.get("curname")

    conn = pymysql.connect(host="localhost", port=3306, user='zachary', passwd="980226", charset='utf8', db='pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    cur_query = f"SELECT * FROM patient where name = %s"
    cursor.execute(cur_query, [curname])
    res = cursor.fetchall()

    if res:
        curpainlevel = res[0]['painlevel']
        case_query = f"SELECT gender,painlevel,mechine,drug,mechine_time,remark FROM patient where painlevel = %s and name != %s"
        cursor.execute(case_query, [curpainlevel, curname])
        case = cursor.fetchmany(3)
        cursor.close()
        conn.close()

        fout = open(showimg_path, 'wb')
        fout.write(res[0]['img'])
        fout.close()
        return render_template('index.html', res=res[0], case=case)
    else:
        try:
            os.remove(showimg_path)
        finally:
            flash('没有该患者记录！')
            return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

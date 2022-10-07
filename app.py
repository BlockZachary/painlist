from markupsafe import escape
from flask import Flask, render_template, request, url_for, redirect, flash
import pymysql
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'

@app.route('/index')
def index():
    return render_template('index.html',res = None)

@app.route('/index/<name>')
def rname(name):
    return f'User:{escape(name)}'

@app.route('/patient_mess/search',methods=["GET"])
def search():
    curname = request.args.get("curname")
    print(curname)
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='zachary', passwd="980226", charset='utf8', db='pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    my_query = f"SELECT * FROM patient where name = %s"
    cursor.execute(my_query, [curname])
    res = cursor.fetchall()

    showimg_path = './static/read_from_mysql.png'
    if res:
        fout = open(showimg_path, 'wb')
        fout.write(res[0]['img'])
        fout.close()
        return render_template('index.html',res=res[0])
    else:
        try:
            os.remove(showimg_path)
        finally:
            flash('No this patient name')
            return redirect(url_for('index')) 


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

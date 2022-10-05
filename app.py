from flask import Flask
from markupsafe import escape

app = Flask(__name__)

@app.route('/index')
def hello():
    return 'Welcome to My Watchlist!'

@app.route('/index/<name>')
def rname(name):
    return f'User:{escape(name)}'


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

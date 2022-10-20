from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(12), nullable=False)
    password = db.Column(db.String(30), nullable=False)
  
@app.route("/" ,methods=['GET', 'POST'])
def hello_world():
    return render_template("index.html")
@app.route('/create')
def create():
    return render_template('registered.html')
@app.route("/signin")
def hello():
    return "<a>会員登録してください</a>"
if __name__=="__main__":
    app.run(host="0.0.0.0")
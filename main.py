from asyncio.windows_events import NULL
import datetime
from flask import Flask, render_template, request, redirect, session
import MySQLdb
import html
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from datetime import timedelta
import secrets
def connect():
        con = MySQLdb.connect(
                host="localhost",
                user="root",
                passwd="Seishiro0126",
                db="test",
                use_unicode=True,
                charset="utf8")
        return con

app =Flask(__name__)
app.secret_key=secrets.token_urlsafe(16)
app.permanent_session_lifetime=timedelta(minutes=60)


@app.route("/" ,methods=['GET', 'POST'])
def hello_world():
    return redirect("loginn")

@app.route("/create",methods=["GET","POST"])
def make():
    if request.method =="GET":
        return render_template("registered.html")
    elif request.method =="POST":
        ID=request.form["ID"]
        name=request.form["name"]
        password=request.form["password"]
        sex=request.form["sex"]
        age = request.form["age"]
        job=request.form["job"]
        hashpass=gph(password)
        con = connect()
        cur = con.cursor()
        cur.execute("""
        SELECT * FROM list WHERE name=%(name)s
        """,{"name":name})
        data=[]
        for row in cur:
            data.append(row)
        if len(data)!=0:
            return render_template("registered.html",msg="既に存在しているメールアドレスです。")
        con.commit()
        con.close()
        con = connect()
        cur = con.cursor()
        cur.execute("""
        INSERT INTO list
        (ID,name,password,sex,age,job)
        VALUES(%(ID)s,%(name)s,%(hashpass)s,%(sex)s,%(age)s,%(job)s)""",
        {"ID":ID,"name":name,"hashpass":hashpass,"sex":sex,"age":age,"job":job})
        con.commit()
        con.close()
        con = connect()
        cur = con.cursor()
        cur.execute("""
        INSERT INTO usagee
        (ID,name,time,money,job)
        VALUES(%(ID)s,%(name)s,%(time)s,%(money)s,%(job)s)""",
        {"ID":ID, "name":name,"time":str(datetime.datetime.today()), "money":0,"job":job})
        con.commit()
        con.close()
        con = connect()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO list2
            (ID,name,income,sum,updatetime,usagee)
            VALUES(%(ID)s,%(name)s,%(income)s,%(sum)s,%(updatetime)s,%(usagee)s)""",
            {"ID":ID,"name":name,"income":0,"sum":0,"updatetime":str(datetime.datetime.today()),"usagee":"使い道"})
        con.commit()
        con.close()
        return render_template("infoo.html",ID=ID,name=name,password=password,sex=sex,age=age,job=job)

@app.route("/loginn", methods=["GET","POST"])
def login():
    if request.method =="GET":
        session.clear()
        return render_template("loginn.html")
    elif request.method =="POST":
        name=html.escape(request.form["name"])
        password=html.escape(request.form["password"])
        con = connect()
        cur = con.cursor()
        cur.execute("""
                    SELECT password,name,sex,age,job,ID
                    FROM list 
                    WHERE name=%(name)s
                    """,{"name":name})
        data=[]
        for row in cur:
            data.append([row[0],row[1],row[2],row[3],row[4],row[5]])
        if len(data)==0:
            con.close()
            return render_template("loginn.html",msg="IDが間違っています")
        if cph(data[0][0],password):
            session["ID"]=data[0][5]
            session["name"]=data[0][1]
            session["sex"]=data[0][2]
            session["age"]=data[0][3]
            session["job"]=data[0][4]
            con.close()
            return redirect("home")
        else:
            con.close()
            return render_template("loginn.html",msg="パスワードが間違っています。")

@app.route("/home")
def home():
    if "name" in session:
        return render_template("successs.html",ID=html.escape(session["ID"]),name=html.escape(session["name"]),age=html.escape(session["age"]),sex=html.escape(session["sex"]),job=html.escape(session["job"]))
    else:
        return redirect("loginn")

@app.route("/usage" ,methods=["GET","POST"])
def usage():
    if request.method =="GET":
        return render_template("mypage3.html")
    elif request.method =="POST":
        income = html.escape(request.form["income"])
        usagee = html.escape(request.form["usagee"])
        income = int(income)
        if "ID" in session:
            ID = session["ID"]
            name=session["name"]
            con = connect()
            cur = con.cursor()
            cur.execute("""
            SELECT sum FROM list2
            WHERE ID=%(ID)s""",{"ID":ID})
            data=[]
            for row in cur:
                data.append(row)
            print(data)
            summ=data[len(data)-1][0]
            con.commit()
            con.close()
            summ=summ+income
            con = connect()
            cur = con.cursor()
            cur.execute("""
            INSERT INTO list2
            (ID,name,income,sum,updatetime,usagee)
            VALUES(%(ID)s,%(name)s,%(income)s,%(sum)s,%(updatetime)s,%(usagee)s)""",
            {"ID":ID,"name":name,"income":income,"sum":summ,"updatetime":str(datetime.datetime.today()),"usagee":usagee})
            con.commit()
            con.close()
            con = connect()
            cur = con.cursor()
            cur.execute("""
            UPDATE usagee
            SET money=%(summ)s
            WHERE ID=%(ID)s""",{"summ":summ, "ID":ID})
            con.commit()
            con.close()
            return render_template("mypage.html")
    else:
        return redirect("login")

@app.route("/rireki")
def rireki():
    if "name" in session:
        # セッションに記録した情報を出力
        ID=session["ID"]
        con = connect()
        cur = con.cursor()
        cur.execute("""
        SELECT income,sum,updatetime,usagee
        FROM list2
        WHERE ID=%(ID)s
        ORDER BY updatetime DESC""",{"ID":ID})
        res = "<table align=\"center\" border=\"1\">\n"
        res = res + "\t<tr><th>&nbsp;日時&nbsp;</th><th>&nbsp;支出入金額&nbsp;</th><th>&nbsp;合計&nbsp;</th><th>&nbsp;使用用途&nbsp;</th></tr>\n"
        for row in cur:
            income = row[0]
            sum = row[1]
            updatetime = row[2]
            usagee = row[3]
            res = res + "<tr><th>" +str(updatetime)+"</th><th>" +str(income)+"</th><th>" +str(sum)+"</th><th>"+str(usagee) +"</th></tr>\n"
        con.commit()
        con.close()
        res = res + "</table>"
        return render_template("kakonorireki.html",res=res)
    else:
        return redirect("loginn")
@app.route("/getapi",methods=["GET","POST"])
def root_page():
    if request.method == "GET":
        return render_template("getapi.html")
    elif request.method == "POST":
        job2 = html.escape(request.form["job2"])
                
        
        con = connect()
        cur = con.cursor()
        cur.execute("""
            SELECT name,money,job
            FROM usagee
            WHERE job=%(job)s
            ORDER BY money DESC
            """,{"job":job2})
        res = {}
        tmpa = []
        rank = 1
        for row in cur:
            dic = {}
            dic["rank"] = rank
            dic["name"] = row[0]
            dic["money"] = row[1]
            dic["job"] = row[2]
            tmpa.append(dic)
            rank += 1
        res["content"] = tmpa
        con.commit()
        con.close()
        return render_template("webapi.html",res=res)


if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")
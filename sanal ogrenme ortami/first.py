from flask import Flask, render_template, url_for, flash, redirect, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os
from functools import wraps


class Regester(Form):
    name = StringField("", validators=[
                       validators.Length(min=3, max=25)], render_kw={"placeholder": "write ur name"})
    username = StringField("", validators=[
                           validators.Length(min=3, max=25)], render_kw={"placeholder": "write ur username"})
    email = StringField("", validators=[
                        validators.Email(message="sign with valid email")], render_kw={"placeholder": "write ur email"})
    password = PasswordField("", validators=[
        validators.DataRequired(message="put password "),
        validators.EqualTo(fieldname="confirm", message="password dont equal")

    ],
        render_kw={"placeholder": "write ur password"})
    confirm = PasswordField("", render_kw={
                            "placeholder": "write ur password"})


class loginform(Form):
    username = StringField(label="", render_kw={
                           "placeholder": "write your user name"})
    password = PasswordField("", validators=[validators.DataRequired(
        message="put password")], render_kw={"placeholder": "write your password"})

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else :
            flash("You have to sign in :)","danger")
            return  redirect(url_for("login2"))
    return decorated_function

class Article_Form(Form):
    title = StringField("Name of article",validators=[validators.Length(min = 5)],render_kw={"placeholder":"add the name"})
    contant = TextAreaField("contant of article",validators=[validators.Length(min = 5)])

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "lordhadi"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

app.secret_key = "lord1hadi"
mysql = MySQL(app)

pic = os.path.join("static")
app.config["UPLOAD_FOLDER"] = pic


@app.route("/")
def ind():
    return render_template("index.html")


@app.route("/about")
def about():
    pic1 = os.path.join(app.config["UPLOAD_FOLDER"], "hadi.jpg")
    return render_template("about.html", user=pic1)


@app.route("/sign up", methods=["GET", "POST"])
def sign_up():
    form = Regester(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        insert = "Insert into user(name , username , email , password) VALUES (%s,%s,%s,%s)"

        cursor.execute(insert, (name, username, email, password))
        mysql.connection.commit()
        cursor.close()
        flash("you have successfully signed in ", "success")
        return redirect(url_for("login2"))
    else:

        return render_template("regster.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login2():
    form = loginform(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entred = form.password.data

        cursor = mysql.connection.cursor()

        get12 = "Select * From user where username =%s"

        result = cursor.execute(get12, (username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entred, real_password):
                flash("you have successfully logged in", "success")
                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("ind"))
            else:
                flash("Password wrong", "danger")
                return redirect(url_for("login2"))
        else:
            flash("username is wrong ", "danger")
            return redirect(url_for("login2"))
    else:

        return render_template("login.html", form=form)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("ind"))
@app.route("/Dashboard")
@login_required
def Dashboard():
    cursor = mysql.connection.cursor()
    get = "Select * from article Where author=%s "
    username = session["username"]
    result = cursor.execute(get,(username,))
    if result >0 :
        articles = cursor.fetchall()
        return render_template("Dashboard.html",articles=articles)
    else:
        return render_template("Dashboard.html")

@app.route("/add_article",methods = ["GET","POST"])
@login_required
def Add_article():
    form = Article_Form(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        contant = form.contant.data
        cursor = mysql.connection.cursor()

        insert = "Insert into article(title,author,contant)VALUES(%s,%s,%s)"

        cursor.execute(insert,(title,session["username"],contant))
        mysql.connection.commit()

        cursor.close()


        flash("article successfully added","success")
        return redirect(url_for("Dashboard"))


    return render_template("add_article.html",form = form)

@app.route("/Articles")
def Show_artilcles():
    cursor = mysql.connection.cursor()
    show = "Select * From article"

    result = cursor.execute(show)

    if result >0 :
        articles = cursor.fetchall()

        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")

@app.route("/article/<string:id>")
def article_id(id):
     cursor = mysql.connection.cursor()
     sql = "Select * From article where id= %s"
     result = cursor.execute(sql,(id,))
     if result > 0 :
         article = cursor.fetchone()
         return render_template("article.html",article = article)
     else:
         return render_template("article.html")

@app.route("/delete/<string:id>")
@login_required 
def delete_article(id):
    cursor = mysql.connection.cursor()
    sql = "Select * from article where id = %s and author = %s"
    result = cursor.execute(sql,(id,session["username"]))
    if result >0 :
        sql2= "Delete from article where id = %s"
        cursor.execute(sql2,(id,))

        mysql.connection.commit()
        flash("your article deleted","danger")

        return redirect(url_for("Dashboard"))

    else:
        flash("You can just delete your article","danger")
    
        return redirect(url_for("Dashboard"))
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
    if request.method =="GET":
        cursor = mysql.connection.cursor()
        sql= "Select * from article where id=%s and author = %s"
        result = cursor.execute(sql,(id,session["username"]))
        if result == 0:
            flash("There is no article","danger")
            return redirect(url_for("ind"))
        else:
            article = cursor.fetchone()
            form = Article_Form() 
            form.title.data = article["title"]
            form.contant.data = article["contant"]
            return render_template("update.html" , form= form)
    else:
        form = Article_Form(request.form)
        newTitle = form.title.data
        newContant = form.contant.data

        sql = "Update article Set title =%s ,contant = %s where id =%s"
        cursor = mysql.connection.cursor()
        cursor.execute(sql,(newTitle,newContant,id))
        mysql.connection.commit()
        flash("Updated ","success")

        return redirect(url_for("Dashboard"))

@app.route("/search",methods=["GET","POST"])
def Search():
    if request.method=="GET":
        return redirect(url_for("ind"))
    else:
        kw=request.form.get("Search_input")
        cursor = mysql.connection.cursor()
        sql = "Select *from article where title like '%"+kw+"%'"
        result = cursor.execute(sql)
        if result == 0 :
            flash("not found !!!","warning")
            return redirect(url_for("Show_artilcles"))
        else :
            articles = cursor.fetchall()
            return render_template("/articles.html",articles =articles )





if __name__ == '__main__':
    app.run(debug=True)

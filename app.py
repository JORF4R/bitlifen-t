# -*- coding: utf-8 -*-

import datetime
import random
from flask import Flask, render_template
from flask import (
    Flask,
    config,
    render_template,
    request,
    flash,
    json,
    send_file,
    session,
    jsonify,
    redirect,
    url_for,
    send_from_directory,
)
import os
from flask_mail import Mail, Message
import bcrypt
from flask_mysqldb import MySQL
import jwt


app = Flask(__name__)
app.config["SECRET_KEY"] = "bitlifent"
app.config['TIMEZONE'] = 'America/Bogota'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Jorfar2003"
app.config["MYSQL_DB"] = "bitlifent"

app.config["UPLOAD_FOLDER"] = "static/users/"

mysql = MySQL(app)

semilla = bcrypt.gensalt()
app.config['MAIL_SERVER']='smtp.gmail.com'

app.config['MAIL_USERNAME'] = 'jorfar03@gmail.com'
app.config['MAIL_PASSWORD'] = 'chgq lfrh ilph hrok'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True



# Inicializar la extensión Mail
mail = Mail(app)

elecionesin=["naces blanco","naces negro"]
# Ruta principal
@app.route('/')
def home():
    if 'usuario' not in session:
       
        return redirect("/login")
    else:
      
        return render_template("index.html")

@app.route('/login')
def log():
    return render_template('login.html')
@app.route('/singup')
def singup():
    return render_template('singup.html')
@app.route('/logout')
def salir():
    session.clear()
    return redirect(url_for('home'))

@app.route("/addusers", methods=["POST", "GET"])
def addusers():
    if request.method == "GET":
        
        return render_template("index.html")
    else:
        if request.method == "POST":
            
            email = request.form["email"]
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            username = request.form["username"]
            password = request.form["clave"]
            otraclave = request.form["otraclave"]
            Photo = "1.png"
            State = "Inactivo"
            nacimiento= request.form["fechan"]
            ultimaelec= random.choice(elecionesin)
            nivel =0
            historia=""
            DateCreate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          
            
            link = mysql.connection.cursor()
            link.execute("SELECT * FROM usuarios WHERE username=%s", [username])
            usuarioo = link.fetchone()
            link.execute("SELECT * FROM usuarios WHERE email=%s", [email])
            maiilusuario =link.fetchone()
            print(usuarioo)
            if usuarioo!=None:
                print("holaaa")
                flash("El usuario ya existe", "alert-warning")
                return redirect("/singup")
            if maiilusuario!=None:
                flash("El email ya existe", "alert-warning")
                return redirect("/singup")
            if password != otraclave:
                flash("La confirmación del Password no coincide", "alert-warning")
                return redirect("/singup")
            
            password_encode = password.encode("utf-8")
            password_encriptado = bcrypt.hashpw(password_encode, semilla)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (nombre, apellido, email, username, password, photo, state, nacimiento, ultimaelec, nivel, historia, dateCreate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (nombre, apellido, email, username, password_encriptado, Photo, State, nacimiento, ultimaelec, nivel, historia, DateCreate))
            
            mysql.connection.commit()
            cur.close()
            link.close()
            print("holaaa")
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
            os.makedirs(user_folder)

            token_validation = jwt.encode(
    {
        "user": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
    },
    app.config["SECRET_KEY"],
    algorithm="HS256"
)

            msg = Message(
                "Validación usuario bitlifent",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email],
            )
            msg.html = render_template(
                "email.html",
                email=username,
                username=nombre+" " +apellido,
                token_validation=token_validation,
            )

            mail.send(msg)

          

            flash(
                "Usuario registrado correctamente, se ha enviado un correo electrónico de confirmación"
            )
            return redirect('/singup')

    return render_template("singup.html")



@app.route("/autenticar", methods=["POST", "GET"])
def autenticar():
    if request.method == "GET":
        if "usuario" in session:   
            return render_template("index.html")
        else:
            return render_template("login.html")
    else:
   
        if request.method == "POST":
            username = request.form["username"]
            Password = request.form["clave"]
            password_encode = Password.encode("utf-8")
            link = mysql.connection.cursor()
            sql = "SELECT * FROM usuarios WHERE username = %s"
            link.execute(sql, [username])
            usuario = link.fetchone()
            link.close()
            if usuario != None:
                password_encriptado_encode = usuario[5].encode()
                if bcrypt.checkpw(password_encode, password_encriptado_encode):
                    if usuario[7] == "Inactivo":
                        flash("correo sin autenticar", "alert-warning")
                        return redirect("/login")
                    # Registra la sesión
                    session["nombres"] = usuario[1]
                    session["usuario"] = usuario[4]
                   
                    session['foto'] = usuario[6]
                    session['nivel'] = usuario[10]
                    return redirect("/")
                else:
                    flash("El password no es correcto", "alert-warning")
                    return redirect("/login")
            else:
                flash("Usuario no existe", "alert-warning")
                return redirect("/login")




@app.route("/verification_email/<string:token_verified>", methods=["GET"])
def verification_email(token_verified):
    data = jwt.decode(token_verified, options={"verify_signature": False})
    Email = data["user"]
    link = mysql.connection.cursor()
    link.execute("SELECT Email FROM usuarios WHERE Email=%s", [Email])
    usuario = link.fetchone()
    if usuario != None:
        link.execute("UPDATE usuarios SET State=%s WHERE Email=%s", ("Activo", Email))
        mysql.connection.commit()
        flash(
            "Registro completado, ingresa con tu usuario y contraseña y tendrás acceso a nuestra plataforma",
            "alert-warning",
        )
        return redirect("/login")
    else:
        flash("Token no válido", "alert-warning")
        return redirect("/login")







if __name__ == '__main__':
    app.run(debug=True)


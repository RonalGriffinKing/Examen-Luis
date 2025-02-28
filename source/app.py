from flask import Flask, render_template,request,redirect,jsonify
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os,random

load_dotenv()





app = Flask(__name__)
app.config['MONGO_URI']='mongodb://127.0.0.1:27017/Mimascota'

app.config['SECRET_KEY']=os.urandom(24)


jwt=JWTManager(app)


mongo=PyMongo(app)




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/Registrarme",methods=['GET','POST'])
def Registrarme():  
    if request.method=='POST':
        correo=request.form.get('correo')
        contra=request.form.get('contra')
        nombre=request.form.get('usuario')
        if not correo or not contra or not nombre:
            return render_template("Registro.html",messages='No puede estar vacio'),400
        else:
            if mongo.db.usuarios.find_one({'correo':correo}):
                return render_template("Registro.html",messages='Correo ya en uso.'),400
            else:   
                user=mongo.db.usuarios.find_one({'correo':correo})
                clave=generate_password_hash(contra)
                mongo.db.usuarios.insert_one({'correo':correo,'contra':clave,'nombre':nombre,'rol':'normal','visitas':'1'})
                return render_template("Registro.html",messages='Correcto.'),201
    return render_template("Registro.html")


@app.route("/Login",methods=['GET','POST'])
def Login():
    if request.method=='POST':
        correo=request.form.get('correo')
        contra=request.form.get('contra')
        if not correo or not contra:
            return render_template("Login.html",messages='No puede estar vacio'),400
        else:
            usuario=mongo.db.usuarios.find_one({'correo':correo})
            if usuario:
                if check_password_hash(usuario['contra'],contra):
                    query={'correo':correo}
                    visitas=int(usuario.get('visitas',0)) + 1
                    actualizacion={ "$set": { 'visitas':visitas } }
                    mongo.db.usuarios.update_one(query,actualizacion)
                    usuario=mongo.db.usuarios.find_one({'correo':correo})

    
                    acceso=create_access_token(identity=correo)
                    return render_template("Perfil.html",messages='Bienvenido',datos=usuario,access_token=acceso),201
                    
                else:
                    return render_template("Login.html",messages='Contraseña incorrecta.'),400
    return render_template("Login.html")

@app.route("/Perfil")
@jwt_required()
def Perfil():
   
    return render_template("Perfil.html")


@app.route("/Tienda")
def Tienda():
    
  
    productos=list(mongo.db.productos.find())
    return render_template("Tienda.html",productosl=productos)


def crear():
    productos=[
        {'Nombre':'Shampo','img':'https://www.kiwoko.com/dw/image/v2/BDLQ_PRD/on/demandware.static/-/Sites-kiwoko-master-catalog/default/dw9382c014/images/Cunipic_Champ%C3%BA_de_Jojoba_para_hurones_CUNCHAJO_M.jpg?sw=780&sh=780&sm=fit&q=85','Precio':'20','Descripcion':'El mejor que existe'},
        {'Nombre':'Comedero','img':'https://media.zooplus.com/bilder/2/400/25787_PLA_Trixie_Keramiknapf_Hamster_80ml_2.jpg','Precio':'15','Descripcion':'Muy util'},
        {'Nombre':'Jaula','img':'https://m.media-amazon.com/images/I/71aID6ov96L.__AC_SX300_SY300_QL70_ML2_.jpg','Precio':'5','Descripcion':'Te encantara'},
        ]
    if mongo.db.usuarios.find_one({'correo':'luis@gmail.com'}):
        print('Usuario ya esta en bd')
    else:   
        correo='luis@gmail.com'
        nombre='luis'
        contra='1234567'
        clave=generate_password_hash(contra)
        mongo.db.usuarios.insert_one({'correo':correo,'contra':clave,'nombre':nombre,'rol':'Admin','visitas':'1'})
        mongo.db.productos.insert_many(productos)
        print('Correo:Luis@gmail.com contrasela:1234567')

crear()

if __name__ == "__main__":
    app.run(debug=True)

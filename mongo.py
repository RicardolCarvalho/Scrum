from flask import Flask, request, Response
from flask_pymongo import PyMongo
from api_gpt_g1 import post_todas_noticias
from api_gpt_uol import post_todas_noticias_2
from urllib.parse import unquote
from login import hash_password, requires_auth

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@projeficaz.fsc9tus.mongodb.net/TGproj"
mongo = PyMongo(app, tlsAllowInvalidCertificates=True, tls=True)

@app.route('/')
def home():
    return {"msg": 'rota publica'}

@app.route('/secret')
@requires_auth
def secret():
    return {"msg": 'rota secreta'}


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    filtro = {'email': data['email'], 'senha': data['senha']}
    projecao = {'_id': 0}
    usuario = mongo.db.usuarios.find_one(filtro, projecao)
    if usuario is None:
        return {"erro": "usuário e/ou senha inválidos"}, 400
    return {"id": usuario['id']}, 200

@app.route('/usuarios', methods=['GET'])
def get_users():    
    filtro = {}
    projecao = {'_id': 0}
    dados_user = mongo.db.usuarios.find(filtro, projecao)
    lista_user = list(dados_user)
    return {'usuarios': lista_user}, 200

@app.route('/usuarios', methods=['POST'])
def post_users():
    filtro = {}
    projecao = {'_id': 0}
    data = request.json
    if data['nome'] == " " or data['nome'] == "":
        return {"erro": "nome é obrigatório"}, 400
    if data['email'] == " " or data['email'] == "" or "@" not in data['email']:
        return {"erro": "email é obrigatório"}, 400
    if data['senha'] == " " or data['senha'] == "":
        return {"erro": "senha é obrigatório"}, 400
    if data['cpf'] == " " or data['cpf'] == "":
        return {"erro": "cpf é obrigatório"}, 400
    
    idss = mongo.db.ids.find_one()
    data['id'] = idss['id_user']
    mongo.db.ids.update_one({}, {'$inc': {'id_user': 1}})
    
    dados_user = mongo.db.usuarios.find(filtro, projecao)
    lista_user = list(dados_user)
    for user in lista_user:
        if data['cpf'] == user['cpf']:
            return {"erro": "cpf já cadastrado"}, 400
        
    hashed_password = hash_password(data['senha'])
    user_data = {'id': data['id'], 'nome': data['nome'], 'email': data['email'], 'senha': hashed_password, 'cpf': data['cpf']}

    result = mongo.db.usuarios.insert_one(user_data)
    return {"id": str(result.inserted_id)}, 201

@app.route('/usuarios/<id>', methods=['GET'])
def get_user(id):
    filtro = {'id':id}
    projecao = {'_id': 0}
    dados_user = mongo.db.usuarios.find_one(filtro, projecao)
    return dados_user, 200

@app.route('/usuarios/<id>', methods=['PUT'])
def put_user(id):
    filtro = {"id":id}
    projecao = {"_id": 0} 
    data = request.json
    usuario_existente = mongo.db.usuarios.find_one(filtro, projecao)
    if usuario_existente is None:
        return {"erro": "usuário não encontrado"}, 404
    mongo.db.usuarios.update_one(filtro, {"$set": data})
    return {"mensagem": "alteração realizada com sucesso"}, 200

@app.route('/usuarios/<id>', methods=['DELETE'])
def delete_user(id):
    filtro ={"id": id}
    projecao = {'_id': 0}
    usuario_existente = mongo.db.usuarios.find_one(filtro, projecao)
    if usuario_existente is None:
        return {"erro": "usuário não encontrado"}, 404
    else:
        mongo.db.usuarios.delete_one(filtro)
    
    return {"mensagem": "usuário deletado com sucesso"}, 200

#-------------------------------------------------------------------------------

@app.route('/noticias', methods=['GET'])
def get_news():
    filtro = {}
    projecao = {'_id': 0}
    dados_news = mongo.db.noticias.find(filtro, projecao)
    lista_news = list(dados_news)
    return {'noticias': lista_news}, 200

@app.route('/noticias', methods=['POST'])
def post_news():
    post_todas_noticias()
    post_todas_noticias_2()
    

@app.route('/noticias/<titulo>', methods=['GET'])
def get_new(titulo):
    titulo = unquote(titulo)
    filtro = {'titulo': titulo}
    projecao = {'_id': 0}
    dados_news = mongo.db.noticias.find_one(filtro, projecao)
    return dados_news, 200

@app.route('/noticias/<titulo>', methods=['DELETE'])
def delete_new(titulo):
    titulo = unquote(titulo)
    filtro ={"titulo": titulo}
    projecao = {'_id': 0}
    noticia_existente = mongo.db.noticias.find_one(filtro, projecao)
    if noticia_existente is None:
        return {"erro": "notícia não encontrada"}, 404
    else:
        mongo.db.noticias.delete_one(filtro)
    
    return {"mensagem": "notícia deletada com sucesso"}, 200


@app.route('/noticias/<titulo>', methods=['PUT'])
def put_new(titulo):

    titulo = unquote(titulo)
    filtro = {"titulo": titulo}    
    projecao = {"_id": 0} 
    data = request.json


    noticia_existente = mongo.db.noticias.find_one(filtro, projecao)


    if noticia_existente is None:
        return {"erro": "notícia não encontrada"}, 404
    
    mongo.db.noticias.update_one(filtro, {"$set": data})
    return {"mensagem": "alteração realizada com sucesso"}, 200

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, redirect, session, url_for, render_template,jsonify
from configAuth import AuthConfig
import uuid
import flask_redis
import requests
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object(AuthConfig)
db = SQLAlchemy()
db.init_app(app)
redis_client = flask_redis.FlaskRedis(app)



class Client(db.Model):
    __tablename__="client"
    id = db.Column(db.Integer, primary_key=True)
    _client_secret = db.Column(db.String(255))
    _redirect_url = db.Column(db.String(255))
    @property
    def client_secret(self):
        return self._client_secret
    @property
    def redirect_url(self):
        return self._redirect_url
    @client_secret.setter
    def client_secret(self, cs):
        self._client_secret = cs
    @redirect_url.setter
    def redirect_url(self, ru):
        self._redirect_url = ru
    
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column(db.String(255),unique=True)
    _password = db.Column(db.String(255))
    @property
    def username(self):
        return self._username
    @property
    def password(self):
        return self._password
    @username.setter
    def username(self, un):
        self._username = un
    @password.setter
    def password(self, pwd):
        self._password = pwd
with app.app_context():
    db.create_all()


@app.route("/registerApplication", methods=['POST'])
def registerApplication():
    print("registeringApp")
    client = Client(client_secret=str(uuid.uuid4()), redirect_url=request.form['redirect_url'])
    db.session.add(client)
    db.session.commit()
    return jsonify({
            "clientId": client.id,
            "clientSecret":client.client_secret
        }),200

@app.route("/loginUI")
def loginUI():
    # 获取clientId请求参数
    cid = request.args.get("cid")
    csc = request.args.get("csc")
    return render_template('login.html',clientId=cid,clientSecret=csc)

    
@app.route("/login",methods=['POST'])
def login():
    print(request.method)
    username = request.form['username']
    password = request.form['password']
    print(username)
    print(password)
    clientId = request.args.get('clientId')
    clientSecret = request.args.get('clientSecret')
    # 将clientId转为integer类型
    clientId = int(clientId)
    client = Client.query.filter_by(id=clientId).first()
    if(clientId==None):
        return "Application Not Registerd",401
    elif clientSecret!=client.client_secret:
        return "Invalid clientSecret",401
    user = User.query.filter_by(_username=username).first()
    if user is None:
        return "No Such User",401
    elif(user.password==password):
        code = str(uuid.uuid4())
        token = str(uuid.uuid4())
        redis_client.set(code,token)
        res = requests.post(f"{client.redirect_url}/callback?code={code}")
        if(res.status_code==200):
            return redirect(f"{client.redirect_url}")
        else:
            return "Invalid Credentials",401
    else:
        return "Invalid Credentials",401
@app.route("/token")
def token():
    code = request.args.get('code')
    if(code==None):
        return "Bad Requests",400
    else:
        code = redis_client.get(code)
        if(code==None):
            return "Token Not Exist",401
        return jsonify({ 
        "authtoken":  code.decode()
            }),200
    return "Invalid Credentials",401
    
@app.route("/resource")
def resource():
    if request.headers.get('Authorization') is None:
        return "No Authorization Header",401
    token = request.headers.get('Authorization').split(' ')[1]
    keys = redis_client.keys("*")
    print(keys)
    if(keys == None):
        return "No Token Found",401
    for key in keys:
        if redis_client.get(key).decode() == token:
            return "A片网站123.cc",200
    
    return "Unauthorized",401
@app.route("/registerUser",methods=['POST'])
def registerUser():
    try:
        user = User(username=request.json['username'],password=request.json['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "userId": user.id
        }),200
    except Exception as e:
        return str(e),500
@app.route("/")
def index():
    return render_template('templates/index.html')

    

if __name__ == "__main__":
    app.run(debug=True,port=5001)
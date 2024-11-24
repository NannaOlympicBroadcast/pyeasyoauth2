from flask import Flask, request, redirect, url_for, render_template,g
from config import Config
import requests
app = Flask(__name__)
app.secret_key="sk-520131411451410086"
app.config.from_object(Config)
import os
if os.path.exists("token.txt"):
    os.remove("token.txt")


def save_token(token):
    with open("token.txt","w") as f:
        f.write(token)
    pass

def get_token():
    token = ""
    with open("token.txt","r") as f:
        token = f.read()
    return token

@app.before_request
def before_request():
    g.token = ""
@app.route("/login")
def login():
    CID = request.args.get("cid")
    CCS = request.args.get("ccs")
    if CID == None or CCS == None:
        CID = Config.CLIENT_ID
        CCS = Config.CLIENT_SECRET
    return redirect(Config.THIRD_PARTY_LOGIN_URL+f"?cid={CID}&csc={CCS}")
@app.route("/callback",methods=["POST"])
def callback():
    code = request.args.get("code")
    if code == None:
        return "Bad Request",400
    else:
        tokenRes = requests.get(Config.THIRD_PARTY_TOKEN_URL+"?code="+code)
        if tokenRes.status_code==200:
            save_token(tokenRes.json().get("authtoken"))
            return "OK",200
        else:
            return "获取token失败",500
@app.route("/")
def hello():
    token = get_token()
    if token == None or token == "":
        return redirect(f'http://{Config.APP_IP}/login?cid={Config.CLIENT_ID}&csc={Config.CLIENT_SECRET}')
    else:
        res = requests.get(Config.THIRD_PARTY_RESOURCE_URL,headers={
            "Authorization":"Bearer "+token
        }) 
        if res.status_code!= 200:
            return "获取资源失败",404
        return res.text
save_token("")
Flask.run(app)
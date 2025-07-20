from bcrypt import gensalt, hashpw
from flask import Flask, redirect, render_template, request, session
from secrets import token_bytes
from string import ascii_lowercase
from time import time


app = Flask(__name__)
app.secret_key = token_bytes(16)
pw_hash = b"$2b$12$TlDpPzihBCfMvQylze2t4um3vZ9YbbGuOn46ay7xLhO2wK0hQKT7."
pw_salt = b"$2b$12$TlDpPzihBCfMvQylze2t4u"

active = {}
allowed = ascii_lowercase
timeout = 60
id_len = 6
max_content_len = 10**5 # max 100 kb
max_active = 100  # 100 * 100kb = 10 Mb

@app.route("/")
def index():
	return "submit id like GET /abcdef create and read requests and POST /abcdef to send data\n"


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login")
	
	pw = request.form.get("password").encode()
	if hashpw(pw, pw_salt) == pw_hash:
		session["ok"] = True
		return redirect("/")

	return redirect("/login")


@app.route("/<id>", methods=["GET", "POST"])
def catch(id):
	if "ok" not in session:
		return redirect("/login")

	# remove old ids
	global active
	active = {key:val for key,val in active.items() if (val["time"] + timeout) > time()}

	if request.method == "GET":
		if id in active:
			if "req" in active[id]:
				return active[id]["req"]
			return "no requests yet\n"
		if id and len(id) == 6 and all(c in allowed for c in id):
			active[id] = {}
			active[id]["time"] = int(time())
			return f"activated {id} until {int(time()) + timeout}\n"
		return "invalid id\n", 400

	if request.method == "POST":
		if request.content_length > max_content_len:
			return "request too large\n", 400
		if len(active) > max_active:
			return "server busy\n", 429
		if id not in active:
			return "bad id\n", 400

		active[id]["req"] = str(request.headers).encode() + request.get_data() + b"\n"
		return "caught\n"


# debug
if __name__ == "__main__":
	app.run("127.0.0.1", 9002)

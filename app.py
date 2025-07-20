from bcrypt import gensalt, hashpw
from flask import Flask, redirect, render_template, request, session
from random import choices
from secrets import token_bytes
from string import ascii_lowercase
from time import time


app = Flask(__name__)
app.secret_key = token_bytes(16)
pw_hash = b"$2b$12$TlDpPzihBCfMvQylze2t4um3vZ9YbbGuOn46ay7xLhO2wK0hQKT7."
pw_salt = b"$2b$12$TlDpPzihBCfMvQylze2t4u"

active = {}
id_len = 6
timeout = 120 # sec
max_content_len = 10**7 # max 10Mb
max_active = 10  # max 100Mb

@app.route("/")
def index():
	if "ok" not in session:
		return redirect("/login")

	req_id = "".join(choices(ascii_lowercase, k=id_len))
	active[req_id] = {}
	active[req_id]["time"] = int(time())

	return f"""
- created id {req_id} for {timeout} seconds<br>
- you can now submit data with POST /{req_id} (don't forget the session cookie)<br>
- then read the data with GET /{req_id} (don't forget the session cookie)<br>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	
	pw = request.form.get("password").encode()
	if hashpw(pw, pw_salt) == pw_hash:
		session["ok"] = True
		return redirect("/")

	return redirect("/login")


@app.route("/<req_id>", methods=["GET", "POST"])
def catch(req_id):
	if "ok" not in session:
		return redirect("/login")

	# remove old ids
	global active
	active = {key:val for key,val in active.items() if (val["time"] + timeout) > time()}

	if request.method == "GET":
		if req_id in active:
			if "req" in active[req_id]:
				return active[req_id]["req"]
			return "no requests yet\n"
		return "invalid id\n", 400

	if request.method == "POST":
		if request.content_length > max_content_len:
			return "request too large\n", 400
		if len(active) > max_active:
			return "server busy\n", 429
		if req_id not in active:
			return "bad id\n", 400

		active[req_id]["req"] = str(request.headers).encode() + request.get_data() + b"\n"
		return "caught\n"


# debug
if __name__ == "__main__":
	app.run("127.0.0.1", 9002)

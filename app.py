from flask import Flask, request
from string import ascii_lowercase
from time import time


app = Flask(__name__)
active = {}
allowed = ascii_lowercase
timeout = 60
id_len = 6
max_content_len = 10**5 # max 100 kb
max_active = 100  # 100 * 100kb = 10 Mb


@app.route("/")
def index():
	return "submit id like GET /abcdef create and read requests and POST /abcdef to send data\n"


@app.route("/<id>", methods=["GET", "POST"])
def catch(id):
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

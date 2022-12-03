# Catcher
 simple python server to catch requests from anywhere (mostly for CTFs) 

## How To
1. GET /abcdef  -> initialize abcdef endpoint
2. POST /abcdef -> saves headers and body
3. GET /abcdef  -> returns saved headers and body

## Deployment
```bash
sudo apt install gunicorn
pip3 install flask
python3 app.py
```

## Deployed at
- catcher.XXX.YYY (deploy it yourself)

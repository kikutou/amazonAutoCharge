from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_me():
    return "Hello me"

if __name__ == '__main__':
    app.run(host='0.0.0.0')

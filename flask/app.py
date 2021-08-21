from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test")
def test():
    return "<p>Test!</p>"


@app.route("/milk")
def milk():
    return "<p>Test!</p>"

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "<h3>It Works.</h3>"


@app.route("/about")
def about():
    return "<h3>About.</h3>"


@app.route("/health")
def health():
    return "<h3>Banana Fire.</h3>"

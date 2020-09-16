from scraper import Scraper
from flask import Flask, render_template, jsonify


app = Flask(__name__)


@app.route("/check_connection", methods=['GET', 'POST'])
def check_connection():
    return jsonify({'status': 'OK'})




@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

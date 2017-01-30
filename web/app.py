# coding: utf-8
from datetime import datetime

from flask import Flask, jsonify
from flask import render_template

import settings
from db import get_data

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/co2/', methods=['GET'])
@app.route('/co2/<string:from_date>', methods=['GET'])
def get_tasks(from_date=None):
    parsed_date = None
    if from_date:
        try:
            parsed_date = datetime.strptime(from_date, settings.DB_DATE_FORMAT)
        except ValueError:
            pass
    return jsonify(get_data(parsed_date))


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=settings.PORT)

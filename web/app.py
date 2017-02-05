# coding: utf-8
from datetime import datetime

from flask import Flask, jsonify, request
from flask import render_template

import settings
from db import get_uart_data, get_pwm_data

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/co2/', methods=['GET'])
@app.route('/co2/<string:from_date>', methods=['GET'])
def get_data(from_date=None):
    parsed_date = None
    is_pwm = request.args.get('pwm')
    limit = request.args.get('limit')
    if from_date:
        try:
            parsed_date = datetime.strptime(from_date, settings.DB_DATE_FORMAT)
        except ValueError:
            pass
    if is_pwm:
        data = get_pwm_data(parsed_date, limit)
    else:
        data = get_uart_data(parsed_date, limit)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=settings.PORT)

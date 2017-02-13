# coding: utf-8
from datetime import datetime

from flask import Flask, jsonify, request, redirect
from flask import render_template

import settings
from db import get_uart_data, get_pwm_data, reset_data

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
    limit = int(limit) if limit else limit
    smooth = request.args.get('smooth')
    smooth = int(smooth) if smooth else smooth
    if from_date:
        try:
            parsed_date = datetime.strptime(from_date, settings.DB_DATE_FORMAT)
        except ValueError:
            pass
    if is_pwm:
        data = get_pwm_data(parsed_date, limit, smooth)
    else:
        data = get_uart_data(parsed_date, limit, smooth)
    return jsonify(data)


@app.route('/reset/', methods=['GET'])
def reset():
    reset_data()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=settings.PORT)

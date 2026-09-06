from flask import Flask, render_template, redirect, url_for
import mysql.connector, os
from dotenv import load_dotenv

from routes.ror import ror_bp
from routes.wydatki import wydatki_bp
from routes.przychody import przychody_bp
from routes.bilans import bilans_bp
from routes.car import car_bp
from routes.chart import chart_bp

load_dotenv()
app = Flask(__name__)

@app.context_processor
def utility_processor():
    def format_pl(value):
        if value is None:
            return "0,00"
        try:
            # Formatuje liczbę ze spacją jako separatorem tysięcy i przecinkiem jako dziesiętnym
            return "{:,.2f}".format(float(value)).replace(",", " ").replace(".", ",").replace(" ", " ")
        except (ValueError, TypeError):
            return value
    return dict(format_pl=format_pl)

app.register_blueprint(ror_bp, url_prefix='/finanse/ror')
app.register_blueprint(wydatki_bp, url_prefix='/finanse/wydatki')
app.register_blueprint(przychody_bp, url_prefix='/finanse/przychody')
app.register_blueprint(bilans_bp, url_prefix='/finanse/bilans')
app.register_blueprint(car_bp, url_prefix='/finanse/car')
app.register_blueprint(chart_bp, url_prefix='/finanse/chart')

@app.route('/finanse/')
def index():
    return render_template('index.html', db_ok=True, db_msg="Połączono")

@app.route('/finanse')
def fix_url():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

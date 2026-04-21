from flask import Flask, render_template, send_from_directory, abort, jsonify
import os
import sys
import subprocess
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

if basedir not in sys.path:
    sys.path.append(basedir)

from utils import get_stats, CSV_PATH, SCRIPTS

app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
app.jinja_loader.searchpath.append('/var/www/html/flask/shared/templates')

@app.template_filter('format_pl')
def format_pl(value, precision=2):
    try:
        if value is None: return "0,00"
        return "{:,.{}f}".format(float(value), precision).replace(",", " ").replace(".", ",")
    except:
        return value

@app.route('/inwestycje/get_csv/<filename>')
def get_csv(filename):
    if not os.path.exists(os.path.join(CSV_PATH, filename)):
        abort(404)
    return send_from_directory(CSV_PATH, filename)

@app.route('/inwestycje/run_etl_import')
def run_etl_import():
    try:
        subprocess.Popen(["/bin/bash", SCRIPTS['etl_import']])
        return jsonify({"status": "success", "message": "Import uruchomiony."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/inwestycje/run_etl_gpw')
def run_etl_gpw():
    try:
        # Używamy run zamiast Popen, aby poczekać na zakończenie przed przeładowaniem strony
        subprocess.run(["/bin/bash", SCRIPTS['etl_gpw']], check=True)
        return jsonify({"status": "success", "message": "Import GPW zakończony."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/inwestycje/run_etl_load')
def run_etl_load():
    try:
        subprocess.Popen(["/bin/bash", SCRIPTS['etl_load']])
        return jsonify({"status": "success", "message": "Ładowanie uruchomione."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/inwestycje/run_gpw_check')
def run_gpw_check():
    try:
        subprocess.run(["/bin/bash", SCRIPTS['gpw_check']], check=True)
        return jsonify({"status": "ok", "message": "Sprawdzono."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Blueprints
from routes.chart import chart_bp
from routes.dane import dane_bp
from routes.dane_dzienne import dane_dzienne_bp
from routes.historia import historia_bp
from routes.obroty import obroty_bp
from routes.platforma import platforma_bp
from routes.sprzedaj import sprzedaj_bp
from routes.ticker import ticker_bp

app.register_blueprint(chart_bp, url_prefix='/inwestycje/chart')
app.register_blueprint(dane_bp, url_prefix='/inwestycje/dane')
app.register_blueprint(dane_dzienne_bp, url_prefix='/inwestycje/dane_dzienne')
app.register_blueprint(historia_bp, url_prefix='/inwestycje/historia')
app.register_blueprint(obroty_bp, url_prefix='/inwestycje/obroty')
app.register_blueprint(platforma_bp, url_prefix='/inwestycje/platforma')
app.register_blueprint(sprzedaj_bp, url_prefix='/inwestycje/sprzedaj')
app.register_blueprint(ticker_bp, url_prefix='/inwestycje/ticker')

@app.route('/inwestycje/')
@app.route('/')
def index():
    stats_data = get_stats()
    return render_template('index.html', tytul_aplikacji='Inwestycje', db_ok=True, s=stats_data)

if __name__ == '__main__':
    app.run(port=5002)

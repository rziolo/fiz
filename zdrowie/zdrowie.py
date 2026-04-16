from flask import Flask, render_template
import mysql.connector
import os
from dotenv import load_dotenv
from routes.ha_vita_pressure import pressure_bp

basedir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__, template_folder='templates')
app.jinja_loader.searchpath.append('/var/www/html/flask/shared/templates')

# Rejestrujemy blueprint pod konkretnym prefiksem bezpośrednio we Flasku
app.register_blueprint(pressure_bp, url_prefix='/zdrowie')

def check_db():
    try:
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
            connect_timeout=3
        )
        db.close()
        return True, "OK"
    except Exception as e:
        return False, str(e)

@app.route('/zdrowie')
def index():
    db_ok, db_msg = check_db()
    return render_template('index.html', tytul_aplikacji='Zdrowie', db_ok=db_ok, db_msg=db_msg)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5003)

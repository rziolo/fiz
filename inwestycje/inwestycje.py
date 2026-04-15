from flask import Flask, render_template
import mysql.connector
import os
import sys
from dotenv import load_dotenv

basedir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__, template_folder='templates')
app.jinja_loader.searchpath.append('/var/www/html/flask/shared/templates')

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
        print(f"!!! DEBUG DB ERROR: {str(e)}", file=sys.stderr, flush=True)
        return False, str(e)

@app.route('/')
def index():
    db_ok, db_msg = check_db()
    return render_template('index.html', tytul_aplikacji='Inwestycje', db_ok=db_ok, db_msg=db_msg)

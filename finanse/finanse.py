from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__, template_folder='templates')
app.jinja_loader.searchpath.append('/var/www/html/flask/shared/templates')

@app.route('/')
def index():
    return render_template('index.html', tytul_aplikacji='Finanse Domowe', db_host=os.getenv('DB_HOST'))

if __name__ == '__main__':
    app.run(port=5001)

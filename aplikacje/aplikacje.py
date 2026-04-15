from flask import Flask, render_template
import os

app = Flask(__name__, template_folder='templates')
# Ustawienie ścieżki do shared templates
app.jinja_loader.searchpath.append('/var/www/html/flask/shared/templates')

@app.route('/')
def index():
    return render_template('index.html', tytul_aplikacji='HUB Aplikacji')

if __name__ == '__main__':
    app.run(port=5000)

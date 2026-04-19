from flask import Blueprint, render_template
import os

# Pobieramy absolutną ścieżkę do katalogu, w którym jest ten plik (routes)
# i cofamy się o jeden poziom do góry, by wejść do templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

chart_bp = Blueprint('chart', __name__, template_folder=template_dir)

@chart_bp.route('/')
def index():
    return render_template('chart.html')

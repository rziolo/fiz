from flask import Blueprint, render_template
import os

# Pobieramy absolutną ścieżkę do katalogu, w którym jest ten plik (routes)
# i cofamy się o jeden poziom do góry, by wejść do templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

historia_bp = Blueprint('historia', __name__, template_folder=template_dir)

@historia_bp.route('/')
def index():
    return render_template('historia.html')

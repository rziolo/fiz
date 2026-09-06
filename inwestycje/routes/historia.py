from flask import Blueprint, render_template
import os
import mysql.connector

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
historia_bp = Blueprint('historia', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

@historia_bp.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. ROK MIESIĄC
    cursor.execute("""
        SELECT
            rm_label as rok_miesiac,
            (SELECT ABS(wklad) FROM dane_dzienne d2 WHERE DATE_FORMAT(d2.data, '%Y-%m') = rm_label ORDER BY d2.data DESC LIMIT 1) as wklad,
            (SELECT wartosc FROM dane_dzienne d3 WHERE DATE_FORMAT(d3.data, '%Y-%m') = rm_label ORDER BY d3.data DESC LIMIT 1) as wartosc,
            (SELECT ABS(AVG(wklad)) FROM dane_dzienne d4 WHERE DATE_FORMAT(d4.data, '%Y-%m') = rm_label) as sredni_wklad,
            (SELECT SUM(sprzedaz_cena - zakup_cena) FROM obroty o WHERE DATE_FORMAT(o.sprzedaz_data, '%Y-%m') = rm_label AND ticker_nm != 'dywidenda') as zysk_op
        FROM (SELECT DISTINCT DATE_FORMAT(data, '%Y-%m') as rm_label FROM dane_dzienne) as periods
        ORDER BY rok_miesiac DESC
    """)
    rok_miesiac = cursor.fetchall()

    # 2. ROK
    cursor.execute("""
        SELECT
            rok_label as rok,
            (SELECT ABS(wklad) FROM dane_dzienne d2 WHERE DATE_FORMAT(d2.data, '%Y') = rok_label ORDER BY d2.data DESC LIMIT 1) as wklad,
            (SELECT wartosc FROM dane_dzienne d3 WHERE DATE_FORMAT(d3.data, '%Y') = rok_label ORDER BY d3.data DESC LIMIT 1) as wartosc
        FROM (SELECT DISTINCT DATE_FORMAT(data, '%Y') as rok_label FROM dane_dzienne) as years
        ORDER BY rok DESC
    """)
    rok_stats = cursor.fetchall()

    # 3. HISTORIA INWESTYCJI
    cursor.execute("SELECT * FROM obroty ORDER BY zakup_data DESC")
    historia_inw = cursor.fetchall()

    # 4. OBROTY ROK MIESIĄC
    cursor.execute("""
        SELECT
            rm,
            SUM(zakup_zl) as zakup_zl, SUM(zakup_il) as zakup_ilosc,
            SUM(sprz_zl) as sprzedaz_zl, SUM(sprzedaz_ilosc) as sprzedaz_ilosc,
            SUM(dyw_zl) as dywidenda_zl, SUM(dywidenda_ilosc) as dywidenda_ilosc
        FROM (
            SELECT DATE_FORMAT(zakup_data, '%Y-%m') as rm, zakup_cena as zakup_zl,
                   1 as zakup_il, 0 as sprz_zl, 0 as sprzedaz_ilosc, 0 as dyw_zl, 0 as dywidenda_ilosc
            FROM obroty WHERE ticker_nm != 'dywidenda'
            UNION ALL
            SELECT DATE_FORMAT(sprzedaz_data, '%Y-%m') as rm, 0, 0, sprzedaz_cena, 1, 0, 0
            FROM obroty WHERE ticker_nm != 'dywidenda' AND sprzedaz_data IS NOT NULL
            UNION ALL
            SELECT DATE_FORMAT(sprzedaz_data, '%Y-%m') as rm, 0, 0, 0, 0, sprzedaz_cena, 1
            FROM obroty WHERE ticker_nm = 'dywidenda'
        ) as combined
        GROUP BY rm ORDER BY rm DESC
    """)
    obroty_rm = cursor.fetchall()

    # 5. OBROTY ROK (rozbudowane o Wartość i Spółki dla ostatniego dnia roku)
    cursor.execute("""
        SELECT
            c.r,
            SUM(c.zakup_zl) as zakup_zl, SUM(c.zakup_il) as zakup_ilosc,
            SUM(c.sprz_zl) as sprzedaz_zl, SUM(c.sprzedaz_ilosc) as sprzedaz_ilosc,
            SUM(c.dyw_zl) as dywidenda_zl, SUM(c.dywidenda_ilosc) as dywidenda_ilosc,
            (
                SELECT d.wartosc 
                FROM dane_dzienne d 
                WHERE DATE_FORMAT(d.data, '%Y') = c.r 
                ORDER BY d.data DESC LIMIT 1
            ) as wartosc,
            (
                SELECT COUNT(DISTINCT o.ticker_nm)
                FROM obroty o
                WHERE o.ticker_nm != 'dywidenda'
                  AND o.zakup_data <= (SELECT MAX(d.data) FROM dane_dzienne d WHERE DATE_FORMAT(d.data, '%Y') = c.r)
                  AND (o.sprzedaz_data IS NULL OR o.sprzedaz_data > (SELECT MAX(d.data) FROM dane_dzienne d WHERE DATE_FORMAT(d.data, '%Y') = c.r))
            ) as spolki_ilosc
        FROM (
            SELECT DATE_FORMAT(zakup_data, '%Y') as r, zakup_cena as zakup_zl,
                   1 as zakup_il, 0 as sprz_zl, 0 as sprzedaz_ilosc, 0 as dyw_zl, 0 as dywidenda_ilosc
            FROM obroty WHERE ticker_nm != 'dywidenda'
            UNION ALL
            SELECT DATE_FORMAT(sprzedaz_data, '%Y') as r, 0, 0, sprzedaz_cena, 1, 0, 0
            FROM obroty WHERE ticker_nm != 'dywidenda' AND sprzedaz_data IS NOT NULL
            UNION ALL
            SELECT DATE_FORMAT(sprzedaz_data, '%Y') as r, 0, 0, 0, 0, sprzedaz_cena, 1
            FROM obroty WHERE ticker_nm = 'dywidenda'
        ) as c
        GROUP BY c.r ORDER BY c.r DESC
    """)
    obroty_r = cursor.fetchall()

    db.close()
    return render_template('historia.html', rok_miesiac=rok_miesiac, rok_stats=rok_stats,
                           historia_inw=historia_inw, obroty_rm=obroty_rm, obroty_r=obroty_r)

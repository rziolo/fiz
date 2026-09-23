import sys
import os
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'etl', 'db', 'health_connect', 'health_connect_export.db')
PDF_PATH = os.path.join(BASE_DIR, 'static', 'wykres.pdf')

# Zakres dat podawany jako argumenty skryptu
date_from = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
date_to = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m-%d')

from_ms = int(datetime.strptime(f"{date_from} 00:00:00", '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
to_ms = int(datetime.strptime(f"{date_to} 23:59:59", '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

if not os.path.exists(DB_PATH):
    sys.exit(1)

conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
cursor = conn.cursor()

# Zapytanie sumujące kroki dziennie bez duplikatów
steps_raw = cursor.execute('''
    SELECT date(start_time/1000, 'unixepoch', 'localtime') as dzien,
           MAX(count) as max_krokow,
           SUM(count) as suma_krokow
    FROM steps_record_table
    WHERE start_time BETWEEN ? AND ?
    GROUP BY dzien
    ORDER BY dzien ASC
''', (from_ms, to_ms)).fetchall()

conn.close()

if not steps_raw:
    sys.exit(0)

dates_str = [row[0] for row in steps_raw]
counts = [row[1] if row[2] > 15000 and row[1] > 0 else row[2] for row in steps_raw]

dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates_str]

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(dates, counts, color='#198754', width=0.6)
ax.set_title(f'Liczba kroków ({date_from} do {date_to})', fontsize=12, pad=15)
ax.set_ylabel('Kroki', fontsize=10)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
plt.savefig(PDF_PATH, format='pdf')
plt.close()

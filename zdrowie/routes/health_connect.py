from flask import Blueprint, render_template
import sqlite3

health_connect_bp = Blueprint('health_connect', __name__)
DB_PATH = '/var/www/html/flask/zdrowie/etl/db/health_connect/health_connect_export.db'

EXERCISE_TYPE_MAP = {
    0: "Inny / Ogólny", 1: "Badminton", 2: "Baseball", 3: "Koszykówka", 8: "Kolarstwo",
    9: "Kolarstwo stacjonarne", 10: "Orbitrek", 11: "Taniec", 13: "Piłka nożna", 28: "Wędrówka",
    33: "Pilates", 37: "Bieganie", 38: "Bieżnia elektryczna", 52: "Pływanie", 53: "Spacer",
    57: "Nordic Walking", 58: "Trening siłowy", 59: "Rozciąganie", 60: "Joga"
}

def pl_num(val, decimals=2):
    if val is None:
        return None
    try:
        val_float = float(val)
        formatted = f"{val_float:,.{decimals}f}"
        return formatted.replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return str(val)

def format_duration(minutes):
    if not minutes or minutes <= 0:
        return "0min"
    mins = int(round(minutes))
    hours = mins // 60
    rem_mins = mins % 60
    if hours > 0 and rem_mins > 0:
        return f"{hours}h {rem_mins}min"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{rem_mins}min"

def get_db_connection():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn

@health_connect_bp.route('/health-connect')
@health_connect_bp.route('/health_connect')
def health_connect_view():
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- AGREGACJA DANYCH DLA TABELI 'DANE RÓŻNE' ---
    combined = {}

    def ensure_day(day_str):
        if day_str not in combined:
            combined[day_str] = {
                'day': day_str,
                'weight': None,
                'steps': None,
                'systolic': None,
                'diastolic': None,
                'resting_hr': None,
                'spo2': None,
                'body_fat': None,
                'calories': None
            }

    # 1. Waga
    for r in cursor.execute("SELECT strftime('%Y-%m-%d', time/1000, 'unixepoch', 'localtime') as day, AVG(weight)/1000.0 as val FROM weight_record_table GROUP BY day"):
        ensure_day(r['day'])
        combined[r['day']]['weight'] = pl_num(r['val'], 1)

    # 2. Kroki
    raw_steps = cursor.execute("""
        SELECT day, SUM(count) as steps FROM (
            SELECT strftime('%Y-%m-%d', start_time/1000, 'unixepoch', 'localtime') as day,
                   start_time, MAX(count) as count
            FROM steps_record_table
            WHERE app_info_id = 7
            GROUP BY start_time
        ) GROUP BY day
    """).fetchall()
    for r in raw_steps:
        ensure_day(r['day'])
        combined[r['day']]['steps'] = pl_num(r['steps'], 0)

    # 3. Ciśnienie
    raw_bp = cursor.execute("""
        SELECT strftime('%Y-%m-%d', time/1000, 'unixepoch', 'localtime') as day,
               AVG(systolic) as systolic, AVG(diastolic) as diastolic
        FROM blood_pressure_record_table
        GROUP BY day
    """).fetchall()
    for r in raw_bp:
        ensure_day(r['day'])
        combined[r['day']]['systolic'] = pl_num(r['systolic'], 0)
        combined[r['day']]['diastolic'] = pl_num(r['diastolic'], 0)

    # 4. Tętno spoczynkowe
    raw_rhr = cursor.execute("""
        SELECT strftime('%Y-%m-%d', time/1000, 'unixepoch', 'localtime') as day,
               ROUND(AVG(beats_per_minute), 0) as rate
        FROM resting_heart_rate_record_table
        GROUP BY day
    """).fetchall()
    for r in raw_rhr:
        ensure_day(r['day'])
        combined[r['day']]['resting_hr'] = pl_num(r['rate'], 0)

    # 5. Saturacja (SpO2)
    raw_spo2 = cursor.execute("""
        SELECT strftime('%Y-%m-%d', time/1000, 'unixepoch', 'localtime') as day,
               AVG(percentage) as percentage
        FROM oxygen_saturation_record_table
        GROUP BY day
    """).fetchall()
    for r in raw_spo2:
        ensure_day(r['day'])
        combined[r['day']]['spo2'] = pl_num(r['percentage'], 1)

    # 6. Tłuszcz
    raw_body_fat = cursor.execute("""
        SELECT strftime('%Y-%m-%d', time/1000, 'unixepoch', 'localtime') as day,
               AVG(percentage) as percentage
        FROM body_fat_record_table
        GROUP BY day
    """).fetchall()
    for r in raw_body_fat:
        ensure_day(r['day'])
        combined[r['day']]['body_fat'] = pl_num(r['percentage'], 2)

    # 7. Kalorie
    raw_calories = cursor.execute("""
        SELECT day, ROUND(SUM(energy), 0) as total_calories FROM (
            SELECT strftime('%Y-%m-%d', start_time/1000, 'unixepoch', 'localtime') as day,
                   start_time, MAX(energy) as energy
            FROM active_calories_burned_record_table
            GROUP BY start_time
        ) GROUP BY day
    """).fetchall()
    for r in raw_calories:
        ensure_day(r['day'])
        val = r['total_calories']
        if val and val > 50000:
            val = val / 1000.0
        combined[r['day']]['calories'] = pl_num(val, 0)

    # Sortowanie zbiorczej listy według daty malejąco
    dane_rozne = sorted(combined.values(), key=lambda x: x['day'], reverse=True)[:50]

    # --- POZOSTAŁE ZAKŁADKI ---

    # Tętno chwilowe
    raw_hr_series = cursor.execute("""
        SELECT strftime('%Y-%m-%d %H:%M', epoch_millis/1000, 'unixepoch', 'localtime') as formatted_time,
               ROUND(AVG(beats_per_minute), 0) as bpm
        FROM heart_rate_record_series_table
        GROUP BY formatted_time
        ORDER BY MIN(epoch_millis) DESC
        LIMIT 50
    """).fetchall()
    heart_rate_data = [{'time': r['formatted_time'], 'bpm': pl_num(r['bpm'], 0)} for r in raw_hr_series]

    # Treningi
    raw_exercise = cursor.execute("""
        SELECT strftime('%Y-%m-%d %H:%M', start_time/1000, 'unixepoch', 'localtime') as start_date,
               title, exercise_type,
               ROUND((end_time - start_time) / 60000.0, 1) as duration_min
        FROM exercise_session_record_table
        ORDER BY start_time DESC
        LIMIT 50
    """).fetchall()
    exercise = []
    for item in raw_exercise:
        row = dict(item)
        type_name = EXERCISE_TYPE_MAP.get(row.get('exercise_type'), f"Trening ({row.get('exercise_type')})")
        display_name = f"{row['title']} ({type_name})" if row.get('title') and str(row['title']).strip() else type_name
        exercise.append({'start_date': row['start_date'], 'display_name': display_name, 'duration_str': format_duration(row.get('duration_min', 0))})

    # Sen
    raw_sleep = cursor.execute("""
        SELECT sleep_start, sleep_end,
               MAX(light_sleep_min) as light_sleep_min,
               MAX(deep_sleep_min) as deep_sleep_min,
               MAX(rem_sleep_min) as rem_sleep_min,
               MAX(awake_min) as awake_min
        FROM (
            SELECT strftime('%Y-%m-%d %H:%M', MIN(s.stage_start_time)/1000, 'unixepoch', 'localtime') as sleep_start,
                   strftime('%Y-%m-%d %H:%M', MAX(s.stage_end_time)/1000, 'unixepoch', 'localtime') as sleep_end,
                   SUM(CASE WHEN s.stage_type = 4 THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as light_sleep_min,
                   SUM(CASE WHEN s.stage_type = 5 THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as deep_sleep_min,
                   SUM(CASE WHEN s.stage_type = 6 THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as rem_sleep_min,
                   SUM(CASE WHEN s.stage_type IN (1, 3) THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as awake_min
            FROM sleep_stages_table s
            GROUP BY s.parent_key
        )
        WHERE (light_sleep_min + deep_sleep_min + rem_sleep_min) >= 60
        GROUP BY sleep_start, sleep_end
        ORDER BY sleep_start DESC
        LIMIT 30
    """).fetchall()

    sleep_stages = [{
        'sleep_start': r['sleep_start'],
        'sleep_end': r['sleep_end'],
        'light_sleep_str': format_duration(r['light_sleep_min']),
        'deep_sleep_str': format_duration(r['deep_sleep_min']),
        'rem_sleep_str': format_duration(r['rem_sleep_min']),
        'awake_str': format_duration(r['awake_min'])
    } for r in raw_sleep]

    conn.close()

    return render_template(
        'health_connect.html',
        dane_rozne=dane_rozne,
        heart_rate_data=heart_rate_data,
        exercise=exercise,
        sleep_stages=sleep_stages
    )
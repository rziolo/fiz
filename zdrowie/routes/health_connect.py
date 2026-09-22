from flask import Blueprint, render_template
import sqlite3

health_connect_bp = Blueprint('health_connect', __name__)
DB_PATH = '/var/www/html/flask/zdrowie/etl/db/health_connect/health_connect_export.db'

EXERCISE_TYPE_MAP = {
    0: "Inny / Ogólny",
    1: "Badminton",
    2: "Baseball",
    3: "Koszykówka",
    4: "Koszykówka",
    5: "Boks",
    8: "Kolarstwo",
    9: "Kolarstwo stacjonarne",
    10: "Orbitrek",
    11: "Taniec",
    13: "Piłka nożna",
    26: "Gimnastyka",
    27: "Piłka ręczna",
    28: "Wędrówka",
    29: "Jazda na łyżwach",
    31: "Sztuki walki",
    33: "Pilates",
    34: "Wioślarstwo",
    35: "Wioślarstwo stacjonarne",
    37: "Bieganie",
    38: "Bieżnia elektryczna",
    39: "Żeglarstwo",
    44: "Narciarstwo",
    46: "Snowboard",
    48: "Squash",
    49: "Schody",
    50: "Strajder",
    52: "Pływanie",
    53: "Spacer",
    54: "Tenis stołowy",
    55: "Tenis",
    56: "Siatkówka",
    57: "Nordic Walking",
    58: "Trening siłowy",
    59: "Rozciąganie",
    60: "Joga",
    62: "Zumba"
}

def pl_num(val, decimals=2):
    if val is None:
        return ""
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
def health_connect_view():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tkanka tłuszczowa
    raw_body_fat = cursor.execute("""
        SELECT strftime('%Y-%m-%d %H:%M', time/1000, 'unixepoch', 'localtime') as date, AVG(percentage) as percentage
        FROM body_fat_record_table
        GROUP BY date
        ORDER BY MIN(time) DESC LIMIT 50
    """).fetchall()
    body_fat = [{'date': r['date'], 'percentage_str': pl_num(r['percentage'], 2)} for r in raw_body_fat]

    # 2. Ciśnienie krwi
    raw_bp = cursor.execute("""
        SELECT strftime('%Y-%m-%d %H:%M', time/1000, 'unixepoch', 'localtime') as date, systolic, diastolic
        FROM blood_pressure_record_table ORDER BY time DESC LIMIT 50
    """).fetchall()
    blood_pressure = [{
        'date': r['date'], 
        'systolic_str': pl_num(r['systolic'], 0), 
        'diastolic_str': pl_num(r['diastolic'], 0)
    } for r in raw_bp]

    # 3. Tętno spoczynkowe
    raw_rhr = cursor.execute("""
        SELECT strftime('%Y-%m-%d', time/1000, 'unixepoch', 'localtime') as date, beats_per_minute as rate
        FROM resting_heart_rate_record_table ORDER BY time DESC LIMIT 50
    """).fetchall()
    resting_hr = [{'date': r['date'], 'rate_str': pl_num(r['rate'], 0)} for r in raw_rhr]

    # 4. Saturacja (SpO2)
    raw_spo2 = cursor.execute("""
        SELECT strftime('%Y-%m-%d %H:%M', time/1000, 'unixepoch', 'localtime') as date, AVG(percentage) as percentage
        FROM oxygen_saturation_record_table
        GROUP BY date
        ORDER BY MIN(time) DESC LIMIT 50
    """).fetchall()
    oxygen_saturation = [{'date': r['date'], 'percentage_str': pl_num(r['percentage'], 1)} for r in raw_spo2]

    # 5. Treningi
    raw_exercise = cursor.execute("""
        SELECT 
            strftime('%Y-%m-%d %H:%M', start_time/1000, 'unixepoch', 'localtime') as start_date,
            title,
            exercise_type,
            ROUND((end_time - start_time) / 60000.0, 1) as duration_min
        FROM exercise_session_record_table ORDER BY start_time DESC LIMIT 50
    """).fetchall()

    exercise = []
    for item in raw_exercise:
        row = dict(item)
        type_code = row.get('exercise_type')
        type_name = EXERCISE_TYPE_MAP.get(type_code, f"Trening (typ: {type_code})")
        
        if row.get('title') and str(row['title']).strip():
            display_name = f"{row['title']} ({type_name})"
        else:
            display_name = type_name
            
        exercise.append({
            'start_date': row['start_date'],
            'display_name': display_name,
            'duration_str': format_duration(row.get('duration_min', 0))
        })

    # 6. Spalone kalorie (dzielimy przez 1000 jeśli dane w bazie są w surowych dżulach/kaloriach)
    raw_calories = cursor.execute("""
        SELECT 
            strftime('%Y-%m-%d', start_time/1000, 'unixepoch', 'localtime') as day,
            ROUND(SUM(energy), 0) as total_calories
        FROM active_calories_burned_record_table
        GROUP BY day ORDER BY day DESC LIMIT 30
    """).fetchall()
    
    active_calories = []
    for r in raw_calories:
        val = r['total_calories']
        # Korekta w przypadku gdy wartość jest przeliczona na dżule w bazie
        if val and val > 50000:
            val = val / 1000.0
        active_calories.append({
            'day': r['day'],
            'calories_str': pl_num(val, 0)
        })

    # 7. Fazy snu
    raw_sleep = cursor.execute("""
        SELECT 
            s.parent_key,
            strftime('%Y-%m-%d %H:%M', MIN(s.stage_start_time)/1000, 'unixepoch', 'localtime') as sleep_start,
            SUM(CASE WHEN s.stage_type = 4 THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as light_sleep_min,
            SUM(CASE WHEN s.stage_type = 5 THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as deep_sleep_min,
            SUM(CASE WHEN s.stage_type = 6 THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as rem_sleep_min,
            SUM(CASE WHEN s.stage_type IN (1, 3) THEN (s.stage_end_time - s.stage_start_time) ELSE 0 END) / 60000.0 as awake_min
        FROM sleep_stages_table s
        GROUP BY s.parent_key
        ORDER BY sleep_start DESC LIMIT 30
    """).fetchall()

    sleep_stages = []
    for item in raw_sleep:
        row = dict(item)
        sleep_stages.append({
            'sleep_start': row['sleep_start'],
            'light_sleep_str': format_duration(row.get('light_sleep_min', 0)),
            'deep_sleep_str': format_duration(row.get('deep_sleep_min', 0)),
            'rem_sleep_str': format_duration(row.get('rem_sleep_min', 0)),
            'awake_str': format_duration(row.get('awake_min', 0))
        })

    conn.close()

    return render_template(
        'health_connect.html',
        body_fat=body_fat,
        blood_pressure=blood_pressure,
        resting_hr=resting_hr,
        oxygen_saturation=oxygen_saturation,
        exercise=exercise,
        active_calories=active_calories,
        sleep_stages=sleep_stages
    )

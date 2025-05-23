#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Database config
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': int(os.environ.get('POSTGRES_PORT', 5432)),
    'user': os.environ.get('POSTGRES_USER', 'demouser'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'demopassword'),
    'dbname': os.environ.get('POSTGRES_DATABASE', 'analytics'),
}

@app.route('/')
def dashboard():
    """Serve simple dashboard"""
    with open('../dashboard/simple.html', 'r') as f:
        return f.read()

@app.route('/api/vitals-by-age-group')
def get_vitals_by_age_group():
    """Get average vitals by age group - optimized query"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query the materialized view for instant results
        cursor.execute("SELECT * FROM analytics.mv_vitals_by_age_group ORDER BY age_group")
        results = cursor.fetchall()
        
        # Convert to structured data
        age_groups = []
        for row in results:
            age_groups.append({
                'ageGroup': row[0],
                'totalReadings': row[1],
                'avgTemperature': float(row[2]) if row[2] else 0,
                'avgPulseRate': int(row[3]) if row[3] else 0,
                'avgSystolic': int(row[4]) if row[4] else 0,
                'avgDiastolic': int(row[5]) if row[5] else 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': age_groups,
            'message': 'Average vitals by age group retrieved successfully'
        })
        
    except Exception as e:
        # Mock data fallback for demo
        return jsonify({
            'success': False,
            'data': [
                {
                    'ageGroup': '0-17',
                    'totalReadings': 0,
                    'avgTemperature': 0,
                    'avgPulseRate': 0,
                    'avgSystolic': 0,
                    'avgDiastolic': 0
                }
            ],
            'message': f'Database not available: {str(e)}'
        })

@app.route('/api/refresh')
def refresh_materialized_view():
    """Refresh the materialized view to get latest data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Set search path to include analytics schema
        cursor.execute("SET search_path TO analytics, public;")
        
        # Refresh the materialized view
        cursor.execute("REFRESH MATERIALIZED VIEW analytics.mv_vitals_by_age_group")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Materialized view refreshed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to refresh materialized view: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 Vitals by Age Group API")
    print("📊 Dashboard: http://localhost:5001")
    print("🔍 Age Group Data: http://localhost:5001/api/vitals-by-age-group")
    print("🔄 Refresh Data: http://localhost:5001/api/refresh")
    app.run(debug=True, host='0.0.0.0', port=5001) 
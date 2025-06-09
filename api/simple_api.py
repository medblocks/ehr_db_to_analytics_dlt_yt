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
    try:
        # Try multiple possible paths for the dashboard file
        dashboard_paths = [
            'dashboard/simple.html',
            '../dashboard/simple.html',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'simple.html')
        ]
        
        for path in dashboard_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read()
        
        # If no dashboard file found, return a simple HTML response
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Health Analytics Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .endpoint h3 { margin: 0 0 10px 0; color: #333; }
                .endpoint a { color: #007bff; text-decoration: none; }
                .endpoint a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💓 Pulse Rate Analytics Dashboard</h1>
                <p>Simple analytics showing average pulse rate by age group</p>
                
                <div class="endpoint">
                    <h3>📊 Pulse Rate by Age Group</h3>
                    <a href="/api/vitals-by-age-group" target="_blank">View Pulse Rate Analytics</a>
                    <p>Get average pulse rate data grouped by age ranges</p>
                </div>
                
                <div class="endpoint">
                    <h3>🔄 Refresh Data</h3>
                    <a href="/api/refresh" target="_blank">Refresh Analytics Data</a>
                    <p>Update analytics with latest data from source</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"<h1>Dashboard Error</h1><p>Error loading dashboard: {str(e)}</p>"

@app.route('/api/vitals-by-age-group')
def get_vitals_by_age_group():
    """Get average pulse rate by age group from ELT materialized view"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query the simplified materialized view created by our ELT pipeline
        cursor.execute("SELECT * FROM analytics.mv_pulse_rate_by_age_group ORDER BY age_group")
        results = cursor.fetchall()
        
        # Convert to structured data
        age_groups = []
        for row in results:
            age_groups.append({
                'ageGroup': row[0],
                'totalReadings': row[1],
                'uniquePatients': row[2],
                'avgPulseRate': float(row[3]) if row[3] else 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': age_groups,
            'message': 'Pulse rate by age group retrieved successfully from ELT pipeline'
        })
        
    except Exception as e:
        # Mock data fallback for demo
        return jsonify({
            'success': False,
            'data': [
                {
                    'ageGroup': '0-17',
                    'totalReadings': 0,
                    'uniquePatients': 0,
                    'avgPulseRate': 0
                }
            ],
            'message': f'Database not available (run ELT pipeline first): {str(e)}'
        })

@app.route('/api/refresh')
def refresh_materialized_views():
    """Refresh materialized view to get latest data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Refresh the pulse rate materialized view
        cursor.execute("REFRESH MATERIALIZED VIEW analytics.mv_pulse_rate_by_age_group")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Pulse rate analytics refreshed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to refresh analytics: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 Health Analytics API (ELT-powered)")
    print("📊 Dashboard: http://localhost:5001")
    print("🔍 Pulse Rate Data: http://localhost:5001/api/vitals-by-age-group")
    print("🔄 Refresh Data: http://localhost:5001/api/refresh")
    app.run(debug=True, host='0.0.0.0', port=5001) 
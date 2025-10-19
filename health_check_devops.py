#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Health Check Endpoint Mejorado - DevOps Belgrano Ahorro
Endpoint para verificar estado de todos los servicios
'''

from flask import Flask, jsonify
import requests
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

def check_belgrano_ahorro():
    """Verificar estado de Belgrano Ahorro"""
    try:
        url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
        response = requests.get(f"{url}/healthz", timeout=10)
        return {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response.elapsed.total_seconds(),
            'status_code': response.status_code
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_database():
    """Verificar estado de la base de datos"""
    try:
        db_path = os.environ.get('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        count = cursor.fetchone()[0]
        conn.close()
        return {'status': 'healthy', 'productos_count': count}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@app.route('/health')
def health_check():
    """Endpoint de health check"""
    belgrano_status = check_belgrano_ahorro()
    db_status = check_database()
    
    overall_status = 'healthy'
    if belgrano_status['status'] != 'healthy' or db_status['status'] != 'healthy':
        overall_status = 'unhealthy'
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'overall_status': overall_status,
        'services': {
            'belgrano_ahorro': belgrano_status,
            'database': db_status
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

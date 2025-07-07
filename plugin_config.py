# ~/db_plugin/plugin_config.py

import os

class AppConfig:
    # --- InfluxDB Configuration ---
    INFLUXDB_HOST = '192.168.1.215'
    INFLUXDB_PORT = 8086
    INFLUXDB_DATABASE = 'reader_62F64_SAM'

    # --- Charting Configuration ---
    CHART_TITLE = "Power (Last 60m)"
    CHART_X_AXIS_LABEL = "Time"
    CHART_Y_AXIS_LABEL = "Watt (W)"
    CHART_TIME_RANGE = "60m"

    # Data series for charting (no color needed for 1-bit B&W)
    DATA_SERIES = [
        {"name": "Import", "measurement": "Momentanverbrauch_Import", "field": "value"},
        {"name": "Export", "measurement": "Momentanverbrauch_Export", "field": "value"},
    ]

    # --- Output Path for Test (TEMPORARILY TO HOME DIRECTORY) ---
    # Uncomment the following line to use a specific web server root directory
    HOME_DIR = os.path.expanduser('~') 
    CHART_IMAGE_FILE = 'chart.png'
    CHART_OUTPUT_PATH = os.path.join(HOME_DIR, CHART_IMAGE_FILE)

    # TRMNL_WEB_SERVER_ROOT = '/var/www/html' 
    # CHART_OUTPUT_PATH = os.path.join(TRMNL_WEB_SERVER_ROOT, CHART_IMAGE_FILE) 


    TRMNL_WIDTH_PX = 800
    TRMNL_HEIGHT_PX = 480
# ~/db_plugin/plugin_config.py

import os

class AppConfig:
    # --- InfluxDB Configuration ---
    INFLUXDB_HOST = '192.168.1.215'
    INFLUXDB_PORT = 8086
    INFLUXDB_DATABASE = 'reader_62F64_SAM'

    # --- Charting Configuration ---
    CHART_TITLE = "Watt (Letzte 60 Minuten)"
    CHART_X_AXIS_LABEL = "Zeit"
    CHART_Y_AXIS_LABEL = "Watt (W)"
    CHART_TIME_RANGE = "60m"

    # Data series for charting (no color needed for 1-bit B&W)
    DATA_SERIES = [
        {"name": "Import", "measurement": "Momentanverbrauch_Import", "field": "value"},
        {"name": "Export", "measurement": "Momentanverbrauch_Export", "field": "value"},
    ]
    # TRMNL configuration
    CHART_IMAGE_FILE = 'screen.png'
    TRMNL_DEVICE_MAC_COLLAPSED = 'F09E9E9A274C'



    TRMNL_BYOS_ROOT = '/app'
    CHART_OUTPUT_PATH = os.path.join(
    TRMNL_BYOS_ROOT,
    'public',
    'assets',
    'screens',
    TRMNL_DEVICE_MAC_COLLAPSED,
    CHART_IMAGE_FILE
    )


    TRMNL_WIDTH_PX = 800
    TRMNL_HEIGHT_PX = 480
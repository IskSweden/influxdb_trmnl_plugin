# TRMNL InfluxDB Chart Plugin

This plugin (`db_plugin`) is a Python-based chart generator integrated into the Terminus platform. It continuously generates and updates a **1-bit black-and-white PNG chart image** (`screen.png`) based on live power data from an **InfluxDB** instance. This image is used as the display output for a TRMNL device connected to the system.

![db_plugin](https://github.com/user-attachments/assets/6f85502e-368f-4b0e-a631-70a17a903585)



---

## File structure

```
terminus/
├── db_plugin/                # Python plugin logic lives here (external_plugin mount)
│   ├── app.py
│   ├── image_chart_generator.py
│   ├── data_fetcher.py
│   ├── plugin_config.py
│   └── requirements.txt
├── bin/
│   └── pollers/
│       └── image_chart       # Bash wrapper to run plugin every 60s
├── public/assets/screens/<MAC>/
│   └── screen.png            # Final chart consumed by TRMNL screen
├── compose.yml               # Defines docker services including image_chart
└── Dockerfile                # Uses python:3.11-slim as base for image_chart
```

## Docker integration
The plugin is run from a dedicated container (`image_chart`) defined in `compose.yml`:
```
  image_chart:
    image: python:3.11-slim
    volumes:
      - .:/app
      - ./db_plugin:/external_plugin
    command: /bin/bash -c "pip install -r /external_plugin/requirements.txt && while true; do python3 /external_plugin/app.py; sleep 60; done"
    depends_on:
      - web
    restart: unless-stopped

```
This command installs dependencies and runs the `app.py` entry point every 60 seconds.

---
# How it works

## Data fetching

- **File**: `data_fetcher.py`
    
- **Logic**: Connects to the configured InfluxDB instance using `InfluxDBClient` and pulls time-series data from measurements like:
    
    - `Momentanverbrauch_Import`
        
    - `Momentanverbrauch_Export`


## Chart Generation

- **File**: `image_chart_generator.py`

- **Logic**:
Uses `matplotlib` to draw a line chart of the past 60 minutes.
Saves it to a temporary `.png`, converts to 1-bit `.pbm`, then back to a final `.png` using `ImageMagick`.

 Final path: `public/assets/screens/F09E9E9A274C/screen.png`


## Image output

The generated image is saved using the MAC-specific path, e.g.:
 
`/app/public/assets/screens/F09E9E9A274C/screen.png`

File permissions are corrected using:
  `os.chown(...), os.chmod(...), os.utime(...)`
to ensure that TRMNL detects it as modified and refreshes the screen.

## Triggering Device Refresh

- The display reads from `/api/display` every ~60 seconds.
    
- However, due to TRMNL firmware behavior, it may only re-poll when:
    
    - A file timestamp changes
        
    - A forced refresh occurs
        
- This plugin handles timestamp updates to trigger that behavior.

---

# Configuration

### File: `plugin_config.py`

Contains centralized settings:


```python
INFLUXDB_HOST = '192.168.1.215' 
INFLUXDB_DATABASE = 'reader_62F64_SAM'
TRMNL_DEVICE_MAC_COLLAPSED = 'F09E9E9A274C' 
CHART_OUTPUT_PATH = ~/terminus/public/assets/screens/F09E9E9A274C/screen.png
TRMNL_WIDTH_PX = 800
TRMNL_HEIGHT_PX = 480
```

---

## Poller Integration

### File: `bin/pollers/image_chart`

```bash
#!/usr/bin/env bash
echo "[ImageChartPoller] Starting..." 
while true; do   
	echo "[ImageChartPoller] Running chart generator at $(date)..."
	python3 /external_plugin/app.py
	echo "[ImageChartPoller] Sleeping 60 seconds..."
	sleep 60 
done
```


---

## 📈 Refresh Verification

You can confirm updates via:

```bash
`watch stat public/assets/screens/F09E9E9A274C/screen.png`
```

You should see the `Modify` timestamp update every 60s.

Check logs:

```bash
docker compose logs -f image_chart
```

Check API exposure:
```bash
curl -s http://localhost:2300/api/display -H "ID: F0:9E:9E:9A:27:4C"`
```

---

## ⚠️ Known Issues

- TRMNL device may ignore timestamp updates unless firmware supports sub-minute polling.
    
- File permission errors (`EPERM`) may occur if container lacks write access.
    
- `convert` requires ImageMagick — ensure it’s installed in Docker base image.
    
- Changes to plugin code require restarting the `image_chart` container.
    

---

## 🧪 Tips

- Modify `plugin_config.py` for different time ranges or data series.
    
- To debug, disable cleanup in `generate_chart_image()` and inspect `_mpl_temp.png` and `_1bit_temp.pbm`

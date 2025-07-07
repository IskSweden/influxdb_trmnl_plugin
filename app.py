# ~/db_plugin/app.py

from plugin_config import AppConfig
from data_fetcher import InfluxDBFetcher
from image_chart_generator import ImageChartGenerator

def main():
    print("Starting data fetching and chart generation...")

    # 1. Fetch Data
    fetcher = InfluxDBFetcher(AppConfig)
    fetched_data = fetcher.fetch_data()
    print(f"Fetched Data: {fetched_data}")
    
    if fetched_data:
        print(f"Fetched Data: {fetched_data}")
        # 2. Generate Chart Image
        chart_generator = ImageChartGenerator(AppConfig) # Pass config only
        chart_generator.generate_chart_image(fetched_data)

        print("Pushing to TRMNL web server...")

    else:
        print("Failed to fetch data, skipping chart generation.")
    
    print("Process finished.")



if __name__ == "__main__":
    main()
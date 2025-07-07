# ~/db_plugin/influxdb_fetcher.py

from influxdb import InfluxDBClient
from datetime import datetime 

class InfluxDBFetcher: # Renamed class to follow convention
    def __init__(self, config):
        self.config = config
        self.influxdb_host = config.INFLUXDB_HOST
        self.influxdb_port = config.INFLUXDB_PORT
        self.influxdb_database = config.INFLUXDB_DATABASE
        self.data_series_configs = config.DATA_SERIES
        self.chart_time_range = config.CHART_TIME_RANGE
        self.client = None

    def connect(self):
        #Establishes a connection to the InfluxDB database.
        try:
            self.client = InfluxDBClient(
                host=self.influxdb_host,
                port=self.influxdb_port,
                database=self.influxdb_database
            )
            # Ping the database to ensure connection is live
            self.client.ping()
            print("Successfully connected to InfluxDB.")
        except Exception as e:
            print(f"Error connecting to InfluxDB at {self.influxdb_host}:{self.influxdb_port}/{self.influxdb_database}: {e}")
            self.client = None # Ensure client is None if connection fails to prevent usage of a bad client

    def disconnect(self):
        #Closes the InfluxDB client connection if it exists.
        if self.client:
            try:
                self.client.close()
                self.client = None
                print("Disconnected from InfluxDB.")
            except Exception as e:
                print(f"Error disconnecting from InfluxDB: {e}")

    def fetch_data(self):
        #Fetches aggregated data for all configured series from InfluxDB.
        #   
        all_series_data = {}

        try:
            self.connect()
            if not self.client: # If connection failed, self.client will be None
                return all_series_data # Return empty data immediately

            # Hardcoded 1-minute interval for fixed 60m range, 60 points
            group_by_interval = "1m"

            for series_config in self.data_series_configs:
                name = series_config["name"]
                measurement = series_config["measurement"]
                field = series_config["field"]

                query = (
                    f'SELECT MEAN("{field}") '
                    f'FROM "{measurement}" '
                    f'WHERE time > now() - {self.chart_time_range} '
                    f'GROUP BY time({group_by_interval}) FILL(none)'
                )
                print(f"Executing InfluxDB query for {name}: {query}")

                try:
                    result = self.client.query(query)
                    points = list(result.get_points(measurement=measurement))

                    series_data_points = []
                    for point in points:
                        if 'time' in point and 'mean' in point:
                            try:
                                time_str = point["time"]
                                value = float(point["mean"])
                                value_in_watt = value * 1000 # convert to wattage
                                time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                                series_data_points.append({
                                    "time": time_obj,
                                    "value": value_in_watt # Storing converted value
                                })
                            except (KeyError, ValueError) as err:
                                print(f"Skipping invalid point data for {name}: {point} -> {err}")
                        else:
                            print(f"Skipping point for {name} due to missing 'time' or 'mean' field: {point}")

                    # Sort data by time to ensure it's in chronological order for charting
                    series_data_points.sort(key=lambda x: x['time'])
                    all_series_data[name] = series_data_points
                    print(f"Fetched {len(series_data_points)} points for {name}.")

                except Exception as e:
                    print(f"Error querying {name}: {e}")
                    all_series_data[name] = [] # Ensure an empty list for this series on error

        except Exception as e: # Catch any errors during connect or main loop
            print(f"An unexpected error occurred during data fetching: {e}")

        finally:
            self.disconnect() # Ensure disconnect always happens

        return all_series_data
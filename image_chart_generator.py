# ~/db_plugin/image_chart_generator.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import subprocess
import base64

class ImageChartGenerator:

    def __init__(self, config):
        self.config = config
        self.output_path = config.CHART_OUTPUT_PATH
        self.chart_title = config.CHART_TITLE
        self.x_axis_label = config.CHART_X_AXIS_LABEL
        self.y_axis_label = config.CHART_Y_AXIS_LABEL
        self.trmnl_width_px = config.TRMNL_WIDTH_PX
        self.trmnl_height_px = config.TRMNL_HEIGHT_PX
        self.data_series_configs = config.DATA_SERIES
        self.mac = config.TRMNL_DEVICE_MAC_COLLAPSED
        self.image_file = config.CHART_IMAGE_FILE


    def generate_chart_image(self, fetched_data):
        """
        Generates a 1-bit black and white chart image from fetched data.
        Args:
            fetched_data (dict): Dictionary containing time series data.
        """

        if not fetched_data:
            print("No data to plot.")
            return
        
        plt.switch_backend('agg') # Use non-interactive backend for saving images
        
        # Calculate figure size in inches based on desired pixel dimensions at 100 DPI
        fig_width_inches = self.trmnl_width_px / 100
        fig_height_inches = self.trmnl_height_px / 100
        fig, ax = plt.subplots(figsize=(fig_width_inches, fig_height_inches), dpi=100) # Ensure 1:1 pixel mapping at 100 DPI

        # Set background to white
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        # Set all text and line colors to black (ensuring 1-bit B&W output)
        plt.rcParams['text.color'] = 'black'
        plt.rcParams['axes.labelcolor'] = 'black'
        plt.rcParams['xtick.color'] = 'black'
        plt.rcParams['ytick.color'] = 'black'
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.rcParams['grid.color'] = 'black'
        plt.rcParams['grid.alpha'] = 0.5 # A bit transparent for grid

        line_styles = ['-']

        for i, data in enumerate(self.data_series_configs):
            series_name = data['name']
            series_data = fetched_data.get(series_name, [])
            
            if not series_data:
                print(f"Warning: No data for series: {series_name}")
                continue
            
            # Extract timestamps and values
            timestamps = [point['time'] for point in series_data]
            values = [point['value'] for point in series_data]

            # Plot the data
            ax.plot(timestamps, values, label=series_name, 
                            linestyle=line_styles[i % len(line_styles)], 
                            color='black', linewidth=1.5, marker=None)
            
        # --- Chart Customization ---
        ax.set_title(self.chart_title, fontsize=16)
        ax.set_xlabel(self.x_axis_label, fontsize=12)
        ax.set_ylabel(self.y_axis_label, fontsize=12)

        # Format X-axis (Time)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) # Only show hour:minute
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10)) # Tick every 10 minutes
        fig.autofmt_xdate() # Automatically format date labels to prevent overlap

        # Add a simple legend
        ax.legend(frameon=False, loc='upper right', fontsize=10, facecolor='white', edgecolor='white')

        # Add grid
        ax.grid(True, linestyle=':', alpha=0.7)

        # Set tight layout to minimize padding
        plt.tight_layout()


        temp_mpl_output_path = None # Path for Matplotlib's initial PNG
        temp_pbm_output_path = None # Path for 1-bit PBM intermediate file

        try:

            temp_mpl_output_path = self.output_path.replace(".png", "_mpl_temp.png")
            
            # Save the Matplotlib plot to the temporary PNG
            plt.savefig(temp_mpl_output_path, dpi='figure', bbox_inches='tight', facecolor=fig.get_facecolor())
            print(f"Temporary Matplotlib PNG saved to {temp_mpl_output_path}")


            temp_pbm_output_path = self.output_path.replace(".png", "_1bit_temp.pbm")


            # Step 1: Convert PNG to 1-bit PBM
            subprocess.run([
                "convert", temp_mpl_output_path,
                "-resize", f"{self.trmnl_width_px}x{self.trmnl_height_px}!",
                "-monochrome",
                temp_pbm_output_path
            ], check=True)

            if not os.path.exists(temp_pbm_output_path):
                raise FileNotFoundError(f"PBM file was not created: {temp_pbm_output_path}")

            print(f"Intermediate 1-bit PBM created at {temp_pbm_output_path}")

            # Step 2: Convert PBM to final 1-bit PNG
            subprocess.run([
                "convert", temp_pbm_output_path,
                "-type", "bilevel",
                "-depth", "1",
                "-define", "png:color-type=0",
                self.output_path
            ], check=True)

            print(f"Final 1-bit chart image saved to {self.output_path}")

        except subprocess.CalledProcessError as e:
            print(f"ImageMagick error: {e}")
        except FileNotFoundError as e:
            print(f"File creation error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            plt.close(fig)
            if temp_mpl_output_path and os.path.exists(temp_mpl_output_path):
                os.remove(temp_mpl_output_path)
                print(f"Cleaned up: {temp_mpl_output_path}")
            if temp_pbm_output_path and os.path.exists(temp_pbm_output_path):
                os.remove(temp_pbm_output_path)
                print(f"Cleaned up: {temp_pbm_output_path}")
"""
Outputs three text files in the current directory.

Requirements: pandas (as of now, need to be looked further)
  pip install pandas ??

This Python code is for reading the directory, reading as well as loading
the CSV Files from the targeted directory. (Multi-year, multi-station temperature analytics)

After that, the next step will be to add months and their respective seasons. 
so that it reads all CSVs from ./temperatures/, computes:
 1) Seasonal average temperatures (AU seasons)
 2) Station(s) with largest overall temperature range (max - min)
 3) Temperature stability: stations with min/max std dev

We will also choose our destination target names for: Average Temperature, Largest Temperature
Range as well as Temperature Stability Stations. For now the output will  directly be on the root.




CODEEEEEEEEEE
Option 1:
The best and first way to read, extract and load the data files in order to get the
information would be to use a function with a For Loop and expect where the problems might arise beoforehand.

"""


DATA_DIR = "temperatures"   # folder containing stations_group_YYYY.csv
OUTPUT_AVG = "average_temp.txt"
OUTPUT_RANGE = "largest_temp_range_station.txt"
OUTPUT_STABILITY = "temperature_stability_stations.txt"

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

SEASON_MAP = {
    # Southern Hemisphere seasons
    "December": "Summer", "January": "Summer", "February": "Summer",
    "March": "Autumn", "April": "Autumn", "May": "Autumn",
    "June": "Winter", "July": "Winter", "August": "Winter",
    "September": "Spring", "October": "Spring", "November": "Spring",
}
SEASON_ORDER = ["Summer", "Autumn", "Winter", "Spring"]  # output order

ID_COLS = ["STATION_NAME", "STN_ID", "LAT", "LON"]



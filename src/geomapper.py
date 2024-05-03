import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point
from dotenv import load_dotenv
import os

def fetch_coordinates(api_key, address):
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": address,
        "inputtype": "textquery",
        "fields": "formatted_address,name,business_status,geometry",
        'key': api_key
    }
    response = requests.get(base_url, params=params)
    result = response.json()
    print(result)
    if result['status'] == 'OK':
        location = result['candidates'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None  # Handle errors or no results appropriately

# Load the shapefile
gdf = gpd.read_file("data/supervisory_district_data/geo_export_184b7eec-1746-4e9d-8d73-acdce90a99f1.shp")

load_dotenv()

api_key = os.getenv('PLACES_API_KEY')
address = '840 Brannan St, San Francisco, CA 94103'  # An example place

# Fetch coordinates
latitude, longitude = fetch_coordinates(api_key, address)

# # Create a DataFrame with the fetched coordinates
df = pd.DataFrame([{'latitude': latitude, 'longitude': longitude}])

# # Create Point geometries from latitude and longitude
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
points_gdf = gpd.GeoDataFrame(df, geometry='geometry')


# # Ensure both GeoDataFrames use the same CRS
points_gdf.crs = gdf.crs

# # Perform spatial join
joined_gdf = gpd.sjoin(points_gdf, gdf, how="inner", predicate='intersects')

print(joined_gdf.to_markdown())

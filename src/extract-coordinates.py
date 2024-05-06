import geopandas as gpd

# Load the shapefile
gdf = gpd.read_file("data/supervisory_district_data/geo_export_184b7eec-1746-4e9d-8d73-acdce90a99f1.shp")

# Function to extract a sample coordinate from the geometry
def extract_sample_coordinate(geometry):
    if geometry.geom_type == 'Polygon':
        return list(geometry.exterior.coords)[0]  # Return the first coordinate of the polygon
    elif geometry.geom_type == 'MultiPolygon':
        # Return the first coordinate of the first polygon in the MultiPolygon
        return list(geometry.geoms[0].exterior.coords)[0]

# Apply the function to extract coordinates
gdf['sample_coordinate'] = gdf['geometry'].apply(extract_sample_coordinate)

# Print 'sup_dist' and 'sample_coordinate' columns
print(gdf[['sup_dist', 'sample_coordinate']])

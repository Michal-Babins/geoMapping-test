from typing import Dict
import geopandas as gpd
from dotenv import load_dotenv
import os
import psycopg2
from shapely.geometry import mapping
import shapely
# Load the shapefile
gdf = gpd.read_file("data/supervisory_district_data/geo_export_184b7eec-1746-4e9d-8d73-acdce90a99f1.shp")

class DatabaseConfig:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file

    @property
    def base(self):
        return os.getenv('DB_BASE')

    @property
    def user(self):
        return os.getenv('DB_USER')

    @property
    def database(self):
        return os.getenv('DB_DATABASE')

    @property
    def port(self):
        return os.getenv('DB_PORT')

    @property
    def password(self):
        return os.getenv('DB_PASSWORD')
    
    @property
    def connection_string(self):
        return f"host={os.getenv('DB_BASE')} dbname={os.getenv('DB_DATABASE')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')} port={os.getenv('DB_PORT')}"

    def create_connection(self):
        try:
            conn = psycopg2.connect(self.connection_string)
            print("Connection established")
            return conn
        except Exception as e:
            print(f"Unable to connect to the database: {e}")


def shapefile_manager(gdf,file_name):

    # Convert geometry using shapely
    gdf['geom'] = gdf['geometry'].apply(lambda geom: mapping(geom))

    # gdf['geom'] = gdf['geometry']

    gdf.rename(columns={'sup_dist_n': 'spacial_name'}, inplace=True)

    gdf['source'] = file_name

    return gdf

def create_spatial_data_table(cursor,conn):
    create_table_command = """
        CREATE EXTENSION IF NOT EXISTS postgis;
        CREATE TABLE spacial_data (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            spacial_name VARCHAR(255),
            source VARCHAR(255),
            geom GEOMETRY(Point, 4326),
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    cursor.execute(create_table_command)
    conn.commit()
    


if __name__=="__main__":
    config = DatabaseConfig()
    connection = config.create_connection()

    file_path = "data/supervisory_district_data/geo_export_184b7eec-1746-4e9d-8d73-acdce90a99f1.shp"
    #read in file
    gdf = gpd.read_file(file_path)

    file_name = file_path.split('/')[-1]

    shape_gdf = shapefile_manager(gdf,file_name)

    cursor = connection.cursor()

    # create_spatial_data_table(cursor, connection)

    for index, row in gdf.iterrows():
        # Convert the Shapely geometry back to WKT format for insertion
        wkt_geom = shapely.geometry.shape(row['geom']).wkt
        
        cursor.execute(
            "INSERT INTO spacial_data (spacial_name, source, geom) VALUES (%s, %s, ST_GeomFromText(%s, 4326))",
            (row['spacial_name'], row['source'], wkt_geom)
        )
    connection.commit()

    cursor.close()
    connection.close()
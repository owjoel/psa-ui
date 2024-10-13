import os
import sys
import pandas as pd
from pymongo import MongoClient, errors
from pymongo.database import Database
from datetime import datetime
from urllib.parse import quote_plus

# MongoDB connection
def db_init():
    global client
    global db
    host: str = os.getenv('MONGO_HOST')
    port: str = os.getenv('MONGO_PORT')
    username: str = os.getenv('MONGO_USERNAME')
    password: str = os.getenv('MONGO_PASSWORD')
    uri = "mongodb://%s:%s@%s:%s" % (
        quote_plus(username), quote_plus(password), quote_plus(host), quote_plus(port))
    try:
        client = MongoClient(uri)
        db = client['dev']
        collection = db['allocations']
        print(f"MongoDB client connected")
    except errors.ConnectionFailure:
        sys.exit(1)


client: MongoClient
db: Database
db_init()

# LOAD DOCKEDSHIPS DATA
file_path = './data/combined_vessel_data.csv'
df = pd.read_csv(file_path)

# Transform DataFrame into JSON
def get_docked_ships_json(df):
    records = []
    for _, row in df.iterrows():
        record = {
            "IMO": row['IMO'] if pd.notnull(row['IMO']) else None,
            "ATA": datetime.strptime(row['Actual Arrival Time'], '%Y/%m/%d %H:%M') if pd.notnull(row['Actual Arrival Time']) else None,
            "ShipType": row['Ship Type'] if pd.notnull(row['Ship Type']) else None,
            "ETD": datetime.strptime(row['Estimated Departure Time'], '%Y/%m/%d %H:%M') if pd.notnull(row['Estimated Departure Time']) else None,
            "Berth_id": row['Berth'] if pd.notnull(row['Berth']) else None
        }
        records.append(record)
    return records

# Batch insert DockedShips
def batch_insert_dockedships(records):
    if records:
        db.DockedShips.insert_many(records)

# Transform CSV data into JSON format for DockedShips
json_records_dockedships = get_docked_ships_json(df)

# Insert into MongoDB for DockedShips
batch_insert_dockedships(json_records_dockedships)
print(f"Inserted {len(json_records_dockedships)} records into the DockedShips collection.")


# LOAD BERTH DATA
file_path_berth = './data/BerthInfo.csv'
df_berth = pd.read_csv(file_path_berth)

def get_berth_json(df_berth):
    records = []
    for index, row in df_berth.iterrows():
        try:
            record = {
                "BerthCode": row['Berth'] if pd.notnull(row['Berth']) else None,
                "BerthLength": row['BerthLength'] if pd.notnull(row['BerthLength']) else None,
                "MaxDraft": float(row['MaxDraft']) if pd.notnull(row['MaxDraft']) else None,
                "MaxLOA": float(row['MaxLOA']) if pd.notnull(row['MaxLOA']) else None,
                "Terminal_id": "HKTERM",  # Assuming no Terminal_id is provided, default to None
                "EstimatedWaitTime": None,  # No data provided for EstimatedWaitTime
            }
            records.append(record)
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue  # Skip the row if an error occurs
    return records

# Batch insert Berth data
def batch_insert_berth(records):
    if records:
        db.Berth.insert_many(records)
        print(f"Inserted {len(records)} records into the Berth collection.")

json_records_berths = get_berth_json(df_berth)
batch_insert_berth(json_records_berths)

append_file = "./data/unique_imo_data.csv"

df = pd.read_csv(append_file)
for _, row in df.iterrows():
    result = db.DockedShips.find_one_and_update(
        { "IMO": str(row['IMO']) },
        { "$set": { "BerthDelay": row['ATA_berth_delay'] } }
    )
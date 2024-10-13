import joblib
import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient, errors
from pymongo.database import Database
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
eta_model = joblib.load('WT.pkl')
waiting_time_model = joblib.load()

encodeMapping = {
    'Container': 0,
    'GENERAL / HEAVY LIFT CARGO': 1,
    'LIQUIFIED NATURAL GAS TANKER': 2,
    'LIQUIFIED PETROLEUM GAS TANKER': 3,
    'TANKER (CRUDE,FUEL,DIESEL,LUB)': 4
}

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
        print(f"MongoDB client connected")
    except errors.ConnectionFailure:
        sys.exit(1)

# Initialize the connection
client: MongoClient
db: Database

db_init()

def predict_eta(data):
    return eta_model.predict(data)

def get_lowest_wt_berth():
    berth_waiting_times = {port: 0 for port in db.Berth.find().distinct('Berth_id')}
    
    ships_in_port = get_ships_in_port()

    for berth in berth_waiting_times:
        total_waiting_time = 0
        for ship in db.DockedShips.find({"PortCode": port}):  # Assuming a 'PortCode' field is available
            features = get_input_features(ship, berth, ships_in_port)
            total_waiting_time += waiting_time_model.predict([features])[0]
        berth_waiting_times[port] = total_waiting_time

    min_waiting_time_port = None
    min_waiting_time = float('inf')
    for port, waiting_time in berth_waiting_times.items():
        if waiting_time < min_waiting_time:
            min_waiting_time = waiting_time
            min_waiting_time_port = port
        elif waiting_time == min_waiting_time and min_waiting_time == 0:
            min_waiting_time_port = port
    
    return min_waiting_time_port

def get_input_features(ship, berth, ships_in_port):
    features = []

    shipType = encodeMapping.get(ship.ShipType, 0) 
    length, gt, breadth = get_ship_features(ship.IMO)
    
    ata_shift = get_shift(ship.ATA)
    etd_shift = get_shift(ship.ETD)
    
    ata_autumn, ata_spring, ata_summer, ata_winter = get_season(ship.ATA)
    etd_autumn, etd_spring, etd_summer, etd_winter = get_season(ship.ETD)
    
    
    ata_fri,ata_mon,ata_sat,ata_sun,ata_thurs,ata_tues, ata_wed = get_day(ship.ATA)
    etd_fri,etd_mon,etd_sat,etd_sun,etd_thurs,etd_tues, etd_wed = get_day(ship.ETD)
    
    max_draft, max_loa, berth_length= get_berth_features(berth.BerthCode)

    expected_waiting_time = get_expected_waiting_time(ship.ETD,ship.ATA)
    berth_delay = ship.BerthDelay if hasattr(ship, 'BerthDelay') and ship.BerthDelay is not None else 0
    features.append(
        shipType,
        ship.MaxVesselDraft,
        max_draft, max_loa, berth_length,
        ata_fri, ata_mon, ata_sat, ata_sun, ata_thurs, ata_tues, ata_wed,
        etd_fri, etd_mon, etd_sat, etd_sun, etd_thurs, etd_tues, etd_wed, 
        ata_shift, etd_shift,
        ata_autumn, ata_spring, ata_summer, ata_winter,
        etd_autumn, etd_spring, etd_summer, etd_winter,
        ships_in_port,
        length, gt, breadth,
        expected_waiting_time,
        ship.Berth_delay
            )
    
    return features

def get_ship_features(IMO):
    url = f"https://www.balticshipping.com"

    payload = {
                "request[0][module]": "ships",
                "request[0][action]": "list",
                "request[0][data][1][name]": "imo",
                "request[0][data][1][value]": IMO
            }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            ship_data = data['data']['request'][0]['ships'][0]['data']
            length = ship_data.get('length', 'N/A')
            gt = ship_data.get('gt', 'N/A')
            breadth = ship_data.get('breadth', 'N/A')
        return length, gt, breadth
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for IMO {IMO}: {http_err} (Status Code: {response.status_code})")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for IMO {IMO}: {req_err}")
    except KeyError:
        print(f"Data parsing error: Expected keys not found in response for IMO {IMO}")
    except json.JSONDecodeError:
        print(f"JSON decoding error for IMO {IMO}: Unable to parse response as JSON")
    except Exception as e:
        print(f"An unexpected error occurred for IMO {IMO}: {e}")

def get_day(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    
    day_name = date.day_name()
    
    mon = tues = wed = thurs = fri = sat = sun = 0
    
    if day_name == 'Monday':
        mon = 1
    elif day_name == 'Tuesday':
        tues = 1
    elif day_name == 'Wednesday':
        wed = 1
    elif day_name == 'Thursday':
        thurs = 1
    elif day_name == 'Friday':
        fri = 1
    elif day_name == 'Saturday':
        sat = 1
    elif day_name == 'Sunday':
        sun = 1
    
    return fri, mon, sat, sun, thurs, tues, wed

def get_shift(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    hour = date.hour
    if 0 <= hour < 8:
        return 1 
    elif 8 <= hour < 16:
        return 2 
    else:
        return 3 

def get_season(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    month = date.month

    autumn = spring = summer = winter = 0

    if month in [12, 1, 2]:
        winter = 1
    elif month in [3, 4, 5]:
        spring = 1
    elif month in [6, 7, 8]:
        summer = 1
    else:  # autumn
        autumn = 1

    return autumn, spring, summer, winter
    
# need to implement
def get_berth_features(berth_code):
    result = db.Berth.find_one({ 'BerthCode': berth_code }, { 'MaxDraft': 1, 'MaxLOA': 1, 'BerthLength': 1, '_id': 0 })
    if result:
        max_draft = result.get('MaxDraft')
        max_loa = result.get('MaxLOA')
        berth_length = result.get('BerthLength')
        print(f"MaxDraft: {max_draft}, MaxLOA: {max_loa}, BerthLength: {berth_length}")
    else:
        print(f"No berth found for BerthCode: {berth_code}")

def get_expected_waiting_time(etd_str, ata_str):
    # Define the format of the datetime strings
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Convert the strings into datetime objects
    etd = datetime.strptime(etd_str, date_format)
    ata = datetime.strptime(ata_str, date_format)
    
    # Calculate the difference in hours
    waiting_time = (etd - ata).total_seconds() / 3600

    return waiting_time

def get_ships_in_port():
    # Get the number of ships currently in port
    return db.DockedShips.count_documents({})

get_lowest_wt_berth()
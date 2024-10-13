import joblib
import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient, errors
from pymongo.database import Database
import os
# from dotenv import load_dotenv
from urllib.parse import quote_plus
import pandas as pd
import random

# load_dotenv()
eta_model = joblib.load('eta_model.joblib')
eta_scaler = joblib.load('eta_scaler.joblib')
# waiting_time_model = joblib.load('WT.pkl')
# wt_scaler = joblib.load('WTscaler.pkl')

expected_columns = ['Ship Type', 'Vessel Max Draft', 'MaxDraft', 'MaxLOA', 'BerthLength', 'ATA_day_Friday', 'ATA_day_Monday', 'ATA_day_Saturday', 'ATA_day_Sunday', 'ATA_day_Thursday', 'ATA_day_Tuesday', 'ATA_day_Wednesday', 'EDT_day_Friday', 'EDT_day_Monday', 'EDT_day_Saturday', 'EDT_day_Sunday', 'EDT_day_Thursday', 'EDT_day_Tuesday', 'EDT_day_Wednesday', 'ATA_shift', 'EDT_shift', 'ATA_season_autumn', 'ATA_season_spring', 'ATA_season_summer', 'ATA_season_winter', 'EDT_season_autumn', 'EDT_season_spring', 'EDT_season_summer', 'EDT_season_winter', 'ATA_inport', 'Length', 'Gross Tonnage', 'Breadth', 'ATA_berth_delay', 'Expected Waiting time']

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
# db_init()

def predict_eta(data):
    scaled_data = eta_scaler.transform(data)
    return eta_model.predict(scaled_data)

def predict_lowest_wt_berth():
    random_values = ['HKELECT(N)','KC1','HKTERM']
    #return any of these
    return (random.choice(random_values), 0.5)
    berth_waiting_times = {berth: 0 for berth in db.Berth.find().distinct('BerthCode')}
    print(f"Berth waiting times: {berth_waiting_times}")
    ships_in_port = get_ships_in_port()
    print(f"Ships in port: {ships_in_port}")
    for berth in berth_waiting_times:
        total_waiting_time = 0
        print(f"Calculating waiting time for berth {berth}")
        for ship in db.DockedShips.find({"Berth_id": berth}):
            print(f"Calculating waiting time for ship {ship}")
            features = get_input_features(ship, berth, ships_in_port)
            features_df = pd.DataFrame([features], columns=expected_columns)
            features_df = features_df[expected_columns]
            #scale the features with scaler
            scaled_features = wt_scaler.transform(features_df)
            #check shape of features
            print(scaled_features.shape)
            total_waiting_time += waiting_time_model.predict(scaled_features)[0]
        berth_waiting_times[berth] = total_waiting_time

    min_waiting_time_berth = None
    min_waiting_time = float('inf')
    for berth, waiting_time in berth_waiting_times.items():
        print(f"Checking berth {berth} with waiting time {waiting_time}")
        if waiting_time < min_waiting_time:
            min_waiting_time = waiting_time
            min_waiting_time_berth = berth
            print(f"New minimum waiting time found: {min_waiting_time} at berth {berth}")  
        elif waiting_time == min_waiting_time and min_waiting_time == 0:
            min_waiting_time_berth = berth
            print(f"Multiple ports with waiting time 0, selecting {berth}")
    print("Lowest waiting time port:", min_waiting_time_berth)
    

def get_input_features(ship, berth, ships_in_port):
    features = []

    shipType = encodeMapping.get(ship.get('ShipType'), 0) 
    length, gt, breadth = get_ship_features(ship.get('IMO'))
    ata = ship.get('ATA')
    etd = ship.get('ETD')
    ata_shift = get_shift(ata)
    etd_shift = get_shift(etd)
    
    ata_autumn, ata_spring, ata_summer, ata_winter = get_season(ata)
    etd_autumn, etd_spring, etd_summer, etd_winter = get_season(etd)
    
    
    ata_fri,ata_mon,ata_sat,ata_sun,ata_thurs,ata_tues, ata_wed = get_day(ata)
    etd_fri,etd_mon,etd_sat,etd_sun,etd_thurs,etd_tues, etd_wed = get_day(etd)
    
    max_draft, max_loa, berth_length= get_berth_features(berth)
    maxVesselDraft = ship.get('MaxVesselDraft', 15) if ship.get('MaxVesselDraft') is not None else 15
    expected_waiting_time = get_expected_waiting_time(etd,ata)
    berth_delay = ship.get('BerthDelay', 0) if ship.get('BerthDelay') is not None else 0
    features.extend([
        shipType,
        maxVesselDraft,
        max_draft, max_loa, berth_length,
        ata_fri, ata_mon, ata_sat, ata_sun, ata_thurs, ata_tues, ata_wed,
        etd_fri, etd_mon, etd_sat, etd_sun, etd_thurs, etd_tues, etd_wed, 
        ata_shift, etd_shift,
        ata_autumn, ata_spring, ata_summer, ata_winter,
        etd_autumn, etd_spring, etd_summer, etd_winter,
        ships_in_port,
        length, gt, breadth,
        expected_waiting_time,
        berth_delay
            ])
    
    return features

def get_ship_features(IMO):
    print(IMO)
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
            print('data:', data)
            print('Ship data:', length, gt, breadth)
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

    return 150, 8627, 35

def get_day(date):
    
    day_name = date.weekday()
    
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

def get_shift(date):
    if date is None:
        print("Error: Date is None")
        return 2
    
    hour = date.hour
    if 0 <= hour < 8:
        return 1 
    elif 8 <= hour < 16:
        return 2 
    else:
        return 3

def get_season(date):
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
        return max_draft, max_loa, berth_length
    else:
        print(f"No berth found for BerthCode: {berth_code}")

def get_expected_waiting_time(etd_str, ata_str):
    
    # Calculate the difference in hours
    waiting_time = (etd_str - ata_str).total_seconds() / 3600

    return waiting_time

def get_ships_in_port():
    # Get the number of ships currently in port
    return db.DockedShips.count_documents({})
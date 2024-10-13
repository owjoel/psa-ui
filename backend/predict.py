import joblib
import requests
import json
from datetime import datetime
from pymongo import MongoClient

eta_model = joblib.load('WT.pkl')
waiting_time_model = joblib.load()

def get_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dev']  # Replace with your database name
    return db
# Initialize the connection
db = get_db()

def predict_eta(data):
    return eta_model.predict(data)

def predict_waiting_time():
    min_waiting_time = float('inf')
    
    #Get total ships in port
    ships_in_port = 0
    # For each berth
        # initiaize sum = 0
        # Ships = getBerthShips(berthId)
        # For ship in Ships
            features = get_input_features(ship, berth, ships_in_port)
            sum+= waiting_time_model.predict(features)
        #
    return waiting_time_model.predict(data)

def get_intput_features(ship, berth, ships_in_port):
    features = []
    
    length, gt, breadth = get_ship_features(ship.IMO)
    
    ata_shift = get_shift(ship.ATA)
    etd_shift = get_shift(ship.ETD)
    
    ata_autumn, ata_spring, ata_summer, ata_winter = get_season(ship.ATA)
    etd_autumn, etd_spring, etd_summer, etd_winter = get_season(ship.ETD)
    
    
    ata_fri,ata_mon,ata_sat,ata_sun,ata_thurs,ata_tues, ata_wed = get_day(ship.ATA)
    etd_fri,etd_mon,etd_sat,etd_sun,etd_thurs,etd_tues, etd_wed = get_day(ship.ETD)
    
    max_draft, max_loa, berth_length= get_berth_features(berth.BerthCode)

    expected_waiting_time = get_expected_waiting_time(ship.ETD,ship.ATA)

    features.append(
        int(ship.ShipType),
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
    
    waiting_time = waiting_time_model.predict(*features)
    print(waiting_time)
    return waiting_time

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

def get_ships_at_port():
    ships = 0
    
    # Get all ships at port


    return ships

def get_expected_waiting_time(etd_str, ata_str):
    # Define the format of the datetime strings
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Convert the strings into datetime objects
    etd = datetime.strptime(etd_str, date_format)
    ata = datetime.strptime(ata_str, date_format)
    
    # Calculate the difference in hours
    waiting_time = (etd - ata).total_seconds() / 3600

    return waiting_time
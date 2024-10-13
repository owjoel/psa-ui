import os
import sys
import models

from concurrent.futures import ProcessPoolExecutor
from predict import predict_eta, predict_lowest_wt_berth
from models import ShipData, db_init
from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
from pymongo.collection import Collection
# from dotenv import load_dotenv
# from predict import predict_waiting_time
import numpy as np
from flask_cors import CORS

# PLEASE UNCOMMENT EVERYTHING IM COMMENTED TO ALLOW MONGODB
# load_dotenv()

# FLASK
app = Flask(__name__)
client: MongoClient
collection: Collection
CORS(app)

collection: Collection

@app.get('/health')
def health_check():
    return jsonify({ "message": "Active" })

@app.post('/allocation')
def allocate_ship():
    try:
        # marshal JSON
        data = request.get_json(silent=True)
        if not data:
            return jsonify({ "error": "Invalid JSON" }), 400
        ship_data = ShipData.from_dict(data)
        print(ship_data)

        # run both models
        with ProcessPoolExecutor() as executor:
            f1 = executor.submit(predict_eta, ship_data)
            f2 = executor.submit(predict_waiting_time)

            r1 = f1.result()
            r2 = f2.result()
        
        # Store in DB
        print(r1, r2)

        return jsonify(ship_data.to_dict()), 200
    
    except Exception as e:
        print(e)
        return jsonify({ "error": "We encountered an error" }), 500
    
@app.route('/eta-predict', methods=['POST'])
def predict():
    ships = request.json.get('ships', [])
    results = []

    # Process each ship in the list
    for ship in ships:
        features = [
            ship['LAT'],
            ship['LON'],
            ship['SOG'],
            ship['COG'],
            ship['Heading'],
            ship['Length'],
            ship['Width'],
            ship['Draft'],
            ship['distanceToPort']
        ]
        features_array = np.array([features])
        eta = predict_eta(features_array)[0]
        results.append({'name': ship['name'], 'eta': float(eta)})
    
    return jsonify(results)

@app.route('/predict_lowest_wt_berth', methods=['POST'])
def predict_lowest_wt_berth_endpoint():
    try:
        berth, wait_time = predict_lowest_wt_berth()
        return jsonify({"berth": berth, "waiting_time": wait_time})
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to predict lowest waiting time berth"}), 500


# DATABASE

if __name__ == "__main__":
    # db_init()
    app.run(debug=False, )
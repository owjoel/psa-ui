import os
import sys

from concurrent.futures import ProcessPoolExecutor
from predict import predict_eta, predict_waiting_time
from models import ShipData
from urllib.parse import quote_plus
from flask import Flask, request, jsonify
# from pymongo import MongoClient, errors
# from pymongo.collection import Collection
# from dotenv import load_dotenv
from predict import predict_eta, predict_waiting_time
import numpy as np
from flask_cors import CORS

# PLEASE UNCOMMENT EVERYTHING IM COMMENTED TO ALLOW MONGODB
# load_dotenv()

# FLASK
app = Flask(__name__)
# client: MongoClient
# collection: Collection
CORS(app)

@app.get('/health')
def health_check():
    return jsonify({ "message": "Active" })

# @app.post('/allocation')
# def allocate_ship():
#     try:
#         data = request.get_json(silent=True)
#         if not data:
#             return jsonify({ "error": "Invalid JSON" }), 400
#         ship_data = ShipData.from_dict(data)
#         print(ship_data)

#         with ProcessPoolExecutor() as executor:
#             f1 = executor.submit(predict_eta, ship_data)
#             f2 = executor.submit(predict_waiting_time)

#         return jsonify(ship_data.to_dict()), 200
    
#     except Exception as e:
#         print(e)
#         return jsonify({ "error": "We encountered an error" }), 500
    
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


# DATABASE
# def db_init():
#     global client
#     global collection
#     host: str = os.getenv('MONGO_HOST')
#     port: str = os.getenv('MONGO_PORT')
#     username: str = os.getenv('MONGO_USERNAME')
#     password: str = os.getenv('MONGO_PASSWORD')
#     uri = "mongodb://%s:%s@%s:%s" % (
#         quote_plus(username), quote_plus(password), quote_plus(host), quote_plus(port))
#     try:
#         client = MongoClient(uri)
#         db = client['dev']
#         collection = db['allocations']
#         print(f"MongoDB client connected")
#     except errors.ConnectionFailure:
#         sys.exit(1)

if __name__ == "__main__":
    # db_init()
    app.run(debug=False, )
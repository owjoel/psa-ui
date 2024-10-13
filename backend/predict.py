import joblib

eta_model = joblib.load('eta_model.joblib')
eta_scaler = joblib.load('eta_scaler.joblib')
waiting_time_model = joblib.load('eta_model.joblib') # change this @Axel

def predict_eta(data):
    scaled_data = eta_scaler.transform(data)
    return eta_model.predict(scaled_data)

def predict_waiting_time(data):
    return waiting_time_model.predict(data)
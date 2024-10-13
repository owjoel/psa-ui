import joblib

eta_model = None
waiting_time_model = None

def predict_eta(data):
    return eta_model.predict(data)

def predict_waiting_time(data):
    return waiting_time_model.predict(data)
import joblib

eta_model = joblib.load()
waiting_time_model = joblib.load()

def predict_eta(data):
    return eta_model.predict(data)

def predict_waiting_time(data):
    return waiting_time_model.predict(data)
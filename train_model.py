import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

#1. Loading the data we created
print("InsightOps: Loading server data...")
df = pd.read_csv('server_data.csv')

# 2. Selecting the features to track
# Note that we don't give it the 'label' column, 
# so that it can learn to identify anomalies on its own (Unsupervised Learning)
features = ['cpu_usage', 'memory_usage', 'errors', 'latency']
X = df[features]

# 3. Model creation
# contamination=0.1 tells the model to expect about 10% of outliers
model = IsolationForest(contamination=0.1, random_state=42)

#4. Model Training
print("InsightOps: Training the anomaly detection model... This will take a moment.")
model.fit(X)
# 5. Saving the model to a file
# This is the most important step - this file is the ready-made "brain" that we will use in the API and the agent
joblib.dump(model, 'anomaly_detector.pkl')

print("Success! The model has been trained and saved as: anomaly_detector.pkl")
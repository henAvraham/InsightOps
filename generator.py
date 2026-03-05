import pandas as pd
import numpy as np
import random

def generate_server_data(rows=1000):
    data = []
    for i in range(rows):
        # Normal mode most of the time
        cpu = random.uniform(10, 40)
        memory = random.uniform(200, 500)
        errors = random.randint(0, 2)
        latency = random.uniform(10, 50)
        is_anomaly = 0
        
        # Once every 100 lines we will create a "fault"
        if i % 100 == 0:
            cpu = random.uniform(85, 100) # jump in the cpu
            errors = random.randint(20, 50) #lots of errors
            latency = random.uniform(500, 2000) # Terrible slowness
            is_anomaly = 1
            
        data.append([cpu, memory, errors, latency, is_anomaly])
    
    df = pd.DataFrame(data, columns=['cpu_usage', 'memory_usage', 'errors', 'latency', 'label'])
    df.to_csv('server_data.csv', index=False)
    print("the file server_data.csv created successfully")

generate_server_data()
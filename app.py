import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import joblib
from sklearn.metrics import mean_squared_error, r2_score
sns.set(style="whitegrid")
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load the trained model
model_path = r"C:\Users\pavan\Downloads\random_forest_model.pkl"
model = joblib.load(model_path)

# Feature names
feature_names = ['Time on App', 'Time on Website', 'Length of Membership', 'Avg. Session Length']

# Ensure 'static' folder exists for saving plots
static_folder = os.path.join(os.getcwd(), "static")
os.makedirs(static_folder, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html', username=session.get("username"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            session["username"] = username  # Store username in session
            return redirect(url_for('home'))
        return "Missing username or password", 400
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            session["username"] = username  # Store username in session
            return redirect(url_for('home'))
        return "Missing username or password", 400
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('home'))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values
        input_data = [float(request.form[feature]) for feature in feature_names]
        input_array = np.array(input_data).reshape(1, -1)

        # Make prediction
        prediction = model.predict(input_array)[0]

        # Simulating actual value (Replace with real dataset values if available)
        actual_value = prediction * 1.05  # Example: Assume actual value is 5% higher

        # Compute Metrics
        mse = mean_squared_error([actual_value], [prediction])
        rmse = np.sqrt(mse)

        # Compute R² Score (Handle division by zero case)
        if actual_value == prediction:
            r2 = 0.0  # If no variation, R² is zero
        else:
            r2 = r2_score([actual_value], [prediction])

        # Generate a graph
        plt.figure(figsize=(6, 4))
        plt.bar(feature_names, input_data, color=['blue', 'green', 'red', 'orange'])
        plt.xlabel("Features")
        plt.ylabel("Values")
        plt.title("Input Features for Prediction")

        # Save the graph
        graph_path = os.path.join(static_folder, "prediction_plot.png")
        plt.savefig(graph_path)
        plt.close()

        return render_template('index.html', 
                               prediction_text=f'Predicted Yearly Amount Spent: ${prediction:.2f}',
                               mse_text=f'MSE: {mse:.4f}',
                               rmse_text=f'RMSE: {rmse:.4f}',
                               r2_text=f'R² Score: {r2:.4f}',
                               graph_url=url_for('static', filename='prediction_plot.png'),
                               username=session.get("username"))
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)

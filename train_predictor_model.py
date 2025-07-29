"""
================================================================
AI Model Training Script for LEO Link Delay Prediction
================================================================
This script reads the generated link data, trains an XGBoost
regression model to predict link delay, evaluates its performance,
and saves the trained model for future use.
"""
import time
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def train_model():
    # --- 1. Load Data ---
    data_file = 'isl_link_data.csv'
    print(f"--- Loading data from {data_file} ---")
    try:
        df = pd.read_csv(data_file)
        # For a quicker test, you can use a sample of the data
        # df = pd.read_csv(data_file, nrows=100000)
    except FileNotFoundError:
        print(f"ERROR: Data file not found. Please run 'generate_ai_data.py' first.")
        return

    print(f"Data loaded successfully. Shape: {df.shape}")

    # --- 2. Feature Engineering & Data Preparation ---
    print("\n--- Preparing data for training ---")
    # Our features are all columns except the satellite IDs (which are just identifiers)
    # and the label 'actual_delay'.
    features = ['time_slot', 'is_inter_plane']
    label = 'actual_delay'

    X = df[features]
    y = df[label]

    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training data size: {X_train.shape[0]} samples")
    print(f"Testing data size: {X_test.shape[0]} samples")

    # --- 3. Model Training ---
    print("\n--- Training XGBoost Regressor model ---")
    start_time = time.time()

    # Initialize the XGBoost model with some basic parameters
    # n_estimators: number of boosting rounds
    # max_depth: max depth of a tree
    # learning_rate: step size shrinkage
    # objective: defines the loss function
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=7,
        learning_rate=0.1,
        n_jobs=-1, # Use all available CPU cores
        random_state=42
    )

    # Train the model
    model.fit(X_train, y_train)

    end_time = time.time()
    print(f"Model training finished in {end_time - start_time:.2f} seconds.")

    # --- 4. Model Evaluation ---
    print("\n--- Evaluating model performance on the test set ---")
    
    # Make predictions on the test data
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"  Mean Absolute Error (MAE): {mae:.6f} s")
    print(f"  R-squared (R2) Score:    {r2:.4f}")
    print("\nEvaluation notes:")
    print("  - MAE: The average absolute difference between predicted and actual delay. Lower is better.")
    print("  - R2 Score: How well the model explains the variance in the data. Closer to 1.0 is better.")
    
    # --- 5. Save the Trained Model ---
    model_file = 'delay_predictor.joblib'
    print(f"\n--- Saving the trained model to {model_file} ---")
    joblib.dump(model, model_file)
    print("Model saved successfully.")

if __name__ == "__main__":
    train_model()

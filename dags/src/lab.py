import pandas as pd
import os
import pickle
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta  # Import datetime and timedelta
from airflow.models import Variable
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from jinja2 import Template  
from email.mime.multipart import MIMEMultipart
from airflow.hooks.base import BaseHook


# Load data from a CSV file
def load_data():
    """
    Loads S&P 500 data from a CSV file and returns it as a DataFrame.
    """
    df_values = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/sp500_stocks.csv"))
    return df_values

# Preprocess the data
def data_preprocessing(data):
    """
    Preprocess the data for model training.
    """
# Convert 'Date' column to datetime format (adjusted for 'YYYY-MM-DD')
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')

    # Get the date 5 years ago from today
    five_years_ago = datetime.now() - timedelta(days=3*365)

    # Filter the data to include only the last 5 years
    data = data[data['Date'] >= five_years_ago]

        # Data cleaning steps
    data.fillna(data.mean(), inplace=True)
    for column in ['Open', 'High', 'Low', 'Close', 'Volume']:
        data[column] = np.clip(data[column], -1e6, 1e6)

    # Select relevant features and target variable
    features = ['Open', 'High', 'Low', 'Volume']
    target = 'Close'

    X = data[features]
    y = data[target]

    # Handle missing values if any
    X.fillna(method='ffill', inplace=True)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the features
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test

# Build and save a model
def build_save_model(data, filename):
    """
    Train a model and save it as a pickle file.
    """
    X_train, X_test, y_train, y_test = data

    # Train a Random Forest model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), "../model", filename)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as file:
        pickle.dump(model, file)


# Load a saved model, evaluate it, and send an email with the plot
def load_model_and_send_email(data, filename, **kwargs):
    """
    Load a saved model, evaluate it, and send an email with the plot.
    """
    X_train, X_test, y_train, y_test = data
    model_path = os.path.join(os.path.dirname(__file__), "../model", filename)

    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    # Evaluate the model
    predictions = model.predict(X_test)
    r2_score = model.score(X_test, y_test)
    logging.info(f"Model R^2 Score: {r2_score}")

    # Save the plot as an image file
    plt.figure(figsize=(10, 5))
    plt.plot(y_test.values[:100], label="Actual")
    plt.plot(predictions[:100], label="Predicted")
    plt.legend()
    plt.title("Predicted vs Actual Stock Prices")

    plot_path = os.path.join(os.path.dirname(__file__), "../plots/sp500_predictions.png")
    plt.savefig(plot_path)
    plt.close()  # Close the plot to free up memory

    # Log the path of the saved plot


    # Send the plot via email
    send_success_email(plot_path, r2_score, **kwargs)

def send_success_email(plot_path, r2_score, **kwargs):
    """
    Send an email with the plot attached and the model's R² score.
    """
    conn = BaseHook.get_connection('email_smtp')
    sender_email = conn.login
    password = conn.password
    receiver_emails = 'stephyromichan1@gmail.com'  # define receiver email

    # Define subject and body templates
    subject_template = 'Airflow Success: {{ dag.dag_id }} - Data Pipeline tasks succeeded'
    body_template = '''Hi team,
    The Data Pipeline tasks in DAG {{ dag.dag_id }} succeeded.
    The model's R² score is: {{ r2_score }}. Please find attached the predicted vs actual stock price plot.'''

    # Render templates using Jinja2 Template
    subject = Template(subject_template).render(dag=kwargs['dag'])
    body = Template(body_template).render(dag=kwargs['dag'], r2_score=r2_score)

    # Create the email headers and content
    email_message = MIMEMultipart()
    email_message['Subject'] = subject
    email_message['From'] = sender_email
    email_message['To'] = receiver_emails

    # Add body to email
    email_message.attach(MIMEText(body, 'plain'))


# Attach the plot file
    with open(plot_path, 'rb') as file:
        image = MIMEImage(file.read(), name=os.path.basename(plot_path))
        image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(plot_path))
        email_message.attach(image)
    try:
        # Set up the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Using Gmail's SMTP server
        server.starttls()  # Secure the connection
        server.login(sender_email, password)

        # Send email to each receiver
        email_message.replace_header('To', receiver_emails)
        server.sendmail(sender_email, receiver_emails, email_message.as_string())
        logging.info(f"Success email sent successfully to {receiver_emails}!")

    except Exception as e:
        logging.error(f"Error sending success email: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    data = load_data()
    processed_data = data_preprocessing(data)
    build_save_model(processed_data, "sp500_model.pkl")
    load_model_and_send_email(processed_data, "sp500_model.pkl", dag=None)

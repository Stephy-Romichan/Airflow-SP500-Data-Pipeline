# S&P 500 Machine Learning Pipeline

This project demonstrates the use of **Apache Airflow** for orchestrating a **machine learning pipeline** that processes S&P 500 stock data. The pipeline includes data ingestion, data preprocessing, model training, prediction, and automated email notifications. The project is containerized using **Docker** for easy setup and reproducibility.

## Overview

- **Data Source**: S&P 500 stock data (CSV file)
- **Pipeline Tools**: 
  - **Apache Airflow** for scheduling and orchestration
  - **Docker** for containerization
  - **Machine Learning** model for stock prediction
  - **Email Notifications** for status updates

## Features

- **Data Ingestion**: CSV file containing historical S&P 500 stock data
- **Data Preprocessing**: Basic data cleaning and transformation steps
- **Model Training**: Machine learning model trained to predict stock trends
- **Orchestration**: Apache Airflow orchestrates all steps in the pipeline
- **Notifications**: Automated email updates on pipeline execution

## Project Structure

```plaintext
├── dags/
│   ├── airflow_dags.py  # Airflow DAG file for the pipeline
├── data/
│   └── sp500_stocks.csv            # CSV file containing S&P 500 data
├── Dockerfile                    # Docker configuration for containerization
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation

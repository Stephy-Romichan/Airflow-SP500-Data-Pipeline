# SP500 Stock Price Prediction Pipeline

## Overview
This project implements a robust **data pipeline** using **Apache Airflow**, **Sci-kit Learn**,  for predicting SP500 stock prices. The pipeline automates data ingestion, preprocessing, model training, and visualization, providing end-to-end insights into stock market trends.

## Features
- **Data Ingestion**: Automatically fetch and store SP500 historical stock data.
- **Data Preprocessing**: Cleanses and prepares data for high-performance processing.
- **Model Training**: Trains a machine learning model to predict stock prices using scikit-learn.
- **Email Notifications**: Sends automated HTML emails summarizing pipeline results, including an R² score and prediction vs. actual plot.
- **Scalability**: Built to run seamlessly on **AWS EC2**, leveraging **Docker** containers for portability.

## Key Components
1. **Apache Airflow**:
   - Orchestrates and schedules all pipeline tasks.
   - Manages task dependencies and retries.
   
2. **PySpark**:
   - Performs data preprocessing on large datasets.
   - Scales data transformations efficiently.

3. **Sci-kit Learn**:
   - Train a machine learning model and generate predictions

5. **Docker**:
   - Ensures consistent deployment across environments.
   - Simplifies dependency management.


## Workflow
1. **Extract**: Retrieve historical SP500 data from a public API or data source.
2. **Transform**: Clean, preprocess, and feature-engineer data using PySpark.
3. **Load**: Store the processed data in a structured format (e.g., Parquet/CSV).
4. **Model**: Train a machine learning model and generate predictions.
5. **Visualize**: Export predictions for analysis.
6. **Notify**: Automatically email stakeholders with a detailed HTML report and performance metrics.

## Requirements
- **Python** (>=3.7)
- **Apache Airflow**
- **PySpark**
- **Docker**


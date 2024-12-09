from flask import Flask, render_template, request
import pandas as pd
import zipfile
import os
from sqlalchemy import create_engine

app = Flask(__name__)

# Database connection setup (SQLite for simplicity)
engine = create_engine('sqlite:///retail_data.db')

# Helper function to load data from a zip file
def load_zip_data(zip_path, csv_filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_filename) as f:
            return pd.read_csv(f)

# File names
transactions_zip = 'data/400_transactions.zip'
transactions_csv = '400_transactions.csv'
households_csv = 'data/400_households.csv'
products_csv = 'data/400_products.csv'

# Preload the data
if os.path.exists(transactions_zip):
    # Load transactions from zip
    transactions = load_zip_data(transactions_zip, transactions_csv)
    transactions.to_sql('Transactions', con=engine, if_exists='replace', index=False)
else:
    print(f"Error: {transactions_zip} not found!")

if os.path.exists(households_csv):
    households = pd.read_csv(households_csv)
    households.to_sql('Households', con=engine, if_exists='replace', index=False)
else:
    print(f"Error: {households_csv} not found!")

if os.path.exists(products_csv):
    products = pd.read_csv(products_csv)
    products.to_sql('Products', con=engine, if_exists='replace', index=False)
else:
    print(f"Error: {products_csv} not found!")

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Search functionality
@app.route('/search', methods=['GET'])
def search():
    hshd_num = request.args.get('hshd_num')
    if hshd_num:
        query = f"""
        SELECT Hshd_num, Basket_num, Date, Product_num, Department, Commodity
        FROM Transactions
        WHERE Hshd_num = {hshd_num}
        ORDER BY Hshd_num, Basket_num, Date, Product_num, Department, Commodity;
        """
        results = pd.read_sql(query, engine)
        return render_template('results.html', data=results.to_dict(orient='records'))
    return "No Household Number provided."

# File upload route
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        # Save uploaded file as a zip
        uploaded_zip_path = 'data/uploaded_transactions.zip'
        file.save(uploaded_zip_path)

        # Extract and load data from the uploaded zip
        uploaded_transactions = load_zip_data(uploaded_zip_path, transactions_csv)
        uploaded_transactions.to_sql('Transactions', con=engine, if_exists='append', index=False)

        return "File uploaded and data loaded successfully!"
    return "No file uploaded."

# Dashboard
@app.route('/dashboard')
def dashboard():
    query = "SELECT Department, SUM(Spending) as Total_Spending FROM Transactions GROUP BY Department;"
    data = pd.read_sql(query, engine)
    return render_template('dashboard.html', data=data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

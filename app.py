from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Database connection setup
engine = create_engine('sqlite:///retail_data.db')  # Example with SQLite

# Home page route
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
        JOIN Products ON Transactions.Product_num = Products.Product_num
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
        data = pd.read_csv(file)
        data.to_sql('Transactions', con=engine, if_exists='append', index=False)
        return "File uploaded and data loaded successfully!"
    return "No file uploaded."

# Dashboard route
@app.route('/dashboard')
def dashboard():
    # Sample query and visualization logic
    query = "SELECT Category, SUM(Spending) as Total_Spending FROM Transactions GROUP BY Category;"
    data = pd.read_sql(query, engine)
    return render_template('dashboard.html', data=data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

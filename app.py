import sqlite3
import json
from datetime import datetime, timedelta
import random
from flask import Flask, request, jsonify
import os
import csv
from io import StringIO
from flask_cors import CORS

class ExpenseDB:
    def __init__(self, db_path="expenses.db"):
        self.db_path = db_path
        print(f"Database path: {os.path.abspath(self.db_path)}")
        self.init_database()
    
    def init_database(self):
        """Initialize database with sample data and budget goals"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    confidence REAL
                )
            ''')
            
            # Create salary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_salary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monthly_salary REAL NOT NULL DEFAULT 0
                )
            ''')
            
            # Create budget_goals table with percentages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE,
                    percentage REAL NOT NULL
                )
            ''')

            # Insert default budget goals as percentages
            budget_goals = [
                ('Food', 20.0),
                ('Transportation', 10.0),
                ('Entertainment', 10.0),
                ('Shopping', 10.0),
                ('Utilities', 10.0),
                ('Healthcare', 10.0),
                ('Other', 30.0)
            ]
            
            for category, percentage in budget_goals:
                cursor.execute('''
                    INSERT OR REPLACE INTO budget_goals (category, percentage)
                    VALUES (?, ?)
                ''', (category, percentage))
            
            # Initialize salary
            cursor.execute('SELECT COUNT(*) FROM user_salary')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO user_salary (monthly_salary) VALUES (0)')
            
            # Generate sample historical data if empty
            cursor.execute("SELECT COUNT(*) FROM expenses")
            if cursor.fetchone()[0] == 0:
                self._generate_sample_data(cursor)
            
            conn.commit()
            conn.close()
            print("Database initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def _generate_sample_data(self, cursor):
        """Generate sample expense data"""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        descriptions = {
            'Food': ['Groceries', 'Restaurant', 'Coffee Shop', 'Food Delivery', 'Lunch'],
            'Transportation': ['Gas Station', 'Bus Fare', 'Taxi', 'Car Maintenance', 'Parking'],
            'Entertainment': ['Movie Tickets', 'Concert', 'Netflix', 'Sports Event'],
            'Utilities': ['Electric Bill', 'Internet', 'Phone Bill', 'Water Bill'],
            'Shopping': ['Clothing', 'Electronics', 'Amazon', 'Department Store'],
            'Healthcare': ['Pharmacy', 'Doctor Visit', 'Health Insurance', 'Gym Membership']
        }
        
        # Generate 3 months of sample data
        for month in range(3):
            base_date = datetime.now() - timedelta(days=90 - (month * 30))
            for _ in range(15):
                category = random.choice(categories)
                desc = random.choice(descriptions[category])
                amount = round(random.uniform(5, 200), 2)
                date = base_date + timedelta(days=random.randint(0, 29))
                
                cursor.execute('''
                    INSERT INTO expenses (description, amount, category, date, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (desc, amount, category, date.strftime('%Y-%m-%d'), round(random.uniform(0.7, 0.95), 2)))
    
    def add_expense(self, description, amount, category, confidence=0.8):
        """Add new expense to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO expenses (description, amount, category, date, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (description, amount, category, datetime.now().strftime('%Y-%m-%d'), confidence))
        
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return expense_id
    
    def get_all_expenses(self):
        """Get all expenses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, description, amount, category, date, confidence 
            FROM expenses 
            ORDER BY date DESC
        ''')
        
        expenses = []
        for row in cursor.fetchall():
            expenses.append({
                'id': row[0],
                'description': row[1],
                'amount': row[2],
                'category': row[3],
                'date': row[4],
                'confidence': row[5]
            })
        
        conn.close()
        return expenses
    
    def get_expenses_by_month(self):
        """Get expenses grouped by month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', date) as month,
                category,
                SUM(amount) as total
            FROM expenses 
            GROUP BY month, category
            ORDER BY month DESC
        ''')
        
        monthly_data = {}
        for row in cursor.fetchall():
            month, category, total = row
            if month not in monthly_data:
                monthly_data[month] = {}
            monthly_data[month][category] = total
        
        conn.close()
        return monthly_data
    
    def get_budget_goals(self):
        """Get budget goals as percentages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT category, percentage FROM budget_goals')
        goals = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()
        return goals

    def get_budget_limits(self, salary):
        """Calculate budget limits based on salary and percentages"""
        if salary == 0:
            return {}
            
        percentages = self.get_budget_goals()
        limits = {}

        for category, percentage in percentages.items():
            limits[category] = round((percentage / 100) * salary, 2)

        return limits
    
    def get_salary(self):
        """Get monthly salary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT monthly_salary FROM user_salary LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def set_salary(self, salary_amount):
        """Set monthly salary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE user_salary SET monthly_salary = ?', (salary_amount,))
        conn.commit()
        conn.close()
        
        return salary_amount

# Initialize database
expense_db = ExpenseDB()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Serve the main HTML page
@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found. Make sure it's in the same directory as app.py", 404

# Serve CSS
@app.route('/styles.css')
def serve_css():
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "styles.css not found", 404

# Serve JavaScript
@app.route('/script.js')
def serve_js():
    try:
        with open('script.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "script.js not found", 404

# API Routes
@app.route('/salary', methods=['GET'])
def get_salary():
    salary = expense_db.get_salary()
    return jsonify({'monthly_salary': salary})

@app.route('/salary', methods=['POST'])
def set_salary():
    data = request.json
    salary_amount = data.get('monthly_salary', 0)
    
    if salary_amount < 0:
        return jsonify({'error': 'Salary cannot be negative'}), 400
    
    expense_db.set_salary(salary_amount)
    return jsonify({'monthly_salary': salary_amount})

@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = expense_db.get_all_expenses()
    return jsonify({'expenses': expenses})

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    description = data.get('description')
    amount = data.get('amount')
    category = data.get('category', 'Other')
    confidence = data.get('confidence', 0.8)
    
    if not description or not amount:
        return jsonify({'error': 'Missing required fields'}), 400
    
    expense_id = expense_db.add_expense(description, amount, category, confidence)
    return jsonify({'id': expense_id, 'success': True}), 201

@app.route('/analytics/categories', methods=['GET'])
def get_analytics_categories():
    expenses = expense_db.get_all_expenses()
    
    category_totals = {}
    total_spending = 0
    
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += amount
        total_spending += amount
    
    return jsonify({
        'category_totals': category_totals,
        'total_spending': total_spending
    })

@app.route('/analytics/monthly', methods=['GET'])
def get_analytics_monthly():
    monthly_data = expense_db.get_expenses_by_month()
    return jsonify({'monthly_data': monthly_data})

@app.route('/budget/suggestions', methods=['GET'])
def get_budget_suggestions():
    salary = expense_db.get_salary()
    budget_goals = expense_db.get_budget_goals()
    budget_limits = expense_db.get_budget_limits(salary)
    
    expenses = expense_db.get_all_expenses()
    current_month = datetime.now().strftime('%Y-%m')
    
    # Calculate current month spending by category
    current_spending = {}
    total_current_spending = 0
    
    for expense in expenses:
        expense_month = expense['date'][:7]
        if expense_month == current_month:
            category = expense['category']
            amount = expense['amount']
            
            if category not in current_spending:
                current_spending[category] = 0
            current_spending[category] += amount
            total_current_spending += amount
    
    # Create suggestions
    suggestions = []
    
    for category, budget_limit in budget_limits.items():
        spent = current_spending.get(category, 0)
        percentage = (spent / budget_limit * 100) if budget_limit > 0 else 0
        
        # Determine status
        if percentage > 100:
            status = 'over-budget'
            suggestion_text = f'⚠️ You\'ve exceeded your {category} budget! Consider reducing expenses.'
        elif percentage > 80:
            status = 'warning'
            suggestion_text = f'📊 You\'re using {percentage:.0f}% of your {category} budget. Be careful!'
        else:
            status = 'on-track'
            suggestion_text = f'✅ You\'re doing great! {percentage:.0f}% of {category} budget used.'
        
        suggestions.append({
            'category': category,
            'budget_limit': budget_limit,
            'current_spending': spent,
            'percentage': percentage,
            'status': status,
            'suggestion': suggestion_text
        })
    
    # Add monthly summary
    remaining_salary = salary - total_current_spending
    suggestions.append({
        'category': 'Monthly Summary',
        'budget_limit': salary,
        'current_spending': total_current_spending,
        'percentage': (total_current_spending / salary * 100) if salary > 0 else 0,
        'status': 'info',
        'suggestion': f'Total spent: ₹{total_current_spending:.2f} | Remaining: ₹{remaining_salary:.2f}'
    })
    
    return jsonify({'suggestions': suggestions})

@app.route('/categorize', methods=['POST'])
def categorize_expense():
    data = request.json
    description = data.get('description', '').lower()
    
    # Simple AI categorization based on keywords
    keywords = {
        'Food': ['food', 'eat', 'restaurant', 'grocery', 'coffee', 'lunch', 'dinner', 'snack', 'pizza', 'burger', 'cafe'],
        'Transportation': ['taxi', 'bus', 'gas', 'train', 'metro', 'transport', 'fuel', 'parking', 'car', 'bike'],
        'Entertainment': ['movie', 'concert', 'game', 'netflix', 'spotify', 'play', 'entertainment', 'cinema', 'ticket'],
        'Utilities': ['electric', 'water', 'internet', 'phone', 'bill', 'utility', 'power', 'wifi'],
        'Healthcare': ['doctor', 'pharmacy', 'medicine', 'hospital', 'health', 'medical', 'gym'],
        'Shopping': ['shop', 'buy', 'store', 'mall', 'clothes', 'amazon', 'online', 'product'],
    }
    
    category = 'Other'
    confidence = 0.5
    
    for cat, words in keywords.items():
        for word in words:
            if word in description:
                category = cat
                confidence = 0.85
                break
    
    return jsonify({
        'category': category,
        'confidence': confidence
    })

@app.route('/predict/next-month', methods=['GET'])
def predict_next_month():
    monthly_data = expense_db.get_expenses_by_month()
    
    if not monthly_data:
        return jsonify({
            'prediction': {
                'predicted_amount': 0,
                'confidence': 0,
                'trend': 'Insufficient data'
            }
        })
    
    # Get last 3 months of data
    months = sorted(monthly_data.keys(), reverse=True)[:3]
    
    if len(months) < 2:
        return jsonify({
            'prediction': {
                'predicted_amount': 0,
                'confidence': 0.5,
                'trend': 'Insufficient data'
            }
        })
    
    # Calculate total spending per month
    monthly_totals = []
    for month in months:
        total = sum(monthly_data[month].values())
        monthly_totals.append(total)
    
    # Simple average prediction
    predicted_amount = sum(monthly_totals) / len(monthly_totals)
    
    # Calculate trend
    if monthly_totals[0] > monthly_totals[-1]:
        trend = 'Increasing'
    elif monthly_totals[0] < monthly_totals[-1]:
        trend = 'Decreasing'
    else:
        trend = 'Stable'
    
    return jsonify({
        'prediction': {
            'predicted_amount': round(predicted_amount, 2),
            'confidence': '75%',
            'trend': trend
        }
    })

@app.route('/export/csv', methods=['GET'])
def export_csv():
    expenses = expense_db.get_all_expenses()
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['ID', 'Description', 'Amount', 'Category', 'Date', 'Confidence'])
    writer.writeheader()
    
    for expense in expenses:
        writer.writerow({
            'ID': expense['id'],
            'Description': expense['description'],
            'Amount': expense['amount'],
            'Category': expense['category'],
            'Date': expense['date'],
            'Confidence': expense['confidence']
        })
    
    response = app.response_class(
        response=output.getvalue(),
        status=200,
        mimetype='text/csv'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=expenses.csv'
    
    return response

if __name__ == '__main__':
    print("Starting AI Expense Advisor...")
    print("Access the application at: http://127.0.0.1:8000 or http://localhost:8000")
    app.run(debug=True, port=8000, host='0.0.0.0')

# AI Expense Advisor

## Project Overview

AI Expense Advisor is an intelligent web application designed to help users track, categorize, and analyze their personal expenses. Built with a Flask backend and modern web technologies, it leverages machine learning algorithms to automatically categorize expenses and provide insightful budget recommendations and spending predictions.

The application features a user-friendly interface with real-time analytics, AI-powered expense categorization, budget tracking, and predictive insights to help users make informed financial decisions.

## Features

- **Expense Tracking**: Add, view, and manage personal expenses with detailed categorization
- **AI-Powered Categorization**: Automatic expense categorization using machine learning models
- **Budget Management**: Set monthly salary and receive personalized budget suggestions
- **Analytics Dashboard**: Interactive charts and visualizations for spending patterns
- **Spending Predictions**: Forecast next month's expenses based on historical data
- **Data Export**: Export expense data to CSV format
- **Responsive Design**: Modern, mobile-friendly web interface

## Tech Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **SQLite** - Database
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript (ES6+)** - Client-side logic
- **Plotly.js** - Data visualization
- **Font Awesome** - Icons

### Machine Learning
- **scikit-learn** - Machine learning algorithms
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **joblib** - Model serialization

## Model Details

### Architecture

The application uses two main ML components:

1. **Expense Categorization Model**
   - **Algorithm**: RandomForestClassifier with 100 estimators
   - **Purpose**: Automatically categorize expenses into predefined categories
   - **Fallback**: Keyword-based matching for quick categorization

2. **Expense Prediction Model**
   - **Algorithm**: Simple moving average calculation
   - **Purpose**: Predict next month's total expenses
   - **Input**: Historical monthly spending data

### Data Preprocessing

**Text Preprocessing for Categorization:**
- Convert to lowercase
- Remove punctuation and special characters
- Remove numerical digits
- TF-IDF vectorization with max 1000 features
- English stop words removal

**Training Data:**
- Synthetic training data generated from common expense patterns
- Categories: Food, Transportation, Entertainment, Utilities, Healthcare, Shopping, Other
- Keyword mapping for fast matching

### Model Training

- **Training Method**: Background thread initialization
- **Vectorization**: TF-IDF with English stop words
- **Classification**: Random Forest with random_state=42 for reproducibility
- **Fallback Strategy**: Keyword-based categorization when ML model unavailable

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd expense-advisor
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8000`
   - The application will automatically initialize with sample data

## Usage

### Getting Started
1. Set your monthly salary using the "Set Monthly Salary" button
2. Add expenses using the "Add Expense" tab
3. Use AI categorization or manually select categories
4. View analytics and budget suggestions in respective tabs

### API Endpoints

The application provides RESTful API endpoints:

- `GET /` - Main application interface
- `GET/POST /salary` - Get/set monthly salary
- `GET/POST /expenses` - Retrieve/add expenses
- `GET /analytics/categories` - Category spending analytics
- `GET /analytics/monthly` - Monthly spending trends
- `GET /budget/suggestions` - AI budget recommendations
- `POST /categorize` - AI expense categorization
- `GET /predict/next-month` - Spending predictions
- `GET /export/csv` - Export data to CSV

### Key Features Usage

- **Dashboard**: Overview of recent expenses and category breakdown
- **Add Expense**: Input expense details, AI auto-categorization available
- **Analytics**: View spending trends and category distributions
- **Budget Tips**: Personalized budget suggestions based on salary
- **Predictions**: Forecast future spending patterns

## Deployment

### Local Development
The application runs locally at `http://localhost:8000`. Upon startup, it initializes with sample expense data for demonstration purposes.

### Hosting Options

#### Option 1: Heroku (Recommended for Flask apps)
1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create a `Procfile`** in your project root:
   ```
   web: python app.py
   ```

3. **Create `runtime.txt`** for Python version:
   ```
   python-3.9.7
   ```

4. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

5. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

7. **Access your app** at the URL provided by Heroku.

#### Option 2: Railway
1. **Sign up at [Railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Railway will automatically detect Flask and deploy**
4. **Set environment variables if needed** (none required for this app)

#### Option 3: Render
1. **Sign up at [Render.com](https://render.com)**
2. **Connect your GitHub repository**
3. **Choose "Web Service"**
4. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. **Deploy**

#### Option 4: PythonAnywhere
1. **Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com)**
2. **Upload your files** or connect via Git
3. **Create a web app** and configure the WSGI file
4. **Set up virtual environment** and install requirements

### Important Notes
- The app uses SQLite database, which is file-based and persists data locally
- For production, consider using a cloud database like PostgreSQL
- Ensure your hosting platform supports Python 3.8+
- The app runs on port 8000 by default, but hosting platforms may override this

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

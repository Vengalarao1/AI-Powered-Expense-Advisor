import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import re
import threading
import difflib

class ExpenseClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Other']
        self.is_trained = False
        self._training_thread = None
        # Start training in background
        self._training_thread = threading.Thread(target=self.train, daemon=True)
        self._training_thread.start()
        # Lightweight keyword-based mapping
        self.keyword_map = {
            'Food': [
                'drink', 'drinking', 'drining', 'coffee', 'tea', 'beer', 'wine', 'bar',
                'restaurant', 'cafe', 'lunch', 'dinner', 'breakfast', 'meal', 'grocery', 'supermarket'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'gas', 'petrol', 'parking', 'flight'
            ],
            'Entertainment': [
                'netflix', 'movie', 'cinema', 'concert', 'spotify', 'music', 'game'
            ],
            'Shopping': [
                'amazon', 'walmart', 'target', 'shopping', 'clothes', 'cloth', 'dress', 'shirt', 'shirts', 'tshirt', 't-shirt', 'jeans', 'skirt', 'pants', 'trousers', 'jacket', 'coat', 'shoes', 'footwear', 'mall', 'boutique', 'apparel', 'store'
            ],
        }
        # flattened set of keywords for quick checks
        self._keyword_lookup = {k: set(v) for k, v in self.keyword_map.items()}
    
    def preprocess_text(self, text):
        """Clean and preprocess transaction descriptions"""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\d+', '', text)  # Remove numbers
        return text.strip()
    
    def generate_training_data(self):
        """Generate synthetic training data for expense categorization"""
        training_data = [
            # Food transactions
            ("mcdonalds burger king pizza hut subway", "Food"),
            ("starbucks coffee cafe restaurant lunch dinner", "Food"),
            ("grocery supermarket walmart costco", "Food"),
            ("food delivery uber eats doordash", "Food"),
            
            # Transportation
            ("uber lyft taxi bus train metro", "Transportation"),
            ("gas station shell bp exxon", "Transportation"),
            ("car repair maintenance parking", "Transportation"),
            ("flight airline airport", "Transportation"),
            
            # Entertainment
            ("netflix spotify movie cinema theater", "Entertainment"),
            ("concert sports game bowling", "Entertainment"),
            ("amazon prime video music", "Entertainment"),
            
            # Utilities
            ("electricity water bill internet wifi", "Utilities"),
            ("phone mobile verizon at&t", "Utilities"),
            ("rent mortgage housing", "Utilities"),
            
            # Healthcare
            ("hospital doctor pharmacy drugstore", "Healthcare"),
            ("medical insurance dental", "Healthcare"),
            ("gym fitness workout", "Healthcare"),
            
            # Shopping
            ("amazon walmart target shopping", "Shopping"),
            ("clothing shoes fashion", "Shopping"),
            ("electronics apple samsung", "Shopping")
        ]
        
        descriptions = [self.preprocess_text(desc) for desc, _ in training_data]
        labels = [label for _, label in training_data]
        
        return descriptions, labels
    
    def train(self):
        """Train the classification model"""
        try:
            print("[TRAIN] Training expense classification model...")
            
            # Generate training data
            descriptions, labels = self.generate_training_data()
            
            # Vectorize text
            X = self.vectorizer.fit_transform(descriptions)
            y = labels
            
            # Train classifier
            self.classifier.fit(X, y)
            self.is_trained = True
            
            print("[TRAIN] Model training completed!")
            return True
        except Exception as e:
            print(f"[TRAIN] Training error: {e}")
            return False
    
    def predict_category(self, description):
        """Predict expense category"""
        # Wait for training if still in progress
        max_wait = 0
        while not self.is_trained and max_wait < 30:
            import time
            time.sleep(0.1)
            max_wait += 1
        
        if not self.is_trained:
            # Return default if training fails
            return {
                'category': 'Other',
                'confidence': 0.5,
                'all_probabilities': {}
            }
        
        try:
            cleaned_text = self.preprocess_text(description)

            # First, quick keyword-based override
            words = cleaned_text.split()
            # direct and substring match check
            for w in words:
                for cat, kwlist in self.keyword_map.items():
                    # exact or set-based quick check
                    if w in self._keyword_lookup.get(cat, set()):
                        return {
                            'category': cat,
                            'confidence': 0.85,
                            'all_probabilities': {cat: 0.85}
                        }
                    # substring checks
                    for kw in kwlist:
                        if kw in w or (len(w) >= 3 and w in kw):
                            return {
                                'category': cat,
                                'confidence': 0.85,
                                'all_probabilities': {cat: 0.85}
                            }

            # fuzzy match check using difflib for short misspellings
            for w in words:
                for cat, kwlist in self.keyword_map.items():
                    close = difflib.get_close_matches(w, kwlist, n=1, cutoff=0.75)
                    if close:
                        return {
                            'category': cat,
                            'confidence': 0.78,
                            'all_probabilities': {cat: 0.78}
                        }

            # Fall back to model prediction
            X = self.vectorizer.transform([cleaned_text])
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]

            return {
                'category': prediction,
                'confidence': float(max(probabilities)),
                'all_probabilities': dict(zip(self.classifier.classes_, probabilities))
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'category': 'Other',
                'confidence': 0.5,
                'all_probabilities': {}
            }

class ExpensePredictor:
    def __init__(self):
        pass
    
    def predict_next_month(self, historical_data):
        """Predict next month's total expense using historical transactions."""
        if not historical_data or len(historical_data) == 0:
            return {"prediction": "Insufficient data", "predicted_amount": 0}

        # Group by month (assumes each item has a 'date' in 'YYYY-MM-DD' format)
        monthly_sums = {}
        for item in historical_data:
            try:
                month = str(item.get('date', ''))[:7]
                amt = float(item.get('amount', 0) or 0)
                if not month:
                    continue
                monthly_sums[month] = monthly_sums.get(month, 0) + amt
            except Exception:
                continue

        if len(monthly_sums) == 0:
            return {"prediction": "Insufficient data", "predicted_amount": 0}

        # Sort months ascending
        months_sorted = sorted(monthly_sums.keys())

        # Use up to the last 6 months for prediction
        last_months = months_sorted[-6:]
        amounts = [monthly_sums[m] for m in last_months]

        # Prediction: simple average of the selected months
        predicted = sum(amounts) / len(amounts)

        # Confidence heuristic: more months -> higher confidence
        if len(amounts) >= 6:
            confidence = 'high'
        elif len(amounts) >= 3:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Trend: compare most recent month to the earliest in the window
        trend = 'stable'
        if len(amounts) >= 2:
            trend = 'increasing' if amounts[-1] > amounts[0] else ('decreasing' if amounts[-1] < amounts[0] else 'stable')

        return {
            "predicted_amount": round(predicted, 2),
            "confidence": confidence,
            "trend": trend,
            "months_used": last_months,
            "monthly_sums": {m: round(monthly_sums[m], 2) for m in last_months}
        }

# Initialize models
expense_classifier = ExpenseClassifier()
expense_predictor = ExpensePredictor()
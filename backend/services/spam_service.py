import re
import pickle
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class SpamDetectorService:
    """Service for detecting spam and phishing emails"""
    
    # Spam indicators
    SPAM_KEYWORDS = [
        'winner', 'congratulations', 'free', 'prize', 'click here', 'urgent',
        'act now', 'limited time', 'offer expires', 'cash', 'money', 'credit card',
        'password', 'verify account', 'suspended', 'confirm identity', 'bank account',
        'social security', 'tax refund', 'inheritance', 'lottery', 'casino'
    ]
    
    PHISHING_PATTERNS = [
        r'verify.*account',
        r'confirm.*identity',
        r'suspended.*account',
        r'unusual.*activity',
        r'click.*link',
        r'update.*payment',
        r'expire.*\d+.*hours?',
        r'reset.*password'
    ]
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model = None
        self._train_model()
    
    def _train_model(self):
        """Train spam detection model with synthetic data"""
        # Training data (spam examples)
        spam_samples = [
            "Congratulations! You've won $1,000,000! Click here to claim your prize now!",
            "URGENT: Your account has been suspended. Verify your identity immediately.",
            "Free money! Act now! Limited time offer expires in 24 hours!",
            "Your bank account needs verification. Click this link to confirm.",
            "You've been selected for a special cash prize. Claim now!",
            "WINNER! You won the lottery! Send your details to claim.",
            "Verify your password immediately or account will be deleted.",
            "Unusual activity detected. Reset your password now.",
            "Free credit card offer! Apply now! No fees!",
            "Your tax refund is ready. Click here to receive $5000.",
            "Inheritance money waiting for you. Contact us immediately.",
            "Casino bonus! Free $500! Play now and win big!",
            "Your payment method expired. Update now to avoid suspension.",
            "Security alert! Confirm your social security number.",
            "Limited time offer! Buy now and get 90% discount!"
        ]
        
        # Training data (legitimate examples)
        ham_samples = [
            "Hi, let's schedule a meeting for next week to discuss the project.",
            "Thank you for your order. Your package will arrive in 3-5 business days.",
            "Reminder: Team standup meeting tomorrow at 10 AM.",
            "Your monthly statement is now available. Please review at your convenience.",
            "Welcome to our newsletter! Here are this week's updates.",
            "Your appointment is confirmed for Monday at 2 PM.",
            "Project deadline extended to next Friday. Please plan accordingly.",
            "Thank you for attending our webinar. Here are the slides.",
            "Your subscription renewal is coming up next month.",
            "Meeting notes from today's discussion are attached.",
            "Please review the attached document and provide feedback.",
            "Your report has been successfully submitted.",
            "Reminder: Please complete the survey by end of week.",
            "New features have been added to your account.",
            "Your request has been processed successfully."
        ]
        
        # Combine and create labels
        X_train = spam_samples + ham_samples
        y_train = [1] * len(spam_samples) + [0] * len(ham_samples)
        
        # Train vectorizer and model
        X_vectorized = self.vectorizer.fit_transform(X_train)
        self.model = MultinomialNB()
        self.model.fit(X_vectorized, y_train)
    
    def extract_features(self, text: str) -> Dict[str, any]:
        """Extract features from email text"""
        text_lower = text.lower()
        
        features = {
            'spam_keyword_count': 0,
            'phishing_pattern_count': 0,
            'has_urgent_words': False,
            'has_money_words': False,
            'has_link_words': False,
            'excessive_punctuation': False,
            'all_caps_words': 0,
            'suspicious_patterns': []
        }
        
        # Count spam keywords
        for keyword in self.SPAM_KEYWORDS:
            if keyword in text_lower:
                features['spam_keyword_count'] += 1
                if keyword in ['urgent', 'act now', 'limited time']:
                    features['has_urgent_words'] = True
                if keyword in ['money', 'cash', 'prize', 'free']:
                    features['has_money_words'] = True
                if keyword in ['click here', 'click link']:
                    features['has_link_words'] = True
        
        # Check phishing patterns
        for pattern in self.PHISHING_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                features['phishing_pattern_count'] += len(matches)
                features['suspicious_patterns'].extend(matches)
        
        # Check for excessive punctuation
        punctuation_count = len(re.findall(r'[!?]{2,}', text))
        features['excessive_punctuation'] = punctuation_count > 2
        
        # Count all caps words
        words = text.split()
        features['all_caps_words'] = sum(1 for word in words if word.isupper() and len(word) > 2)
        
        return features
    
    def calculate_confidence(self, features: Dict, ml_probability: float) -> float:
        """Calculate confidence score based on features and ML prediction"""
        # Base confidence from ML model
        confidence = ml_probability
        
        # Adjust based on features
        if features['spam_keyword_count'] > 3:
            confidence = min(confidence + 0.1, 1.0)
        
        if features['phishing_pattern_count'] > 0:
            confidence = min(confidence + 0.15, 1.0)
        
        if features['has_urgent_words'] and features['has_money_words']:
            confidence = min(confidence + 0.1, 1.0)
        
        if features['excessive_punctuation']:
            confidence = min(confidence + 0.05, 1.0)
        
        if features['all_caps_words'] > 3:
            confidence = min(confidence + 0.05, 1.0)
        
        return round(confidence, 3)
    
    def detect_spam(self, email_text: str) -> Dict:
        """Main method to detect spam/phishing"""
        # Extract features
        features = self.extract_features(email_text)
        
        # Vectorize text
        X = self.vectorizer.transform([email_text])
        
        # Predict
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0]
        
        # Calculate confidence
        spam_probability = probability[1] if len(probability) > 1 else probability[0]
        confidence = self.calculate_confidence(features, spam_probability)
        
        # Determine classification
        is_spam = bool(prediction == 1)
        
        # Generate explanation
        reasons = []
        if features['spam_keyword_count'] > 0:
            reasons.append(f"Contains {features['spam_keyword_count']} spam keywords")
        if features['phishing_pattern_count'] > 0:
            reasons.append(f"Detected {features['phishing_pattern_count']} phishing patterns")
        if features['has_urgent_words']:
            reasons.append("Uses urgent language")
        if features['has_money_words']:
            reasons.append("Contains money-related terms")
        if features['excessive_punctuation']:
            reasons.append("Excessive punctuation detected")
        
        return {
            'is_spam': is_spam,
            'confidence': confidence,
            'classification': 'SPAM' if is_spam else 'LEGITIMATE',
            'features': features,
            'reasons': reasons if is_spam else ['No suspicious patterns detected'],
            'risk_level': 'HIGH' if confidence > 0.8 else 'MEDIUM' if confidence > 0.5 else 'LOW'
        }

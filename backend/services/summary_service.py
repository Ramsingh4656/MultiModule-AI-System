import re
import nltk
from typing import Dict, List
from collections import Counter
import numpy as np

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

class SummarizerService:
    """Service for extractive text summarization"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s\.\!\?]', '', text)
        return text.strip()
    
    def calculate_word_frequencies(self, text: str) -> Dict[str, float]:
        """Calculate normalized word frequencies"""
        words = word_tokenize(text.lower())
        
        # Filter stopwords and short words
        filtered_words = [
            word for word in words 
            if word.isalnum() and word not in self.stop_words and len(word) > 2
        ]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        
        # Normalize
        max_freq = max(word_freq.values()) if word_freq else 1
        normalized_freq = {word: freq / max_freq for word, freq in word_freq.items()}
        
        return normalized_freq
    
    def score_sentences(self, sentences: List[str], word_frequencies: Dict[str, float]) -> Dict[str, float]:
        """Score sentences based on word frequencies"""
        sentence_scores = {}
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            word_count = len([w for w in words if w.isalnum()])
            
            if word_count > 5:  # Ignore very short sentences
                score = 0
                for word in words:
                    if word in word_frequencies:
                        score += word_frequencies[word]
                
                # Normalize by sentence length
                sentence_scores[sentence] = score / word_count
        
        return sentence_scores
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """Extract key bullet points from text"""
        sentences = sent_tokenize(text)
        word_frequencies = self.calculate_word_frequencies(text)
        sentence_scores = self.score_sentences(sentences, word_frequencies)
        
        # Sort sentences by score
        ranked_sentences = sorted(
            sentence_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Get top sentences
        top_sentences = ranked_sentences[:min(num_points, len(ranked_sentences))]
        
        # Sort by original order
        original_order = []
        for sentence in sentences:
            for scored_sentence, score in top_sentences:
                if sentence == scored_sentence:
                    original_order.append(sentence)
                    break
        
        return original_order
    
    def generate_summary(self, text: str, summary_ratio: float = 0.3) -> Dict:
        """Generate extractive summary"""
        # Preprocess
        cleaned_text = self.preprocess_text(text)
        
        # Tokenize into sentences
        sentences = sent_tokenize(cleaned_text)
        
        if len(sentences) <= 3:
            return {
                'summary': cleaned_text,
                'bullet_points': sentences,
                'original_length': len(text),
                'summary_length': len(cleaned_text),
                'compression_ratio': 1.0,
                'sentences_original': len(sentences),
                'sentences_summary': len(sentences)
            }
        
        # Calculate word frequencies
        word_frequencies = self.calculate_word_frequencies(cleaned_text)
        
        # Score sentences
        sentence_scores = self.score_sentences(sentences, word_frequencies)
        
        # Determine number of sentences for summary
        num_sentences = max(3, int(len(sentences) * summary_ratio))
        
        # Get top sentences
        ranked_sentences = sorted(
            sentence_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_sentences]
        
        # Sort by original order
        summary_sentences = []
        for sentence in sentences:
            for scored_sentence, score in ranked_sentences:
                if sentence == scored_sentence:
                    summary_sentences.append(sentence)
                    break
        
        # Create summary
        summary_text = ' '.join(summary_sentences)
        
        # Extract bullet points (top 5 key sentences)
        bullet_points = self.extract_key_points(cleaned_text, num_points=5)
        
        # Calculate metrics
        compression_ratio = len(summary_text) / len(cleaned_text) if len(cleaned_text) > 0 else 1.0
        
        return {
            'summary': summary_text,
            'bullet_points': bullet_points,
            'original_length': len(text),
            'summary_length': len(summary_text),
            'compression_ratio': round(compression_ratio, 2),
            'sentences_original': len(sentences),
            'sentences_summary': len(summary_sentences),
            'key_terms': list(word_frequencies.keys())[:10]
        }
    
    def summarize_with_length(self, text: str, max_length: int = 500) -> Dict:
        """Generate summary with specific maximum length"""
        # Start with 30% ratio
        result = self.generate_summary(text, summary_ratio=0.3)
        
        # Adjust if needed
        if result['summary_length'] > max_length:
            # Try with smaller ratio
            result = self.generate_summary(text, summary_ratio=0.2)
        
        return result

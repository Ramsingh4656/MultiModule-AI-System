import math
import re
from collections import Counter
from typing import Dict, List, Tuple


class SummarizerService:
    """Pure-Python extractive summarization (NO NLTK)."""

    # A compact stopword list (enough for TF-IDF signal, no external downloads).
    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "there",
        "they",
        "this",
        "to",
        "was",
        "were",
        "will",
        "with",
        "you",
        "your",
        "we",
        "our",
        "i",
        "me",
        "my",
        "them",
        "us",
    }

    SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
    WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize whitespace while preserving sentence structure."""
        text = re.sub(r"\s+", " ", text or "").strip()
        # Keep basic punctuation so sentence splitting remains stable.
        text = re.sub(r"[^\w\s\.\!\?\-\,\;:]", "", text)
        return text.strip()

    def simple_sent_tokenize(self, text: str) -> List[str]:
        """Split on punctuation followed by space + capital letter."""
        cleaned = self.preprocess_text(text)
        if not cleaned:
            return []
        parts = self.SENTENCE_SPLIT_RE.split(cleaned)
        return [p.strip() for p in parts if p.strip()]

    def simple_word_tokenize(self, text: str) -> List[str]:
        words = self.WORD_RE.findall((text or "").lower())
        return [w for w in words if w not in self.STOP_WORDS and len(w) > 2]

    def _tfidf_for_document(self, sentences: List[str]) -> Tuple[Dict[str, float], List[List[str]]]:
        """Compute simple document-level TF-IDF from sentence counts."""
        tokenized: List[List[str]] = [self.simple_word_tokenize(s) for s in sentences]
        all_terms = set(t for toks in tokenized for t in toks)
        if not all_terms:
            return {}, tokenized

        N = max(1, len(sentences))
        df = {term: 0 for term in all_terms}
        tf = {term: 0 for term in all_terms}

        for toks in tokenized:
            # update df
            unique = set(toks)
            for term in unique:
                df[term] += 1
            # update tf (raw counts across document)
            for t in toks:
                tf[t] += 1

        tfidf = {}
        for term in all_terms:
            # log smoothing
            idf = math.log((N + 1) / (df[term] + 1)) + 1.0
            tfidf[term] = float(tf[term]) * idf

        return tfidf, tokenized

    def generate_summary(self, text: str, summary_ratio: float = 0.3) -> Dict:
        """Generate an extractive summary."""
        cleaned_text = self.preprocess_text(text)
        sentences = self.simple_sent_tokenize(cleaned_text)
        original_length = len(text or "")
        if not sentences:
            return {
                "summary": "",
                "bullet_points": [],
                "compression_ratio": 1.0,
                "original_length": original_length,
                "summary_length": 0,
                "sentences_original": 0,
                "sentences_summary": 0,
                "key_terms": [],
            }

        if len(sentences) <= 3:
            return {
                "summary": cleaned_text,
                "bullet_points": sentences,
                "original_length": original_length,
                "summary_length": len(cleaned_text),
                "compression_ratio": 1.0,
                "sentences_original": len(sentences),
                "sentences_summary": len(sentences),
                "key_terms": [],
            }

        tfidf_by_term, tokenized_sentences = self._tfidf_for_document(sentences)
        if not tfidf_by_term:
            # No usable terms; fallback to first few sentences.
            num_sentences = max(3, int(len(sentences) * summary_ratio))
            summary_sentences = sentences[:num_sentences]
            summary_text = " ".join(summary_sentences)
            return {
                "summary": summary_text,
                "bullet_points": summary_sentences[: min(5, len(summary_sentences))],
                "original_length": original_length,
                "summary_length": len(summary_text),
                "compression_ratio": round(len(summary_text) / max(1, len(cleaned_text)), 2),
                "sentences_original": len(sentences),
                "sentences_summary": len(summary_sentences),
                "key_terms": [],
            }

        # Score sentences by: (TF-IDF word frequency) / sentence length
        scores: List[Tuple[int, float]] = []
        for idx, toks in enumerate(tokenized_sentences):
            if not toks:
                continue
            word_count = max(1, len(toks))
            word_freq = Counter(toks)
            tfidf_sum = 0.0
            for term, cnt in word_freq.items():
                tfidf_sum += (tfidf_by_term.get(term, 0.0) * cnt) / word_count
            scores.append((idx, tfidf_sum / word_count))

        # Number of sentences to keep
        num_sentences = max(3, int(len(sentences) * summary_ratio))
        num_sentences = min(num_sentences, len(sentences))

        top = sorted(scores, key=lambda x: x[1], reverse=True)[:num_sentences]
        top_indices = sorted(idx for idx, _ in top)
        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = " ".join(summary_sentences).strip()

        # Bullet points: top 5 scored sentences, preserved original order
        bullet_count = min(5, len(sentences))
        bullet_top = sorted(scores, key=lambda x: x[1], reverse=True)[:bullet_count]
        bullet_indices = sorted(idx for idx, _ in bullet_top)
        bullet_points = [sentences[i] for i in bullet_indices]

        compression_ratio = len(summary_text) / max(1, len(cleaned_text))

        # Key terms: top TF-IDF terms
        key_terms = [t for t, _ in sorted(tfidf_by_term.items(), key=lambda x: x[1], reverse=True)[:10]]

        return {
            "summary": summary_text,
            "bullet_points": bullet_points,
            "compression_ratio": round(compression_ratio, 2),
            "original_length": original_length,
            "summary_length": len(summary_text),
            "sentences_original": len(sentences),
            "sentences_summary": len(summary_sentences),
            "key_terms": key_terms,
        }

    def summarize_with_length(self, text: str, max_length: int = 500) -> Dict:
        """Generate a summary that fits a maximum character length."""
        # Try decreasing ratios until it fits.
        ratios = [0.3, 0.24, 0.2, 0.16, 0.12]
        last = None
        for r in ratios:
            last = self.generate_summary(text, summary_ratio=r)
            if last.get("summary_length", 0) <= max_length:
                return last
        return last if last is not None else self.generate_summary(text, summary_ratio=0.2)

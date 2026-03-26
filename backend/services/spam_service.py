import re
from typing import Dict, List

from math import log, exp


class SpamDetectorService:
    """Service for detecting spam and phishing emails (ML + rules, no NLTK)."""

    SPAM_KEYWORDS: List[str] = [
        "winner",
        "congratulations",
        "free",
        "prize",
        "click here",
        "urgent",
        "act now",
        "limited time",
        "offer expires",
        "cash",
        "money",
        "credit card",
        "password",
        "verify account",
        "suspended",
        "confirm identity",
        "bank account",
        "social security",
        "tax refund",
        "inheritance",
        "lottery",
        "casino",
    ]

    PHISHING_PATTERNS: List[str] = [
        r"verify.*account",
        r"confirm.*identity",
        r"suspended.*account",
        r"unusual.*activity",
        r"click.*link",
        r"update.*payment",
        r"expire.*\d+.*hours?",
        r"reset.*password",
    ]

    WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")

    def __init__(self) -> None:
        # Keep everything pure-Python to avoid heavy native deps.
        self.vocabulary: List[str] = []
        self.idf: Dict[str, float] = {}
        self.class_log_priors: Dict[str, float] = {}
        self.class_term_log_probs: Dict[str, Dict[str, float]] = {}
        self._train_model()

    def _tokenize(self, text: str) -> List[str]:
        return self.WORD_RE.findall((text or "").lower())

    def _ngrams(self, tokens: List[str], ngram_range: tuple[int, int] = (1, 2)) -> List[str]:
        min_n, max_n = ngram_range
        terms: List[str] = []
        for n in range(min_n, max_n + 1):
            if n == 1:
                terms.extend(tokens)
            else:
                for i in range(0, len(tokens) - n + 1):
                    terms.append(" ".join(tokens[i : i + n]))
        return terms

    def _compute_df(self, docs_terms: List[List[str]]) -> Dict[str, int]:
        df: Dict[str, int] = {}
        for terms in docs_terms:
            for term in set(terms):
                df[term] = df.get(term, 0) + 1
        return df

    def _train_model(self) -> None:
        """Train TF-IDF (1–2 grams) + multinomial naive Bayes on synthetic data."""
        # Rule-based + ML combined needs enough training examples.
        # Use 20 spam + 20 legitimate samples.
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
            "Limited time offer! Buy now and get 90% discount!",
            "Act now—this exclusive offer will expire soon. Verify your account today.",
            "You have been chosen as a winner. Click to claim your reward.",
            "Password reset required. Please verify your account to continue.",
            "Claim your prize: urgent confirmation needed. Update your details now.",
            "Final notice: account suspended due to unusual activity. Click here.",
        ]

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
            "Your request has been processed successfully.",
            "Let's review the draft and share any edits before the call.",
            "Can you update the status report for this sprint today?",
            "The invoice for last month has been sent. Payment is due soon.",
            "Your order is on the way. Tracking details are included below.",
            "Please find the agenda and links for the upcoming workshop.",
        ]

        docs = spam_samples + ham_samples
        labels = ["spam"] * len(spam_samples) + ["ham"] * len(ham_samples)

        docs_terms = [self._ngrams(self._tokenize(doc)) for doc in docs]

        df = self._compute_df(docs_terms)
        # Build a capped vocabulary for stability.
        # This isn't required for correctness, but it keeps probabilities tidy.
        vocabulary = sorted(df.keys(), key=lambda t: df[t], reverse=True)[:2000]
        self.vocabulary = vocabulary

        N = len(docs)
        self.idf = {term: (log((N + 1) / (df.get(term, 0) + 1)) + 1.0) for term in vocabulary}

        # Compute class priors.
        spam_count = sum(1 for y in labels if y == "spam")
        ham_count = N - spam_count
        self.class_log_priors = {
            "spam": log((spam_count + 1e-9) / N),
            "ham": log((ham_count + 1e-9) / N),
        }

        # Compute class term probabilities using TF-IDF-weighted pseudo-counts.
        alpha = 1.0  # Laplace smoothing
        vocab_size = len(vocabulary) or 1

        class_term_weight_sum: Dict[str, Dict[str, float]] = {"spam": {}, "ham": {}}
        class_weight_totals: Dict[str, float] = {"spam": 0.0, "ham": 0.0}

        for doc_terms, y in zip(docs_terms, labels):
            term_counts: Dict[str, int] = {}
            for t in doc_terms:
                if t in self.idf:
                    term_counts[t] = term_counts.get(t, 0) + 1

            # Apply TF-IDF weighting to turn counts into "evidence".
            # TF normalization is not critical here; we use counts*idf.
            for term, cnt in term_counts.items():
                w = float(cnt) * self.idf.get(term, 0.0)
                class_term_weight_sum[y][term] = class_term_weight_sum[y].get(term, 0.0) + w
                class_weight_totals[y] += w

        class_term_log_probs: Dict[str, Dict[str, float]] = {"spam": {}, "ham": {}}
        for y in ["spam", "ham"]:
            denom = class_weight_totals[y] + alpha * vocab_size
            for term in vocabulary:
                numer = class_term_weight_sum[y].get(term, 0.0) + alpha
                class_term_log_probs[y][term] = log(numer / denom)

        self.class_term_log_probs = class_term_log_probs

    def extract_features(self, text: str) -> Dict[str, object]:
        """Extract keyword/pattern features from email text."""
        text_lower = (text or "").lower()

        features: Dict[str, object] = {
            "spam_keyword_count": 0,
            "phishing_pattern_count": 0,
            "has_urgent_words": False,
            "has_money_words": False,
            "has_link_words": False,
            "excessive_punctuation": False,
            "all_caps_words": 0,
            "suspicious_patterns": [],
        }

        for keyword in self.SPAM_KEYWORDS:
            if keyword in text_lower:
                features["spam_keyword_count"] = int(features["spam_keyword_count"]) + 1

                if keyword in {"urgent", "act now", "limited time", "offer expires"}:
                    features["has_urgent_words"] = True
                if keyword in {"cash", "money", "prize", "free", "winner"}:
                    features["has_money_words"] = True
                if keyword in {"click here", "click link"}:
                    features["has_link_words"] = True

        # phishing patterns
        suspicious: List[str] = []
        for pattern in self.PHISHING_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                features["phishing_pattern_count"] = int(features["phishing_pattern_count"]) + len(matches)
                suspicious.extend([m if isinstance(m, str) else str(m) for m in matches])

        features["suspicious_patterns"] = suspicious[:10]

        punctuation_count = len(re.findall(r"[!?]{2,}", text or ""))
        features["excessive_punctuation"] = punctuation_count > 2

        words = (text or "").split()
        features["all_caps_words"] = sum(1 for w in words if w.isupper() and len(w) > 2)

        return features

    def detect_spam(self, email_text: str) -> Dict[str, object]:
        """Detect spam/phishing using TF-IDF+NB probability + rule-based boosting."""
        features = self.extract_features(email_text)

        tokens = self._ngrams(self._tokenize(email_text or ""))

        # Score spam/ham with log-probabilities.
        term_counts: Dict[str, int] = {}
        for t in tokens:
            if t in self.idf:
                term_counts[t] = term_counts.get(t, 0) + 1

        spam_score = self.class_log_priors["spam"]
        ham_score = self.class_log_priors["ham"]
        for term, cnt in term_counts.items():
            # TF-IDF weight as pseudo-count
            w = float(cnt) * self.idf.get(term, 0.0)
            # Multiply by log P(term|class) in a multinomial-ish way
            spam_score += w * self.class_term_log_probs["spam"].get(term, 0.0)
            ham_score += w * self.class_term_log_probs["ham"].get(term, 0.0)

        # Convert to probability with softmax (stable).
        m = max(spam_score, ham_score)
        spam_prob = exp(spam_score - m)
        ham_prob = exp(ham_score - m)
        spam_probability = float(spam_prob / (spam_prob + ham_prob)) if (spam_prob + ham_prob) > 0 else 0.5

        # Rule score in [0..1]
        spam_keyword_count = int(features["spam_keyword_count"])
        phishing_pattern_count = int(features["phishing_pattern_count"])
        rule_score = 0.0
        rule_score += min(1.0, spam_keyword_count / 5.0) * 0.4
        rule_score += min(1.0, phishing_pattern_count / 2.0) * 0.4
        rule_score += (0.1 if features["has_urgent_words"] else 0.0)
        rule_score += (0.1 if features["has_money_words"] else 0.0)
        rule_score += (0.05 if features["excessive_punctuation"] else 0.0)
        rule_score += min(0.05, int(features["all_caps_words"]) / 50.0)

        # Combine: ML is the majority signal; rules provide interpretability + boost.
        confidence = max(0.0, min(1.0, (0.65 * spam_probability) + (0.35 * rule_score)))

        # Final decision: combine ML and rules.
        is_spam = confidence >= 0.55
        classification = "SPAM" if is_spam else "LEGITIMATE"
        risk_level = "HIGH" if confidence >= 0.8 else "MEDIUM" if confidence >= 0.5 else "LOW"

        reasons: List[str] = []
        reasons.append(f"Model confidence (spam probability): {spam_probability:.2f}")
        if spam_keyword_count:
            reasons.append(f"Spam keyword matches: {spam_keyword_count}")
        if phishing_pattern_count:
            reasons.append(f"Phishing pattern matches: {phishing_pattern_count}")
        if features["has_urgent_words"]:
            reasons.append("Urgent language detected")
        if features["has_money_words"]:
            reasons.append("Money/reward-related terms detected")
        if features["has_link_words"]:
            reasons.append("Link/call-to-action language detected")
        if features["excessive_punctuation"]:
            reasons.append("Excessive punctuation detected")

        if not reasons or reasons == ["Model confidence (spam probability): {:.2f}".format(spam_probability)]:
            reasons = ["No suspicious patterns detected"]

        return {
            "is_spam": bool(is_spam),
            "confidence": round(confidence, 3),
            "classification": classification,
            "risk_level": risk_level,
            "reasons": reasons,
            "features": features,
        }

import random
import re
from typing import Dict, List, Tuple

from config import settings


# torch/transformers are optional. Rule-based mode must work when unavailable.
try:
    import torch  # type: ignore
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline  # type: ignore

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


class ChatbotService:
    """
    Chatbot service.

    Intent detection is priority-ordered (list of tuples; order matters) so more
    specific topics match before generic "question" catch-all.
    """

    # ORDER MATTERS (most specific first)
    INTENT_PATTERNS: List[Tuple[str, List[str]]] = [
        ("identity", [r"\b(who are you|what are you|your name)\b"]),
        ("capability", [r"\b(can you|are you able|what can you)\b"]),
        (
            "ai_topic",
            [
                r"\b(machine learning|deep learning|neural networks?)\b",
                r"\b(nlp|natural language processing)\b",
                r"\b(computer vision)\b",
                r"\b(artificial intelligence|ai)\b",
            ],
        ),
        (
            "coding",
            [
                r"\b(python|javascript|typescript|react|node|sql|django|fastapi)\b",
                r"\b(write code|show code|implement|debug|bug|error)\b",
                r"\b(algorithm|data structure)\b",
            ],
        ),
        ("resume", [r"\b(resume|cv|ats)\b"]),
        ("spam", [r"\b(spam|phishing|phish|scam)\b"]),
        ("summary", [r"\b(summarize|summary|bullet points|key points)\b"]),
        ("platform", [r"\b(platform|what is this|how does this work|features)\b"]),
        ("greeting", [r"\b(hi|hello|hey|greetings)\b", r"^(good morning|good afternoon|good evening)\b"]),
        ("farewell", [r"\b(bye|goodbye|see you|farewell)\b"]),
        ("gratitude", [r"\b(thank|thanks|appreciate)\b"]),
        ("help", [r"\b(help|assist|support)\b"]),
        ("question", [r"\?$", r"\b(what|when|where|who|why|how|can|could|would|is|are)\b"]),
    ]

    KNOWLEDGE_BASE: Dict[str, List[str]] = {
        "identity": [
            "I'm your AI Productivity Assistant.\n\nAsk me about:\n- Resume analysis (ATS heuristics)\n- Spam/phishing detection\n- Notes summarization\n- The built-in analytics/dashboard\n- General AI questions",
            "I'm a helpful AI assistant inside your productivity suite.\nTell me what you're working on, and I'll route you to the right module.",
        ],
        "capability": [
            "I can help you automate common productivity workflows, including:\n- Uploading a resume to extract skills + ATS heuristics\n- Checking text for likely spam/phishing signals\n- Summarizing long notes into key bullet points\n- Answering questions and guiding you on using the platform",
            "Yes. Tell me your goal (resume, spam, summary, or AI/coding question) and I'll respond with a tailored, practical answer.",
        ],
        "ai_topic": [
            "Machine Learning (ML) is a way to build systems that learn patterns from data instead of being explicitly programmed.\n\nCommon types:\n- Supervised learning (labeled data)\n- Unsupervised learning (find structure)\n- Reinforcement learning (reward-driven)\n\nIf you want, tell me what you're trying to predict or understand and I'll outline a practical approach.",
            "Artificial Intelligence is the broad field of making computers perform tasks that normally require human intelligence.\n\nMachine Learning is one major subfield of AI.\n- NLP helps computers work with text\n- Computer Vision helps with images/video\n- Deep Learning is ML using neural networks\n\nWhat domain are you interested in (text, images, or recommendations)?",
            "Natural Language Processing (NLP) focuses on understanding and generating human language.\n\nTypical tasks:\n- Classification (spam/intent)\n- Extraction (key entities/skills)\n- Summarization\n- Chat assistants\n\nWant an example pipeline for NLP?",
        ],
        "coding": [
            "I can help with coding by suggesting algorithms, debugging strategies, and implementation patterns.\n\nTo be specific, paste:\n- The error message (stack trace)\n- The relevant code snippet\n- What you expected vs what happened",
            "Sure - share your requirements and any constraints (language, runtime, libraries). I'll propose a clean approach and edge cases to test.",
        ],
        "resume": [
            "Resume mode: I can analyze your resume for skill matches and ATS-friendly structure.\n\nWhat I check heuristically:\n- Contact info presence (email/phone)\n- Section coverage (skills/experience/education/projects)\n- Action verbs and overall completeness\n\nIf you upload your resume (PDF/TXT), I'll return:\n- matched skills + missing skills\n- an ATS score + feedback",
            "Send your resume text (or upload PDF/TXT) and list any target skills you care about. I'll compute a match score and highlight what's missing for ATS compatibility.",
        ],
        "spam": [
            "Spam/phishing mode: I'll look for suspicious keywords + patterns and combine that with an ML probability signal.\n\nTypical red flags:\n- urgent/act-now language\n- money/reward terms\n- account-verification wording\n- suspicious call-to-action links\n\nPaste the email text and I'll classify it with confidence + reasons.",
            "If you paste the message content, I can estimate whether it's likely spam or phishing and explain the main signals I detected.",
        ],
        "summary": [
            "Summary mode: I'll generate an extractive summary (key sentences) and a short bullet list.\n\nHow to get better results:\n- Include the full context\n- Keep sentences complete\n- Add any focus areas you want emphasized\n\nPaste your text and tell me your target length if you have one.",
            "I can summarize your notes into:\n- a concise paragraph\n- 5 bullet points\n- key terms\n\nSend the text when you're ready.",
        ],
        "platform": [
            "Welcome to the AI Productivity Suite.\n\nModules you can use right now:\n- Resume Analyzer: upload PDF/TXT; get skill matches + ATS feedback\n- Spam/Phishing Detector: paste email text; get risk + reasons\n- Notes Summarizer: paste notes; get extractive summary + bullets\n- AI Chatbot: ask questions or request module-specific guidance\n- Analytics Dashboard: track module usage\n\nTip: If you're unsure where to start, say what your goal is (resume, spam, summary, or a general AI/coding question).",
            "Here's how the platform works:\n- The frontend sends requests to `/api/*`\n- The backend runs fast, rule-based services (no network model downloads required)\n- Results are stored for analytics\n\nTell me which module you want and what input you have.",
        ],
        "greeting": [
            "Hello! How can I help you today?",
            "Hi there - what are you working on? Resume, spam detection, summarization, or an AI/coding question?",
        ],
        "farewell": [
            "Goodbye! Come back anytime if you need help.",
            "See you later - hope your day goes smoothly.",
        ],
        "gratitude": [
            "You're welcome! If you want, I can help you run one of the modules next.",
            "Glad I could help. What's the next task?",
        ],
        "help": [
            "I can help with:\n- Resume analysis (ATS heuristics)\n- Spam/phishing checks\n- Extractive notes summarization\n- General AI/coding questions\n\nTell me your goal in one sentence and I'll route you.",
            "Need guidance? Share your goal (resume/spam/summary/platform) and I'll suggest the best next step.",
        ],
        "question": [
            "That's a good question. Can you share a bit more context about your goal (resume/spam/summary or a specific topic)?",
            "I can help - what exactly do you want to accomplish, and what constraints do you have (time, format, audience)?",
        ],
    }

    def __init__(self) -> None:
        self.model_name = settings.CHATBOT_MODEL
        self.max_length = settings.MAX_RESPONSE_LENGTH
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.device = "cpu"

        if not _TORCH_AVAILABLE:
            # Rule-based fallback will be used.
            return

        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"  # type: ignore[name-defined]
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
            )
        except Exception:
            # Model load failures shouldn't break the app.
            self.model = None
            self.tokenizer = None
            self.generator = None

    def detect_intent(self, message: str) -> Tuple[str, float]:
        message_lower = (message or "").lower().strip()
        if not message_lower:
            return "question", 0.5

        for intent, patterns in self.INTENT_PATTERNS:
            for pattern in patterns:
                if re.search(pattern, message_lower, flags=re.IGNORECASE):
                    # Slightly higher confidence for specific topics.
                    confidence = 0.9 if intent in {"ai_topic", "coding", "resume", "spam", "summary", "platform"} else 0.85
                    return intent, confidence

        return "question", 0.6

    def build_context(self, conversation_history: List[Dict], max_context: int = 5) -> str:
        if not conversation_history:
            return ""
        recent_messages = conversation_history[-max_context:]
        context_parts: List[str] = []
        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                context_parts.append(f"Human: {content}")
            else:
                context_parts.append(f"Assistant: {content}")
        return "\n".join(context_parts)

    def _fallback_response(self, message: str, intent: str) -> str:
        options = self.KNOWLEDGE_BASE.get(intent) or self.KNOWLEDGE_BASE["question"]
        return random.choice(options)

    def generate_response_with_model(self, prompt: str, context: str = "") -> str:
        if self.generator is None or self.tokenizer is None:
            return self._fallback_response(prompt, self.detect_intent(prompt)[0])

        try:
            if context:
                full_prompt = f"{context}\nHuman: {prompt}\nAssistant:"
            else:
                full_prompt = f"Human: {prompt}\nAssistant:"

            outputs = self.generator(
                full_prompt,
                max_length=len(full_prompt.split()) + self.max_length,
                num_return_sequences=1,
                temperature=0.8,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                repetition_penalty=1.2,
            )

            generated_text = outputs[0].get("generated_text", "")
            if "Assistant:" in generated_text:
                response = generated_text.split("Assistant:")[-1].strip()
                response = response.split("Human:")[0].strip()
                # Keep first paragraph-ish segment
                response = response.split("\n")[0].strip()
                return response if response else self._fallback_response(prompt, self.detect_intent(prompt)[0])

            return self._fallback_response(prompt, self.detect_intent(prompt)[0])
        except Exception:
            return self._fallback_response(prompt, self.detect_intent(prompt)[0])

    def chat(self, message: str, conversation_history: List[Dict] | None = None) -> Dict:
        intent, _intent_confidence = self.detect_intent(message)

        context = ""
        if conversation_history:
            context = self.build_context(conversation_history, max_context=settings.MAX_CONTEXT_LENGTH)

        if self.model is not None and self.generator is not None:
            response = self.generate_response_with_model(message, context)
            model_used = self.model_name
        else:
            response = self._fallback_response(message, intent)
            model_used = "fallback"

        # Confidence: base + a little bump if response is multi-line/detailed.
        confidence = 0.82 if intent != "question" else 0.72
        if len(response) > 120:
            confidence = min(0.99, confidence + 0.08)
        if "\n" in response:
            confidence = min(0.99, confidence + 0.05)

        return {
            "response": response,
            "intent": intent,
            "confidence": round(confidence, 2),
            "has_context": bool(conversation_history),
            "model_used": model_used,
            "context_length": len(conversation_history) if conversation_history else 0,
        }

    def get_model_info(self) -> Dict:
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.model is not None,
            "max_response_length": self.max_length,
            "max_context_length": settings.MAX_CONTEXT_LENGTH,
        }

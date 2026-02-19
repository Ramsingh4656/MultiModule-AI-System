import torch
import re
import random
from typing import Dict, List, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from config import settings
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class ChatbotService:
    """
    Real AI Chatbot Service using HuggingFace Transformers
    Provides context-aware, dynamic conversational AI similar to ChatGPT
    """
    
    # Intent patterns for better response generation
    INTENT_PATTERNS = {
        'greeting': [r'\b(hi|hello|hey|greetings)\b', r'^(good morning|good afternoon|good evening)'],
        'farewell': [r'\b(bye|goodbye|see you|farewell)\b'],
        'gratitude': [r'\b(thank|thanks|appreciate)\b'],
        'question': [r'\?$', r'\b(what|when|where|who|why|how|can|could|would|is|are)\b'],
        'help': [r'\b(help|assist|support)\b'],
        'capability': [r'\b(can you|are you able|what can you)\b'],
        'identity': [r'\b(who are you|what are you|your name)\b'],
    }
    
    def __init__(self):
        """Initialize the chatbot with GPT-2 model"""
        self.model_name = settings.CHATBOT_MODEL
        self.max_length = settings.MAX_RESPONSE_LENGTH
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading chatbot model: {self.model_name} on {self.device}...")
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            print("Chatbot model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None
            self.tokenizer = None
            self.generator = None
    
    def detect_intent(self, message: str) -> Tuple[str, float]:
        """Detect user intent from message"""
        message_lower = message.lower().strip()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent, 0.85
        
        return 'general', 0.6
    
    def build_context(self, conversation_history: List[Dict], max_context: int = 5) -> str:
        """Build conversation context from history"""
        if not conversation_history:
            return ""
        
        # Get last N messages
        recent_messages = conversation_history[-max_context:]
        
        # Build context string
        context_parts = []
        for msg in recent_messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                context_parts.append(f"Human: {content}")
            else:
                context_parts.append(f"Assistant: {content}")
        
        return "\n".join(context_parts)
    
    def generate_response_with_model(self, prompt: str, context: str = "") -> str:
        """Generate response using GPT-2 model"""
        if self.generator is None:
            return self._fallback_response(prompt)
        
        try:
            # Build full prompt with context
            if context:
                full_prompt = f"{context}\nHuman: {prompt}\nAssistant:"
            else:
                full_prompt = f"Human: {prompt}\nAssistant:"
            
            # Generate response
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
                repetition_penalty=1.2
            )
            
            # Extract generated text
            generated_text = outputs[0]['generated_text']
            
            # Extract only the assistant's response
            if "Assistant:" in generated_text:
                response = generated_text.split("Assistant:")[-1].strip()
                # Clean up response
                response = response.split("Human:")[0].strip()
                response = response.split("\n")[0].strip()
                
                # Remove incomplete sentences
                if response and not response[-1] in '.!?':
                    sentences = response.split('.')
                    if len(sentences) > 1:
                        response = '.'.join(sentences[:-1]) + '.'
                
                return response if response else self._fallback_response(prompt)
            
            return self._fallback_response(prompt)
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Generate fallback response when model fails"""
        intent, _ = self.detect_intent(prompt)
        
        fallback_responses = {
            'greeting': [
                "Hello! How can I assist you today?",
                "Hi there! What can I help you with?",
                "Hey! I'm here to help. What do you need?"
            ],
            'farewell': [
                "Goodbye! Feel free to return if you need anything.",
                "See you later! Have a great day!",
                "Take care! I'm here whenever you need assistance."
            ],
            'gratitude': [
                "You're welcome! Happy to help!",
                "My pleasure! Let me know if you need anything else.",
                "Glad I could help!"
            ],
            'help': [
                "I'm here to assist you with various tasks. You can ask me questions, request information, or just have a conversation!",
                "I can help you with many things! Just ask me a question or tell me what you need.",
            ],
            'capability': [
                "I'm an AI assistant that can help answer questions, provide information, and have conversations with you. What would you like to know?",
                "I can assist with answering questions, providing explanations, and discussing various topics. How can I help you today?"
            ],
            'identity': [
                "I'm an AI assistant designed to help you with information and tasks. Think of me as your helpful digital companion!",
                "I'm an AI chatbot built to assist users like you. I'm here to answer questions and provide helpful information."
            ],
            'general': [
                "That's an interesting point. Could you tell me more about what you're looking for?",
                "I understand. How can I help you with that?",
                "Interesting! What specific information do you need?",
                "I'm here to help. Could you provide more details about what you need?"
            ]
        }
        
        responses = fallback_responses.get(intent, fallback_responses['general'])
        return random.choice(responses)
    
    def enhance_response(self, response: str, intent: str) -> str:
        """Enhance response based on intent"""
        # Add personality and natural language
        if intent == 'question' and '?' not in response:
            if not response.endswith(('.', '!', '?')):
                response += '.'
        
        # Ensure proper capitalization
        if response and response[0].islower():
            response = response[0].upper() + response[1:]
        
        return response
    
    def calculate_confidence(self, response: str, intent: str) -> float:
        """Calculate confidence score for response"""
        base_confidence = 0.75
        
        # Adjust based on response quality
        if len(response) > 20:
            base_confidence += 0.1
        
        if intent in ['greeting', 'farewell', 'gratitude']:
            base_confidence += 0.15
        
        # Check for complete sentences
        if response.endswith(('.', '!', '?')):
            base_confidence += 0.05
        
        return min(round(base_confidence, 2), 0.99)
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Main chat method - generates context-aware responses
        
        Args:
            message: User's input message
            conversation_history: List of previous messages for context
        
        Returns:
            Dict with response, intent, confidence, and metadata
        """
        # Detect intent
        intent, intent_confidence = self.detect_intent(message)
        
        # Build context from history
        context = ""
        if conversation_history:
            context = self.build_context(
                conversation_history,
                max_context=settings.MAX_CONTEXT_LENGTH
            )
        
        # Generate response
        if self.model is not None:
            response = self.generate_response_with_model(message, context)
        else:
            response = self._fallback_response(message)
        
        # Enhance response
        response = self.enhance_response(response, intent)
        
        # Calculate confidence
        confidence = self.calculate_confidence(response, intent)
        
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'has_context': len(conversation_history) > 0 if conversation_history else False,
            'model_used': self.model_name if self.model else 'fallback',
            'context_length': len(conversation_history) if conversation_history else 0
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'is_loaded': self.model is not None,
            'max_response_length': self.max_length,
            'max_context_length': settings.MAX_CONTEXT_LENGTH
        }

import PyPDF2
import re
import json
from typing import Dict, List, Tuple
from pathlib import Path
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class ResumeAnalyzerService:
    """Service for analyzing resumes and extracting skills"""
    
    # Common technical skills database
    SKILL_DATABASE = {
        'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin'],
        'web': ['react', 'angular', 'vue', 'html', 'css', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'nextjs'],
        'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
        'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
        'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision', 'ai'],
        'tools': ['git', 'github', 'gitlab', 'jira', 'agile', 'scrum', 'rest api', 'graphql'],
        'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'analytical', 'project management']
    }
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text using NLP"""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.SKILL_DATABASE.items():
            found_in_category = []
            for skill in skills:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_in_category.append(skill)
            
            if found_in_category:
                found_skills[category] = found_in_category
        
        return found_skills
    
    def calculate_match_score(self, found_skills: Dict[str, List[str]], required_skills: List[str]) -> Tuple[float, List[str]]:
        """Calculate match score against required skills"""
        if not required_skills:
            return 100.0, []
        
        # Flatten found skills
        all_found_skills = []
        for skills_list in found_skills.values():
            all_found_skills.extend([s.lower() for s in skills_list])
        
        # Normalize required skills
        required_skills_lower = [s.lower().strip() for s in required_skills]
        
        # Calculate matches
        matched = 0
        missing_skills = []
        
        for req_skill in required_skills_lower:
            if any(req_skill in found_skill or found_skill in req_skill for found_skill in all_found_skills):
                matched += 1
            else:
                missing_skills.append(req_skill)
        
        score = (matched / len(required_skills_lower)) * 100 if required_skills_lower else 100.0
        return round(score, 2), missing_skills
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
        
        return contact_info
    
    def analyze_resume(self, file_path: Path, required_skills: List[str] = None) -> Dict:
        """Main method to analyze resume"""
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() == '.txt':
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or TXT.")
        
        # Extract skills
        found_skills = self.extract_skills(text)
        
        # Calculate match score
        match_score, missing_skills = self.calculate_match_score(found_skills, required_skills or [])
        
        # Extract contact info
        contact_info = self.extract_contact_info(text)
        
        return {
            'extracted_text': text[:500] + '...' if len(text) > 500 else text,
            'skills_found': found_skills,
            'match_score': match_score,
            'missing_skills': missing_skills,
            'contact_info': contact_info,
            'total_skills_found': sum(len(skills) for skills in found_skills.values())
        }

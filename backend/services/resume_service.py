import PyPDF2
import re
from math import log
from pathlib import Path
from typing import Dict, List, Tuple


class ResumeAnalyzerService:
    """Service for analyzing resumes and extracting skills + ATS heuristics."""

    # Common technical skills database
    SKILL_DATABASE = {
        "programming": [
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "ruby",
            "go",
            "rust",
            "php",
            "swift",
            "kotlin",
        ],
        "web": [
            "react",
            "angular",
            "vue",
            "html",
            "css",
            "nodejs",
            "express",
            "django",
            "flask",
            "fastapi",
            "nextjs",
        ],
        "database": [
            "sql",
            "mysql",
            "postgresql",
            "mongodb",
            "redis",
            "elasticsearch",
            "oracle",
            "sqlite",
        ],
        "cloud": [
            "aws",
            "azure",
            "gcp",
            "docker",
            "kubernetes",
            "terraform",
            "jenkins",
            "ci/cd",
        ],
        "ml_ai": [
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "nlp",
            "computer vision",
            "ai",
        ],
        "tools": ["git", "github", "gitlab", "jira", "agile", "scrum", "rest api", "graphql"],
        "soft_skills": [
            "leadership",
            "communication",
            "teamwork",
            "problem solving",
            "analytical",
            "project management",
        ],
    }

    ACTION_VERBS = [
        "developed",
        "designed",
        "built",
        "implemented",
        "created",
        "optimized",
        "improved",
        "analyzed",
        "led",
        "launched",
        "delivered",
        "managed",
        "implemented",
        "achieved",
        "engineered",
        "trained",
        "deployed",
        "maintained",
        "integrated",
    ]

    SECTION_KEYWORDS = [
        "summary",
        "objective",
        "skills",
        "experience",
        "education",
        "projects",
        "certifications",
    ]

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    # `extract_text()` can return None depending on PDF; guard it.
                    page_text = page.extract_text() or ""
                    text += page_text
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text using simple keyword matching."""
        text_lower = text.lower()
        found_skills: Dict[str, List[str]] = {}

        for category, skills in self.SKILL_DATABASE.items():
            found_in_category: List[str] = []
            for skill in skills:
                # Word-boundary matching works best for single tokens, but also
                # behaves reasonably for multi-word phrases like "machine learning".
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, text_lower, flags=re.IGNORECASE):
                    found_in_category.append(skill)

            if found_in_category:
                found_skills[category] = found_in_category

        return found_skills

    def calculate_match_score(
        self, found_skills: Dict[str, List[str]], required_skills: List[str]
    ) -> Tuple[float, List[str]]:
        """Calculate match score against required skills."""
        if not required_skills:
            return 100.0, []

        # Flatten found skills
        all_found_skills: List[str] = []
        for skills_list in found_skills.values():
            all_found_skills.extend([s.lower() for s in skills_list])

        # Normalize required skills
        required_skills_lower = [s.lower().strip() for s in required_skills if s and s.strip()]
        if not required_skills_lower:
            return 100.0, []

        matched = 0
        missing_skills: List[str] = []

        for req_skill in required_skills_lower:
            if any(req_skill in found_skill or found_skill in req_skill for found_skill in all_found_skills):
                matched += 1
            else:
                missing_skills.append(req_skill)

        score = (matched / len(required_skills_lower)) * 100
        return round(score, 2), missing_skills

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume."""
        contact_info: Dict[str, str] = {}

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]

        phone_pattern = r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}"
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info["phone"] = phones[0]

        return contact_info

    def calculate_ats_score(self, full_text: str, found_skills: Dict[str, List[str]]) -> Tuple[float, List[str]]:
        """Heuristic ATS scoring without external NLP dependencies."""
        text = full_text or ""
        text_lower = text.lower()

        # Word count is a strong proxy for "complete" resumes.
        words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text_lower)
        word_count = len(words)

        contact_info = self.extract_contact_info(text)
        contact_present = bool(contact_info)

        # Simple section detection by keyword presence.
        present_sections = []
        for sec in self.SECTION_KEYWORDS:
            # Try to match section-like headings (line starts) OR plain keyword mentions.
            heading_pat = rf"(?im)^[\s\W]*{re.escape(sec)}[\s\W]*$"
            if re.search(heading_pat, text) or re.search(rf"\b{re.escape(sec)}\b", text_lower):
                present_sections.append(sec)

        # Action verbs help ATS parsing and human readability.
        action_count = 0
        for verb in self.ACTION_VERBS:
            # count occurrences of the verb as a whole word
            action_count += len(re.findall(rf"\b{re.escape(verb)}\b", text_lower))

        # Score components (sum to <= 100)
        word_component = 0.0
        if word_count >= 300:
            word_component = 35.0
        elif word_count >= 200:
            word_component = 20.0 + (word_count - 200) / 100 * 15.0
        elif word_count >= 120:
            word_component = 10.0 + (word_count - 120) / 80 * 10.0
        else:
            word_component = 5.0

        contact_component = 20.0 if contact_present else 0.0

        section_component = 0.0
        # Normalize by expecting up to ~5-6 useful sections.
        section_component = 25.0 * min(len(present_sections) / 5.0, 1.0)

        action_component = 15.0 * min(action_count / 10.0, 1.0)

        raw_score = word_component + contact_component + section_component + action_component
        ats_score = max(0.0, min(100.0, round(raw_score, 2)))

        # Build feedback
        feedback: List[str] = []
        if word_count < 150:
            feedback.append("Resume looks too short. Aim for roughly 1+ page and include more quantified impact.")
        if not contact_present:
            feedback.append("Add clear contact details (email and phone) near the top so recruiters can find them.")

        expected_sections = ["skills", "experience", "education", "projects"]
        missing = [s for s in expected_sections if s not in present_sections]
        if missing:
            feedback.append(f"Missing or weak ATS section coverage: {', '.join(missing)}.")

        if action_count < 3:
            feedback.append("Use more action verbs (e.g., developed, built, implemented, optimized) to describe impact.")

        # Soft check: if the resume has almost no recognized skills, suggest adding a skills section.
        total_found_skills = sum(len(v) for v in found_skills.values())
        if total_found_skills < 3:
            feedback.append("Add a dedicated Skills section with specific technologies matching the target job description.")

        # Ensure we always return at least one actionable item.
        if not feedback:
            feedback.append("Overall structure looks ATS-friendly. Consider tightening wording and adding measurable outcomes.")

        return ats_score, feedback

    def analyze_resume(self, file_path: Path, required_skills: List[str] | None = None) -> Dict:
        """Main method to analyze resume."""
        # Extract text based on file type
        if file_path.suffix.lower() == ".pdf":
            text = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() == ".txt":
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or TXT.")

        found_skills = self.extract_skills(text)
        match_score, missing_skills = self.calculate_match_score(found_skills, required_skills or [])
        contact_info = self.extract_contact_info(text)

        ats_score, ats_feedback = self.calculate_ats_score(text, found_skills)

        total_skills_found = sum(len(skills) for skills in found_skills.values())
        truncated_text = text[:1500] + ("..." if len(text) > 1500 else "")

        return {
            "extracted_text": truncated_text,
            "skills_found": found_skills,
            "match_score": match_score,
            "missing_skills": missing_skills,
            "contact_info": contact_info,
            "total_skills_found": total_skills_found,
            "ats_score": ats_score,
            "ats_feedback": ats_feedback,
        }

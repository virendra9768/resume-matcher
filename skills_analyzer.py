import pandas as pd
import re

# Map variations to a single standard name
SKILL_ALIASES = {
    "React.js": "React", "ReactJS": "React",
    "Node.js": "Node", "NodeJS": "Node",
    "Amazon Web Services": "AWS",
    "GCP": "Google Cloud",
    "Postgres": "PostgreSQL",
    "Vue.js": "Vue",
    "Golang": "Go",
    "RESTful APIs": "API", "REST": "API"
}

# Massively expanded dictionary including QA, Automation, and Data
COMPREHENSIVE_SKILLS = [
    # QA, Testing & Automation
    "Playwright", "Selenium", "Cypress", "Appium", "Postman", "REST Assured", "QA", "Quality Assurance", 
    "API Testing", "UI Testing", "Regression Testing", "Integration Testing", "Functional Testing", "TDD", "BDD",
    
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Ruby", "Go", "Rust", "Swift", "Kotlin", "PHP", "Dart",
    
    # Frontend & Mobile
    "React", "React Native", "Vue", "Angular", "HTML", "CSS", "Tailwind", "Next.js", "Flutter",
    
    # Backend & APIs
    "Node", "Express", "Django", "Flask", "FastAPI", "Spring", "Spring Boot", "GraphQL", "gRPC", "Microservices", "API",
    
    # Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "NoSQL", "Redis", "Elasticsearch", "SQL Database",
    
    # Cloud, DevOps & Tools
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Linux", "CI/CD", "Jenkins", "Git", "GitHub", "Terraform", "DevOps",
    
    # Data & AI
    "Machine Learning", "Data Analysis", "Pandas", "TensorFlow", "PyTorch", "NLP", "GenAI", "ChatGPT", "Copilot",
    
    # Architecture
    "System Design", "Agile", "Scrum", "OOP", "Page Object Model", "POM"
]

# Short words that are highly likely to cause false positives if we don't enforce boundaries
STRICT_MATCH_WORDS = {"go", "java", "api", "git", "sql", "qa", "c++", "c#", "php", "pom"}

def analyze_skill_gaps(resume_text: str, jd_text: str):
    # Normalize texts by replacing known aliases
    resume_norm = resume_text
    jd_norm = jd_text
    
    for alias, standard in SKILL_ALIASES.items():
        resume_norm = re.sub(rf'\b{re.escape(alias)}\b', standard, resume_norm, flags=re.IGNORECASE)
        jd_norm = re.sub(rf'\b{re.escape(alias)}\b', standard, jd_norm, flags=re.IGNORECASE)

    resume_lower = resume_norm.lower()
    jd_lower = jd_norm.lower()
    
    chart_data = []
    
    for skill in COMPREHENSIVE_SKILLS:
        skill_lower = skill.lower()
        
        # ADAPTIVE REGEX LOGIC
        if skill_lower in STRICT_MATCH_WORDS:
            # Strict boundary: prevents "Java" from matching inside "JavaScript"
            # We use (?<![a-z]) instead of \b to handle C++ and C# safely
            pattern = r'(?<![a-z])' + re.escape(skill_lower) + r'(?![a-z])'
        else:
            # Loose boundary: Catches squished PDF text like "TypeScriptPlaywright"
            pattern = re.escape(skill_lower)
            
        # 1. Check if skill is required in the Job Description
        if re.search(pattern, jd_lower):
            
            # 2. Check if candidate actually has it
            has_skill = re.search(pattern, resume_lower)
            
            chart_data.append({
                "Skill": skill,
                "Required Proficiency": 100, 
                "Candidate Proficiency": 100 if has_skill else 0
            })
            
    df = pd.DataFrame(chart_data)
    
    if not df.empty:
        # Sort so matching skills are on the left, and missing gaps on the right
        df = df.sort_values(by=["Candidate Proficiency", "Skill"], ascending=[False, True])
        
    return df
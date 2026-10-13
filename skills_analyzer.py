import pandas as pd
import re

# Map variations to a single standard name
SKILL_ALIASES = {
    "React.js": "React", "ReactJS": "React",
    "Node.js": "Node", "NodeJS": "Node",
    "Amazon Web Services": "AWS",
    "GCP": "Google Cloud", "Google Cloud Platform": "Google Cloud",
    "Postgres": "PostgreSQL",
    "Vue.js": "Vue", "VueJS": "Vue"
}

COMPREHENSIVE_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", 
    "React", "Vue", "Angular", "Node", "FastAPI", "Django", "Flask",
    "SQL", "PostgreSQL", "MongoDB", "Redis", 
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "CI/CD", "Git"
]

def analyze_skill_gaps(resume_text: str, jd_text: str):
    # Normalize texts by replacing known aliases with their standard names
    resume_norm = resume_text
    jd_norm = jd_text
    
    for alias, standard in SKILL_ALIASES.items():
        # Replace case-insensitively
        resume_norm = re.sub(rf'\b{re.escape(alias)}\b', standard, resume_norm, flags=re.IGNORECASE)
        jd_norm = re.sub(rf'\b{re.escape(alias)}\b', standard, jd_norm, flags=re.IGNORECASE)

    resume_lower = resume_norm.lower()
    jd_lower = jd_norm.lower()
    
    chart_data = []
    
    for skill in COMPREHENSIVE_SKILLS:
        pattern = r'(?<![a-z0-9])' + re.escape(skill.lower()) + r'(?![a-z0-9])'
        
        if re.search(pattern, jd_lower):
            has_skill = re.search(pattern, resume_lower)
            chart_data.append({
                "Skill": skill,
                "Required Proficiency": 100, 
                "Candidate Proficiency": 100 if has_skill else 0
            })
            
    df = pd.DataFrame(chart_data)
    if not df.empty:
        df = df.sort_values(by=["Candidate Proficiency", "Skill"], ascending=[False, True])
        
    return df
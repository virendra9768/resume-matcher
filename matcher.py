import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from skills_analyzer import analyze_skill_gaps
import textwrap

# Load model globally
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def get_document_embedding(text: str) -> np.ndarray:
    """Chunks long text to bypass the 256 token limit and averages the vectors."""
    # Split text into chunks of ~1000 characters (roughly 150-200 tokens)
    chunks = textwrap.wrap(text, width=1000, break_long_words=False)
    if not chunks:
        return np.zeros((1, 384))
        
    chunk_embeddings = model.encode(chunks, convert_to_numpy=True)
    # Average all chunk vectors into one single vector representing the whole document
    document_embedding = np.mean(chunk_embeddings, axis=0)
    return document_embedding.reshape(1, -1)

def compute_match_score(resume_text: str, jd_text: str) -> dict:
    if not resume_text.strip() or not jd_text.strip():
        raise ValueError("Both documents must contain text.")

    # Use the new chunking function instead of direct encoding
    resume_vector = get_document_embedding(resume_text)
    jd_vector = get_document_embedding(jd_text)
    
    raw_cosine = float(cosine_similarity(resume_vector, jd_vector)[0][0])
    
    BASELINE = 0.35
    MAX_EXPECTED = 0.85
    
    if raw_cosine <= BASELINE:
        semantic_score = 0.0
    elif raw_cosine >= MAX_EXPECTED:
        semantic_score = 100.0
    else:
        semantic_score = ((raw_cosine - BASELINE) / (MAX_EXPECTED - BASELINE)) * 100

    skills_df = analyze_skill_gaps(resume_text, jd_text)
    
    if not skills_df.empty:
        total_required = len(skills_df)
        skills_possessed = len(skills_df[skills_df["Candidate Proficiency"] > 0])
        skill_score = (skills_possessed / total_required) * 100
        
        if skill_score == 0:
            semantic_score = semantic_score * 0.5 
            
        final_percentage = (skill_score * 0.6) + (semantic_score * 0.4)
    else:
        skill_score = 0
        final_percentage = semantic_score

    final_percentage = max(0.0, min(100.0, final_percentage))

    return {
        "similarity_score": round(raw_cosine, 4),
        "semantic_score": round(semantic_score, 2),
        "skill_score": round(skill_score, 2),
        "match_percentage": round(final_percentage, 2),
        "embedding_dimensions": resume_vector.shape[1],
        "verdict": get_verdict_category(final_percentage)
    }

def get_verdict_category(percentage: float) -> str:
    if percentage >= 75: return "Strong Match"
    elif percentage >= 55: return "Moderate Match"
    else: return "Low Match"
import streamlit as st
import time
import plotly.express as px
from extractor import extract_document_text
from matcher import compute_match_score
from skills_analyzer import analyze_skill_gaps

# Cache the heavy ML module so it only loads once per server boot
@st.cache_resource
def load_matcher():
    from matcher import compute_match_score
    return compute_match_score

compute_match_score = load_matcher()

# 1. Page Configuration (No more target emoji)
st.set_page_config(page_title="Resume Matcher", layout="wide")

# 2. Premium Minimalist CSS
st.markdown("""
    <style>
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    .gradient-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0ea5e9 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: -0.5px;
    }
    
    /* Theme-agnostic inputs */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid var(--secondary-background-color) !important;
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.3);
    }
    
    .stButton > button[kind="primary"] {
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 13px;
        background: linear-gradient(90deg, #06b6d4 0%, #0ea5e9 100%);
        color: #ffffff;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(6, 182, 212, 0.2);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(6, 182, 212, 0.4);
    }
    
    /* Dynamic Metric Color */
    [data-testid="stMetricValue"] {
        font-size: 4rem !important;
        font-weight: 800 !important;
        letter-spacing: -2px;
        color: var(--text-color) !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Section (Clean typography, no emojis)
st.markdown('<h1 class="gradient-title">AI Resume Matcher</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #a1a1aa; font-size: 1.1rem; font-weight: 400; margin-bottom: 2rem;'>Semantic and technical alignment analysis.</p>", unsafe_allow_html=True)

# 4. Inputs
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<h4 style='color: var(--text-color); font-weight: 600; font-size: 1.1rem;'>Job Description</h4>", unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste the target job description",
        height=250,
        placeholder="Paste job requirements here...",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<h4 style='color: var(--text-color); font-weight: 600; font-size: 1.1rem;'>Your Resume</h4>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your latest resume", 
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"Loaded: {uploaded_file.name}")

st.write("")

# 5. Button (No rocket emoji)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_clicked = st.button("Analyze Match", type="primary", width="stretch")

# 6. Results Logic
if analyze_clicked:
    if not job_description.strip():
        st.toast("Please paste the job description first!", icon="⚠️")
    elif not uploaded_file:
        st.toast("Please upload your resume!", icon="⚠️")
    else:
        progress_text = "Parsing documents and generating AI embeddings..."
        my_bar = st.progress(0, text=progress_text)
        
        try:
            time.sleep(0.4)
            my_bar.progress(30, text="Extracting text from resume...")
            
            file_bytes = uploaded_file.read()
            resume_text = extract_document_text(uploaded_file.name, file_bytes)
            
            if not resume_text:
                st.error("⚠️ Could not extract readable text. Ensure it's not a scanned image.")
                my_bar.empty()
            else:
                my_bar.progress(70, text="Calculating semantic & skill match...")
                
                # Compute Hybrid Match Score
                results = compute_match_score(resume_text, job_description)
                score = results["match_percentage"]
                verdict = results["verdict"]
                
                # Get the Skills DataFrame for the Chart
                skills_df = analyze_skill_gaps(resume_text, job_description)
                
                my_bar.progress(100, text="Analysis complete!")
                time.sleep(0.3)
                my_bar.empty() 
                
                st.divider()
                
                # Display Results
                res_col1, res_col2 = st.columns([1, 2], gap="large")
                
                with res_col1:
                    # Score
                    st.metric(label="Overall Match Score", value=f"{score}%")
                    
                    # Action Badges
                    if score >= 75:
                        badge_html = """
                        <div style="border: 1px solid var(--secondary-background-color); border-left: 4px solid #10b981; background-color: var(--secondary-background-color); border-radius: 4px; padding: 16px; margin: 16px 0;">
                            <h4 style="color: #10b981; margin: 0 0 4px 0; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Action: Should Apply</h4>
                            <p style="color: var(--text-color); margin: 0; font-size: 14px;">High statistical match. Profile aligns strongly with core requirements.</p>
                        </div>
                        """
                        st.balloons() 
                    elif score >= 55:
                        badge_html = """
                        <div style="border: 1px solid var(--secondary-background-color); border-left: 4px solid #f59e0b; background-color: var(--secondary-background-color); border-radius: 4px; padding: 16px; margin: 16px 0;">
                            <h4 style="color: #f59e0b; margin: 0 0 4px 0; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Action: Can Apply</h4>
                            <p style="color: var(--text-color); margin: 0; font-size: 14px;">Moderate match. Be prepared to address specific technical gaps.</p>
                        </div>
                        """
                    else:
                        badge_html = """
                        <div style="border: 1px solid var(--secondary-background-color); border-left: 4px solid #ef4444; background-color: var(--secondary-background-color); border-radius: 4px; padding: 16px; margin: 16px 0;">
                            <h4 style="color: #ef4444; margin: 0 0 4px 0; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Action: Hold</h4>
                            <p style="color: var(--text-color); margin: 0; font-size: 14px;">Low statistical match. Significant requirements missing.</p>
                        </div>
                        """
                    st.html(badge_html)
                    
                    st.markdown(f"**AI Verdict:** {verdict}")
                    
                    with st.expander("📊 View Detailed Analytics"):
                        st.markdown(f"""
                        - **Semantic Score:** {results.get('semantic_score', 0)}%
                        - **Hard Skill Score:** {results.get('skill_score', 0)}%
                        - **Resume Length:** {len(resume_text):,} chars
                        - **JD Length:** {len(job_description):,} chars
                        """)
                        
                with res_col2:
                    st.markdown("### Skill Gap Analysis")
                    
                    if skills_df.empty:
                        st.info("No standard technical skills detected in this Job Description.")
                    else:
                        # Sort dataframe for horizontal display (Plotly draws bottom-to-top)
                        skills_df = skills_df.sort_values(by=["Candidate Proficiency", "Skill"], ascending=[True, False])
                        
                        # Dynamic height so bars never get squished
                        chart_height = max(400, len(skills_df) * 45)
                        
                        fig = px.bar(
                            skills_df, 
                            y="Skill",  
                            x=["Required Proficiency", "Candidate Proficiency"], 
                            barmode="overlay", # Yeh label alignment fix karega
                            orientation="h", 
                            color_discrete_map={
                                "Required Proficiency": "rgba(148, 163, 184, 0.25)", # Universal subtle grey
                                "Candidate Proficiency": "#0ea5e9" # Premium Cyan/Blue
                            }
                        )

                        fig.update_traces(
                            hovertemplate="<b>Skill:</b> %{y}<br><b>%{data.name}:</b> %{x}%<extra></extra>"
                        )
                        
                        fig.update_layout(
                            height=chart_height,
                            bargap=0.3,
                            legend_title_text="",
                            xaxis_title="Proficiency Level",
                            yaxis_title="",
                            xaxis_range=[0, 100], # Changed from 110 to 100 for perfect edge alignment
                            margin=dict(l=0, r=0, t=40, b=0),
                            plot_bgcolor="rgba(0,0,0,0)", 
                            paper_bgcolor="rgba(0,0,0,0)",
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="left",
                                x=0
                            )
                        )
                        
                        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(148, 163, 184, 0.1)", zeroline=False)
                        
                        st.plotly_chart(
                            fig, 
                            width="stretch", 
                            theme="streamlit", 
                            config={'displayModeBar': False} 
                        )
                        
        except Exception as e:
            my_bar.empty()
            st.error(f"⚠️ Error processing request: {str(e)}")
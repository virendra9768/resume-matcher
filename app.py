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

# 1. Page Configuration
st.set_page_config(page_title="AI Resume Matcher", page_icon="🎯", layout="wide")

# 2. Custom CSS for premium UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.title("🎯 AI Resume Matcher")
st.markdown("### *Find out instantly if your profile aligns with the job requirements.*")
st.divider()

# 4. Inputs
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste the target job description",
        height=250,
        placeholder="e.g., We are looking for a Senior Developer with experience in React, Python, and AWS...",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your latest resume", 
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.info(f"✅ Loaded: {uploaded_file.name}")

st.write("")

# 5. Button
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_clicked = st.button("🚀 Analyze Match", type="primary", width="stretch")

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
                        <div style="background-color: rgba(34, 197, 94, 0.15); border: 1px solid #4ade80; border-radius: 8px; padding: 16px; margin: 16px 0;">
                            <h4 style="color: #4ade80; margin: 0 0 8px 0; font-size: 16px; font-family: sans-serif;">🟢 ACTION: SHOULD APPLY</h4>
                            <p style="color: #bbf7d0; margin: 0; font-size: 14px; font-family: sans-serif; line-height: 1.4;">Your profile strongly matches the requirements. Send it!</p>
                        </div>
                        """
                        st.balloons()
                    elif score >= 55:
                        badge_html = """
                        <div style="background-color: rgba(234, 179, 8, 0.15); border: 1px solid #facc15; border-radius: 8px; padding: 16px; margin: 16px 0;">
                            <h4 style="color: #facc15; margin: 0 0 8px 0; font-size: 16px; font-family: sans-serif;">🟡 ACTION: CAN APPLY</h4>
                            <p style="color: #fef08a; margin: 0; font-size: 14px; font-family: sans-serif; line-height: 1.4;">You meet the core needs, but expect some gap questions.</p>
                        </div>
                        """
                    else:
                        badge_html = """
                        <div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid #f87171; border-radius: 8px; padding: 16px; margin: 16px 0;">
                            <h4 style="color: #f87171; margin: 0 0 8px 0; font-size: 16px; font-family: sans-serif;">🔴 ACTION: DON'T APPLY (YET)</h4>
                            <p style="color: #fecaca; margin: 0; font-size: 14px; font-family: sans-serif; line-height: 1.4;">Significant skill gaps. Consider upskilling first.</p>
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
                        fig = px.bar(
                            skills_df, 
                            x="Skill", 
                            y=["Required Proficiency", "Candidate Proficiency"],
                            barmode="group",
                            color_discrete_map={
                                "Required Proficiency": "rgba(148, 163, 184, 0.3)", 
                                "Candidate Proficiency": "#3B82F6"
                            }
                        )
                        
                        fig.update_layout(
                            legend_title_text="",
                            xaxis_title="",
                            yaxis_title="Proficiency Level",
                            yaxis_range=[0, 110],
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
                        
                        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")
                        
                        # displayModeBar=False hides the overlapping controls
                        st.plotly_chart(
                            fig, 
                            width="stretch", 
                            theme="streamlit", 
                            config={'displayModeBar': False} 
                        )
                        
        except Exception as e:
            my_bar.empty()
            st.error(f"⚠️ Error processing request: {str(e)}")
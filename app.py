import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import tempfile
import os
from groq import Groq
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# Initialize Groq client
GROQ_API_KEY = "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"  # Replace with your actual API key
client = Groq(api_key=GROQ_API_KEY)

# Page config
st.set_page_config(
    page_title="Medical Symptom Interpreter", 
    layout="wide", 
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# Modern UI CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe8d6 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ff9800 0%, #f57c00 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.2);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.3);
        transform: translateX(5px);
        border-color: white;
    }
    
    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(255, 152, 0, 0.3);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: white !important;
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Navigation arrows container */
    .nav-arrows-top, .nav-arrows-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 20px 0;
        gap: 20px;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        border-radius: 20px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(255, 152, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-card h3, .metric-card h2 {
        color: white !important;
        margin: 0;
    }
    
    /* Results card - Text color fixed to black */
    .results-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(255, 152, 0, 0.2);
        margin-top: 30px;
        border: 2px solid #ff9800;
    }
    
    .results-card * {
        color: #2c3e50 !important;
    }
    
    .results-card h3 {
        color: #f57c00 !important;
    }
    
    .results-header {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        padding: 15px 20px;
        border-radius: 15px;
        margin: -25px -25px 20px -25px;
    }
    
    .results-header h2, .results-header p {
        color: white !important;
        margin: 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 15px;
        padding: 8px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        color: #666;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white !important;
    }
    
    /* Headers */
    h1 {
        color: #2c3e50 !important;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    
    h2 {
        color: #2c3e50 !important;
        font-weight: 700;
        margin: 20px 0 15px 0;
    }
    
    h3 {
        color: #f57c00 !important;
        font-weight: 600;
        margin: 15px 0 10px 0;
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .welcome-card h2, .welcome-card p {
        color: white !important;
        margin: 0;
    }
    
    /* Patient info card */
    .patient-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 2px solid #ff9800;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.1);
    }
    
    /* History cards */
    .history-card {
        background: #fff9f0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .history-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(255, 152, 0, 0.2);
    }
    
    /* Explanation card for analytics */
    .explanation-card {
        background: #fff9f0;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid #ff9800;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .explanation-card h4 {
        color: #ff9800 !important;
        margin-top: 0;
    }
    
    .explanation-card p, .explanation-card li {
        color: #2c3e50 !important;
    }
    
    /* Footer */
    .footer {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-top: 40px;
        border: 1px solid #ff9800;
    }
    
    /* Custom button */
    .stButton > button {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255, 152, 0, 0.4);
    }
    
    hr {
        margin: 30px 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ff9800, #f57c00, transparent);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'patient_history' not in st.session_state:
    st.session_state.patient_history = []
if 'patient_name' not in st.session_state:
    st.session_state.patient_name = ""
if 'age' not in st.session_state:
    st.session_state.age = 30
if 'gender' not in st.session_state:
    st.session_state.gender = None
if 'medical_history' not in st.session_state:
    st.session_state.medical_history = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Define page order for navigation
PAGES = ["Home", "Checker", "Analytics", "Reports", "About"]
PAGE_NAMES = {
    "Home": " Home",
    "Checker": " Symptom Checker", 
    "Analytics": " Analytics",
    "Reports": " Reports",
    "About": "ℹ About"
}

def navigate_page(direction):
    """Navigate to next or previous page"""
    current_index = PAGES.index(st.session_state.current_page)
    if direction == "next" and current_index < len(PAGES) - 1:
        st.session_state.current_page = PAGES[current_index + 1]
        st.rerun()
    elif direction == "prev" and current_index > 0:
        st.session_state.current_page = PAGES[current_index - 1]
        st.rerun()

def record_audio(duration=5, rate=16000):
    """Record audio from microphone"""
    try:
        with st.spinner(f"🎙️ Recording for {duration} seconds..."):
            recording = sd.rec(int(duration * rate), samplerate=rate, channels=1, dtype='int16')
            sd.wait()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            wav.write(temp_file.name, rate, recording)
            return temp_file.name
    except Exception as e:
        st.error(f"Recording error: {str(e)}")
        return None

def transcribe_audio(audio_file):
    """Transcribe audio using Groq Whisper"""
    try:
        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file, file.read()),
                model="whisper-large-v3-turbo",
                response_format="text"
            )
        return transcription
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return ""

def analyze_symptoms(text, patient_info=None):
    """Analyze symptoms with patient context"""
    if not text:
        return None
    
    context = ""
    if patient_info and patient_info.get('name'):
        context = f"\nPatient: {patient_info.get('name')}, Age: {patient_info.get('age')}, Gender: {patient_info.get('gender')}\nMedical History: {patient_info.get('history', 'None')}\n"
    
    prompt = f"""You are a medical assistant. Analyze these symptoms:
{context}
Symptoms: {text}

Return JSON format:
{{
    "possible_conditions": [
        {{"condition": "Condition name", "confidence": 85, "explanation": "Brief explanation"}}
    ],
    "severity": "Mild or Moderate or Urgent",
    "recommended_action": "self-care or doctor or immediate",
    "symptom_summary": "Brief summary",
    "health_tips": ["Tip 1", "Tip 2", "Tip 3"],
    "medicine_suggestions": ["OTC Medicine with dosage", "Prescription Medicine"],
    "home_remedies": ["Remedy 1", "Remedy 2"],
    "lifestyle_recommendations": ["Recommendation 1"],
    "dietary_suggestions": ["Suggestion 1"],
    "precautions": ["Precaution 1"],
    "estimated_recovery_time": "X days",
    "emergency_warning_signs": ["Sign 1"],
    "doctor_specialty_recommendation": "Specialist"
}}"""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result['patient_name'] = patient_info.get('name', 'Guest') if patient_info else 'Guest'
            return result
        return None
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None

def generate_pdf_report(symptoms, analysis):
    """Generate PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=1, textColor=colors.HexColor('#ff9800'))
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, spaceAfter=12, textColor=colors.HexColor('#f57c00'))
    
    story.append(Paragraph(f"Medical Report - {analysis.get('patient_name', 'Patient')}", title_style))
    story.append(Paragraph(f"Date: {analysis.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Symptoms:", heading_style))
    story.append(Paragraph(symptoms, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Severity Assessment:", heading_style))
    story.append(Paragraph(f"Severity: {analysis.get('severity', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"Recommended Action: {analysis.get('recommended_action', 'N/A').replace('_', ' ').title()}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Possible Conditions:", heading_style))
    for condition in analysis.get('possible_conditions', []):
        if isinstance(condition, dict):
            story.append(Paragraph(f"• {condition.get('condition', 'Unknown')} ({condition.get('confidence', 0)}% confidence)", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Medicine Suggestions:", heading_style))
    for med in analysis.get('medicine_suggestions', []):
        story.append(Paragraph(f"• {med}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Health Tips:", heading_style))
    for tip in analysis.get('health_tips', []):
        story.append(Paragraph(f"• {tip}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Function to render navigation arrows
def render_navigation_arrows():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if PAGES.index(st.session_state.current_page) > 0:
            if st.button("◀ Previous", key="nav_prev_top", use_container_width=True):
                navigate_page("prev")
    with col3:
        if PAGES.index(st.session_state.current_page) < len(PAGES) - 1:
            if st.button("Next ▶", key="nav_next_top", use_container_width=True):
                navigate_page("next")

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🏥 MedAssistant")
    st.markdown("---")
    
    for page in PAGES:
        icon = "🏠" if page == "Home" else "🔍" if page == "Checker" else "📊" if page == "Analytics" else "📄" if page == "Reports" else "ℹ️"
        if st.button(f"{icon} {PAGE_NAMES[page]}", use_container_width=True, 
                    key=f"sidebar_{page}",
                    type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Consultations", len(st.session_state.patient_history))
    
    if st.session_state.patient_history:
        latest = st.session_state.patient_history[-1]
        st.metric("Last Severity", latest.get('severity', 'N/A'))

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🏥 Medical Symptom Interpreter</h1>
    <p>AI-Powered Health Assistant for Symptom Analysis & Medicine Suggestions</p>
</div>
""", unsafe_allow_html=True)

# Top Navigation Arrows
render_navigation_arrows()

st.markdown("<hr>", unsafe_allow_html=True)

# Main Content Area
st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)

# Patient Info Section
st.markdown("""
<div class="patient-card">
    <h3>👤 Patient Information</h3>
    <p>Please provide your details for personalized analysis</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    patient_name = st.text_input("Full Name", value=st.session_state.patient_name, placeholder="Enter your name")
    st.session_state.patient_name = patient_name
with col2:
    age = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.age)
    st.session_state.age = age
with col3:
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    if gender != "Select":
        st.session_state.gender = gender
with col4:
    medical_history = st.text_area("Medical History", value=st.session_state.medical_history, 
                                   placeholder="e.g., Diabetes, Hypertension", height=68)
    st.session_state.medical_history = medical_history

patient_info = {
    'name': st.session_state.patient_name,
    'age': st.session_state.age,
    'gender': st.session_state.gender,
    'history': st.session_state.medical_history
}

st.markdown("<hr>", unsafe_allow_html=True)

# Welcome message
if st.session_state.patient_name:
    st.markdown(f"""
    <div class="welcome-card">
        <h2>Welcome, {st.session_state.patient_name}! 👋</h2>
        <p>Your health assistant is ready to help you</p>
    </div>
    """, unsafe_allow_html=True)

# Page Content
if st.session_state.current_page == "Home":
    st.markdown("## 🏠 Welcome to Medical Symptom Interpreter")
    st.markdown("### Your AI-Powered Health Assistant")
    
    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎤 Start Symptom Checker", use_container_width=True):
            st.session_state.current_page = "Checker"
            st.rerun()
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()
    with col3:
        if st.button("📄 Generate Report", use_container_width=True):
            st.session_state.current_page = "Reports"
            st.rerun()
    
    st.markdown("---")
    
    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="font-size: 3rem;">🎤</h2>
            <h3>Voice Input</h3>
            <p>Speak your symptoms naturally and get instant analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="font-size: 3rem;">🤖</h2>
            <h3>AI Analysis</h3>
            <p>Advanced medical interpretation with high accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="font-size: 3rem;">💊</h2>
            <h3>Medicine Suggestions</h3>
            <p>OTC and prescription medication recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.patient_history:
        st.markdown("---")
        st.markdown("### 📊 Recent Activity")
        recent = pd.DataFrame(st.session_state.patient_history[-5:])
        if len(recent) > 0:
            st.dataframe(recent[['timestamp', 'patient_name', 'severity', 'recommended_action']], use_container_width=True)

elif st.session_state.current_page == "Checker":
    st.markdown("## 🔍 Symptom Checker")
    st.markdown("Describe your symptoms using voice or text for AI analysis")
    
    tab1, tab2 = st.tabs(["🎤 Voice Input", "📝 Manual Input"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📁 Upload Audio")
            audio_file = st.file_uploader("Choose audio file", type=['mp3', 'wav', 'ogg', 'm4a'])
            
            if audio_file:
                with st.spinner("Transcribing..."):
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_file.name.split(".")[-1]}')
                    temp_file.write(audio_file.getvalue())
                    temp_file.close()
                    st.session_state.transcribed_text = transcribe_audio(temp_file.name)
                    os.unlink(temp_file.name)
                    if st.session_state.transcribed_text:
                        st.success("✅ Audio transcribed!")
        
        with col2:
            st.markdown("### 🎙️ Live Recording")
            duration = st.slider("Recording duration (seconds)", 3, 10, 5)
            if st.button("🎙️ Start Recording", use_container_width=True):
                temp_audio = record_audio(duration)
                if temp_audio:
                    with st.spinner("Transcribing..."):
                        st.session_state.transcribed_text = transcribe_audio(temp_audio)
                        os.unlink(temp_audio)
                        if st.session_state.transcribed_text:
                            st.success("✅ Recording transcribed!")
    
    with tab2:
        st.markdown("### 📝 Manual Description")
        manual_symptoms = st.text_area("Describe your symptoms in detail:", height=150, 
                                       placeholder="Example: I have a fever of 101°F, persistent cough, and headache for 2 days...")
        if st.button("📝 Process Symptoms", use_container_width=True):
            if manual_symptoms:
                st.session_state.transcribed_text = manual_symptoms
                st.success("✅ Symptoms recorded!")
    
    if st.session_state.transcribed_text:
        st.markdown(f"""
        <div style="background: white; border-radius: 15px; padding: 15px; margin: 20px 0;">
            <b>📝 Your Symptoms:</b><br>
            {st.session_state.transcribed_text}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing your symptoms..."):
                st.session_state.analysis = analyze_symptoms(st.session_state.transcribed_text, patient_info)
                if st.session_state.analysis:
                    st.session_state.patient_history.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'patient_name': st.session_state.patient_name or 'Guest',
                        'symptoms': st.session_state.transcribed_text[:100],
                        'severity': st.session_state.analysis.get('severity', 'N/A'),
                        'recommended_action': st.session_state.analysis.get('recommended_action', 'N/A'),
                        'health_tips': st.session_state.analysis.get('health_tips', []),
                        'medicine_suggestions': st.session_state.analysis.get('medicine_suggestions', [])
                    })
                    st.success("✅ Analysis complete!")
                    st.balloons()
                    st.rerun()
    
    # Display results
    if st.session_state.analysis:
        analysis = st.session_state.analysis
        
        st.markdown("""
        <div class="results-card">
            <div class="results-header">
                <h2>📊 Analysis Results</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><h3>⚠️ Severity</h3><h2>{analysis.get("severity", "N/A")}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h3>🏥 Action</h3><h2>{analysis.get("recommended_action", "N/A").replace("_", " ").title()}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h3>👨‍⚕️ Specialist</h3><h2>{analysis.get("doctor_specialty_recommendation", "General")[:12]}</h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h3>⏰ Recovery</h3><h2>{analysis.get("estimated_recovery_time", "Varies")}</h2></div>', unsafe_allow_html=True)
        
        if analysis.get('possible_conditions'):
            st.markdown("### 🔍 Possible Conditions")
            conditions_df = pd.DataFrame(analysis['possible_conditions'])
            fig = px.bar(conditions_df, x='condition', y='confidence', 
                        title="Confidence Levels", color='confidence', 
                        color_continuous_scale='oranges', text='confidence')
            fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        if analysis.get('medicine_suggestions'):
            st.markdown("### 💊 Medicine Suggestions")
            st.warning("⚠️ Please consult a doctor before taking any medication")
            for med in analysis.get('medicine_suggestions', []):
                st.markdown(f"• {med}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💡 Health Tips")
            for tip in analysis.get('health_tips', []):
                st.markdown(f"• {tip}")
            st.markdown("### 🏠 Home Remedies")
            for remedy in analysis.get('home_remedies', []):
                st.markdown(f"• {remedy}")
        
        with col2:
            st.markdown("### 🍎 Dietary Suggestions")
            for diet in analysis.get('dietary_suggestions', []):
                st.markdown(f"• {diet}")
            st.markdown("### 🚶 Lifestyle Changes")
            for lifestyle in analysis.get('lifestyle_recommendations', []):
                st.markdown(f"• {lifestyle}")
        
        for precaution in analysis.get('precautions', []):
            st.warning(f"⚠️ {precaution}")
        
        if analysis.get('emergency_warning_signs'):
            st.markdown("### 🚨 Seek Immediate Medical Attention If:")
            for sign in analysis.get('emergency_warning_signs', []):
                st.error(f"🚑 {sign}")
        
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_page == "Analytics":
    st.markdown("## 📊 Health Analytics Dashboard")
    
    # Analytics Explanation - Fixed with proper HTML
    with st.expander("📖 Understanding Your Analytics Dashboard", expanded=False):
        st.markdown("#### 📊 What This Dashboard Shows You")
        
        st.markdown("**📈 Symptom Severity Over Time:**")
        st.markdown("This line chart tracks how the severity of your symptoms has changed across different consultations. An upward trend may indicate worsening condition, while a downward trend suggests improvement. Regular monitoring helps you understand your health patterns.")
        
        st.markdown("**🥧 Severity Distribution:**")
        st.markdown("The pie chart shows the proportion of mild, moderate, and urgent cases in your consultation history. This helps identify if you're experiencing mostly mild symptoms or if there's a pattern of more serious conditions.")
        
        st.markdown("**📊 Recommended Actions Distribution:**")
        st.markdown("This bar chart displays the types of medical recommendations you've received:")
        st.markdown("- **🏠 Self-Care:** Symptoms that can be managed at home with rest and basic remedies")
        st.markdown("- **👨‍⚕️ Doctor Visit:** Cases requiring professional medical consultation")
        st.markdown("- **🚨 Immediate Attention:** Urgent cases needing immediate medical care")
        
        st.markdown("**📋 Recent Consultations:**")
        st.markdown("Your complete history of symptom checks with health tips and medicine suggestions for easy reference.")
        
        st.markdown("**💡 Pro Tip:**")
        st.markdown("Regular monitoring of these patterns can help you:")
        st.markdown("- Identify recurring health issues")
        st.markdown("- Track treatment effectiveness")
        st.markdown("- Make informed decisions about seeking medical care")
        st.markdown("- Share valuable health data with your doctor")
    
    if st.session_state.patient_history:
        history_df = pd.DataFrame(st.session_state.patient_history)
        
        if st.session_state.patient_name:
            patient_data = history_df[history_df['patient_name'] == st.session_state.patient_name]
            st.markdown(f"### 📊 Analytics for {st.session_state.patient_name}")
        else:
            patient_data = history_df
        
        if len(patient_data) > 0:
            # Time series chart
            fig_time = px.line(patient_data, x='timestamp', y='severity', 
                              title="Symptom Severity Over Time",
                              markers=True, color_discrete_sequence=['#ff9800'])
            fig_time.update_layout(height=450)
            st.plotly_chart(fig_time, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                severity_counts = patient_data['severity'].value_counts()
                fig_pie = px.pie(values=severity_counts.values, names=severity_counts.index,
                                title="Severity Distribution", 
                                color_discrete_sequence=['#4caf50', '#ff9800', '#f44336'])
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                action_counts = patient_data['recommended_action'].value_counts()
                action_labels = {'self-care': '🏠 Self-Care', 'doctor': '👨‍⚕️ Doctor Visit', 'immediate': '🚨 Immediate'}
                fig_bar = px.bar(x=[action_labels.get(k, k) for k in action_counts.index], 
                                y=action_counts.values, 
                                title="Recommended Actions Distribution",
                                color=action_counts.values,
                                color_continuous_scale='Oranges')
                fig_bar.update_layout(height=400, xaxis_title="Recommendation Type", yaxis_title="Number of Cases")
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Recent consultations
            st.markdown("### 📋 Recent Consultations with Health Tips")
            for idx, record in patient_data.tail(5).iterrows():
                with st.expander(f"📅 {record['timestamp']} - Severity: {record['severity']}"):
                    st.markdown(f"**🩺 Symptoms:** {record['symptoms']}")
                    st.markdown(f"**⚠️ Severity:** {record['severity']}")
                    st.markdown(f"**🏥 Recommended Action:** {record['recommended_action']}")
                    
                    if record.get('medicine_suggestions'):
                        st.markdown("**💊 Medicine Suggestions:**")
                        for med in record.get('medicine_suggestions', []):
                            st.markdown(f"• {med}")
                    
                    if record.get('health_tips'):
                        st.markdown("**💡 Health Tips:**")
                        for tip in record.get('health_tips', []):
                            st.markdown(f"• {tip}")
            
            # CSV Download
            csv = history_df.to_csv(index=False)
            filename = f"medical_history_{datetime.now().strftime('%Y%m%d')}.csv"
            st.download_button("📥 Download Complete History (CSV)", data=csv, file_name=filename, use_container_width=True)
        else:
            st.info("No data available for this patient. Please analyze symptoms first.")
    else:
        st.info("No data available. Start by analyzing symptoms in the Symptom Checker!")

elif st.session_state.current_page == "Reports":
    st.markdown("## 📄 Medical Reports")
    
    if st.session_state.analysis and st.session_state.transcribed_text:
        pdf_bytes = generate_pdf_report(st.session_state.transcribed_text, st.session_state.analysis)
        report_name = f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name=report_name, type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📋 Report Preview")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background: white; border-radius: 15px; padding: 15px;">
                <b>👤 Patient:</b> {st.session_state.patient_name or 'Guest'}<br>
                <b>🩺 Symptoms:</b> {st.session_state.transcribed_text}<br>
                <b>⚠️ Severity:</b> {st.session_state.analysis.get('severity', 'N/A')}<br>
                <b>🏥 Action:</b> {st.session_state.analysis.get('recommended_action', 'N/A')}<br>
                <b>👨‍⚕️ Specialist:</b> {st.session_state.analysis.get('doctor_specialty_recommendation', 'General Physician')}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: white; border-radius: 15px; padding: 15px;">
                <b>💊 Medicine Suggestions:</b><br>
            """, unsafe_allow_html=True)
            for med in st.session_state.analysis.get('medicine_suggestions', []):
                st.markdown(f"• {med}")
            st.markdown(f"<b>💡 Health Tips:</b><br>", unsafe_allow_html=True)
            for tip in st.session_state.analysis.get('health_tips', [])[:3]:
                st.markdown(f"• {tip}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if len(st.session_state.patient_history) > 1:
            st.markdown("---")
            st.markdown("### 📜 Previous Consultations")
            patient_records = [r for r in st.session_state.patient_history if r.get('patient_name') == st.session_state.patient_name]
            for record in patient_records[-3:]:
                st.markdown(f"""
                <div class="history-card">
                    <b>📅 {record.get('timestamp', 'N/A')}</b><br>
                    <b>🩺 Symptoms:</b> {record.get('symptoms', 'N/A')}<br>
                    <b>⚠️ Severity:</b> {record.get('severity', 'N/A')}<br>
                    <b>💊 Medicine:</b> {record.get('medicine_suggestions', ['N/A'])[0]}<br>
                    <b>💡 Tip:</b> {record.get('health_tips', ['N/A'])[0]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No reports available. Please analyze symptoms first in the Symptom Checker.")

elif st.session_state.current_page == "About":
    st.markdown("## ℹ️ About Medical Symptom Interpreter")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2920/2920344.png", width=180)
    
    with col2:
        st.markdown("### 🏥 AI-Powered Medical Assistant")
        st.markdown("This application uses advanced artificial intelligence to help interpret medical symptoms and provide preliminary guidance including medicine suggestions.")
        
        st.markdown("**✨ Key Features:**")
        st.markdown("- 🎤 **Voice Input** - Speak your symptoms naturally")
        st.markdown("- 🤖 **AI Analysis** - Powered by Groq's Llama 3.3 model")
        st.markdown("- 💊 **Medicine Suggestions** - OTC and prescription recommendations")
        st.markdown("- 📊 **Analytics Dashboard** - Track your health patterns")
        st.markdown("- 📄 **PDF Reports** - Download comprehensive medical reports")
        st.markdown("- 📜 **History Tracking** - All consultations saved for reference")
        st.markdown("- 📥 **CSV Export** - Download your complete medical history")
        
        st.markdown("**⚠️ Important Medical Disclaimer:**")
        st.markdown("This tool is for **informational purposes only** and does not replace professional medical advice. Always consult with a qualified healthcare provider for proper diagnosis, treatment, and before taking any medication.")
        
        st.markdown("**🛠️ Technology Stack:**")
        st.markdown("- **Frontend:** Streamlit")
        st.markdown("- **AI/ML:** Groq API (Whisper + Llama 3.3)")
        st.markdown("- **Visualizations:** Plotly")
        st.markdown("- **Reports:** ReportLab")
        st.markdown("- **Data Processing:** Pandas, NumPy")
        
        st.markdown("**📞 Emergency Contacts:**")
        st.markdown("- 🚑 **Emergency:** 911/112")
        st.markdown("- 🏥 **Poison Control:** 1-800-222-1222")
        st.markdown("- 💊 **Health Helpline:** 1-800-555-1234")

st.markdown("</div>", unsafe_allow_html=True)

# Bottom Navigation Arrows
st.markdown("<hr>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if PAGES.index(st.session_state.current_page) > 0:
        if st.button("◀ Previous", key="nav_prev_bottom", use_container_width=True):
            navigate_page("prev")
with col3:
    if PAGES.index(st.session_state.current_page) < len(PAGES) - 1:
        if st.button("Next ▶", key="nav_next_bottom", use_container_width=True):
            navigate_page("next")

# Footer
st.markdown("""
<div class="footer">
    <p>⚠️ Informational purposes only. Always consult a healthcare professional before taking any medication.</p>
    <p>Made with ❤️ using AI | © 2026 Medical Symptom Interpreter</p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import tempfile
import os
import base64

# --- 1. APP CONFIGURATION & STATE ---
st.set_page_config(
    page_title="TITAN | Elite Voice Coach",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'user_level' not in st.session_state:
    st.session_state.user_level = "Week 1: The Foundation"

# --- 2. WORLD CLASS UI (CSS INJECTION) ---
def local_css():
    st.markdown("""
    <style>
        /* MAIN BACKGROUND & FONT */
        .stApp {
            background-color: #050505;
            color: #E0E0E0;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        
        /* HEADERS */
        h1 {
            color: #FFFFFF;
            font-weight: 800;
            letter-spacing: -1px;
            font-size: 3rem !important;
            text-shadow: 0px 0px 20px rgba(255, 255, 255, 0.1);
        }
        h2, h3 {
            color: #D4AF37; /* Titan Gold */
            font-weight: 600;
        }
        
        /* CARDS (Glassmorphism) */
        div[data-testid="stExpander"], div[data-testid="stContainer"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 1px solid #1F1F1F;
        }
        
        /* BUTTONS */
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #AA8C2C 100%);
            color: #000000;
            font-weight: 800;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0px 5px 15px rgba(212, 175, 55, 0.4);
            color: #000000;
        }
        
        /* RECORDING WIDGET OVERRIDE */
        .stAudio {
            width: 100%;
        }
        
        /* METRICS */
        div[data-testid="metric-container"] {
            background-color: #111;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. CURRICULUM DATA (EVOLVING LESSONS) ---
LESSON_PLAN = {
    "Week 1: The Foundation": {
        "focus": "Pace & The 'T' Sound",
        "intro": "Welcome to Titan. Your first goal is to slow down. Speed signals nervousness. Silence signals power.",
        "drills": {
            "Drill A: The Crisp T": "Target the total market effectively.",
            "Drill B: The Executive Pause": "We need to stop. Think. And execute.",
            "Drill C: The Baseline Audit": "The strategy requires particular attention to detail."
        }
    },
    "Week 2: The Vowels": {
        "focus": "Round Vowels & The Non-Rhotic R",
        "intro": "This week we remove the American 'R'. In British RP, 'Water' is 'Wa-tuh'. 'Car' is 'Cah'.",
        "drills": {
            "Drill A: The Water Trap": "We value the water strategy.",
            "Drill B: The Silent R": "The car is parked in the center of the harbor.",
            "Drill C: The Long O": "The global goal is total control."
        }
    },
    "Week 3: Gravitas": {
        "focus": "Intonation & Downward Inflection",
        "intro": "You are ending sentences like questions (Upspeak). This week, we drill 'The Stairs'. Walk down the stairs with your voice.",
        "drills": {
            "Drill A: The Command": "This is the final decision.",
            "Drill B: The Bad News": "We are not going to meet the deadline.",
            "Drill C: The Pivot": "That is an interesting point, however, we must focus on ROI."
        }
    },
    "Week 4: The Boardroom": {
        "focus": "Flow & Persuasion",
        "intro": "Full simulation. No scripts. Can you hold the floor against an interruption?",
        "drills": {
            "Drill A: The 60-Second Pitch": "[Free Speech] Pitch your current project.",
            "Drill B: The Defense": "[Free Speech] Explain why a project failed.",
            "Drill C: The Vision": "[Free Speech] Where will the company be in 5 years?"
        }
    }
}

# --- 4. BACKEND FUNCTIONS ---

def get_audio_html(file_path):
    """Hidden audio player that auto-plays for that 'AI Voice' feel"""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f"""
        <audio autoplay="true" style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """

def generate_voice(text, accent_tld='co.uk'):
    """Generates audio bytes for TTS"""
    try:
        tts = gTTS(text, lang='en', tld=accent_tld)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

def analyze_performance(api_key, audio_bytes, level, drill_name, target_text):
    """The Brain: Uses Gemini 2.5 Flash"""
    if not api_key:
        return "⚠️ MISSING API KEY", None

    genai.configure(api_key=api_key)
    
    # Context-Aware Prompt based on Current Level
    system_prompt = f"""
    You are TITAN, a ruthless but sophisticated British Accent Coach.
    Current Level: {level}
    Current Drill: {drill_name}
    Target Text: "{target_text}"
    
    YOUR TASK:
    1. Listen to the user's audio.
    2. Compare it to the British Received Pronunciation (RP) standard.
    3. Check for Indian English habits (Retroflex T, Fast Pace, Rhotic R).
    
    OUTPUT FORMAT (Markdown):
    ## SCORE: [0-100]
    
    ### 🛑 THE ERROR
    [Identify the specific syllable they messed up. e.g., "You rolled the R in 'Market'."]
    
    ### 🎯 THE FIX
    [One physical instruction. e.g., "Keep your tongue flat. Don't curl it back."]
    
    ### 🗣️ COACH'S NOTE
    [A 1-sentence executive tip on gravitas.]
    """
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        with st.spinner("🎧 Titan is analyzing your physics..."):
            response = model.generate_content([
                {'mime_type': 'audio/wav', 'data': audio_bytes}, 
                system_prompt
            ])
            return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 5. MAIN APPLICATION ---

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6681/6681204.png", width=80)
    st.markdown("## TITAN **PRO**")
    st.markdown("### *Executive Communication Suite*")
    
    api_key = st.text_input("🔑 API Access Key", type="password")
    
    st.markdown("---")
    st.markdown("### 📅 Curriculum")
    selected_level = st.radio(
        "Select Module:",
        list(LESSON_PLAN.keys()),
        index=0
    )
    
    st.markdown("---")
    st.caption("v3.0.1 | Powered by Gemini 2.5")

# Main Content
current_lesson = LESSON_PLAN[selected_level]

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.title(selected_level)
    st.markdown(f"*{current_lesson['focus']}*")
    st.write(current_lesson['intro'])

with col2:
    # This acts as the "Coach Intro" voice button
    if st.button("🔊 INTRO"):
        intro_audio = generate_voice(current_lesson['intro'])
        st.audio(intro_audio)

st.markdown("---")

# Drills Section
st.markdown("### 🏋️ TRAINING DRILLS")

# Create tabs for the 3 drills
drill_names = list(current_lesson['drills'].keys())
tab1, tab2, tab3 = st.tabs(drill_names)

def render_drill_tab(tab, drill_key):
    with tab:
        target_text = current_lesson['drills'][drill_key]
        
        # UI Container for the Drill
        with st.container():
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.markdown(f"### *\"{target_text}\"*")
                st.info("Listen to the reference. Then record. Aim for < 90% Match.")
            
            with c2:
                if st.button(f"👂 Reference Audio ({drill_key})"):
                    ref = generate_voice(target_text)
                    st.audio(ref)
            
            st.markdown("---")
            
            # Recorder
            audio_bytes = audio_recorder(
                text="Tap to Record",
                recording_color="#D4AF37",
                neutral_color="#333333",
                icon_size="3x",
            )
            
            if audio_bytes and api_key:
                st.success("Audio Captured. Analyzing...")
                feedback = analyze_performance(api_key, audio_bytes, selected_level, drill_key, target_text)
                
                # Display Results
                st.markdown(feedback)
                
                # OPTIONAL: Make the AI speak the feedback
                # Extract text for TTS (Simple cleanup)
                if "**SCORE:**" in feedback or "## SCORE" in feedback:
                    clean_feedback = feedback.replace("#", "").replace("*", "")[:200] # Speak first 200 chars
                    feedback_audio = generate_voice(f"Here is your feedback. {clean_feedback}")
                    st.audio(feedback_audio)

# Render the tabs
render_drill_tab(tab1, drill_names[0])
render_drill_tab(tab2, drill_names[1])
render_drill_tab(tab3, drill_names[2])

# Footer
st.markdown("---")
st.markdown("<center style='color: #444;'>TITAN EXECUTIVE SYSTEMS © 2025</center>", unsafe_allow_html=True)

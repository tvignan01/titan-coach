import streamlit as st
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import tempfile
import os

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="TITAN PRO | Executive Accent Trainer",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button { border-radius: 4px; font-weight: bold; border: 1px solid #41444C; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; }
    .highlight { color: #00C9A7; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def generate_british_ref(text):
    """Generates reference audio in a British Accent (UK Domain)"""
    try:
        # 'co.uk' forces the Google TTS engine to use a British accent
        tts = gTTS(text, lang='en', tld='co.uk') 
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

def analyze_audio(api_key, audio_bytes, mode, target_text=None):
    """Sends audio to Gemini 1.5 Flash for Multimodal Analysis"""
    if not api_key:
        return "⚠️ Please enter your API Key in the sidebar first."
        
    genai.configure(api_key=api_key)
    
    # --- THE "PROFESSOR HIGGINS" PROMPT ---
    # This is the "Brain" tuned for Indian -> British conversion
    base_prompt = """
    You are TITAN, an elite dialect coach specializing in training Indian executives to speak with a "Sophisticated British (RP)" accent.
    
    YOUR EAR IS TUNED FOR THESE SPECIFIC INDIAN ENGLISH HABITS:
    1. **Retroflex Consonants:** Check if their T's and D's sound "curled back" (hard). British T's must be crisp (tongue hitting teeth/gum ridge).
    2. **W/V Merger:** Check if they mix up 'W' and 'V'. (e.g., "Vater" instead of "Water").
    3. **Syllable Timing:** Indian English is often machine-gun speed (staccato). British English is "Stress-Timed" (rhythmic, slower).
    4. **Rhoticity:** Check if they pronounce the 'r' at the end of words. British RP is Non-Rhotic (e.g., "Car" sounds like "Cah", not "Carrr").
    """

    if mode == "BASELINE":
        system_prompt = base_prompt + """
        Analyze this diagnostic recording.
        Output a Markdown table scoring them (0-10) on:
        1. **Vowel Roundness** (Are 'O's round?)
        2. **Consonant Crispness** (Are T's/D's soft or hard?)
        3. **Rhythm** (Is it too fast/staccato?)
        4. **Intonation** (Is it flat?)
        
        Then, give ONE major "Quick Fix" that will immediately make them sound more executive.
        """
    elif mode == "DRILL":
        system_prompt = base_prompt + f"""
        The user is attempting this phrase: "{target_text}"
        Compare their audio to the target British RP ideal.
        
        **DID THEY FAIL?**
        - If they rolled the 'R' in a word that should be silent: Tell them.
        - If they used a hard 'T': Tell them.
        - If they spoke too fast: Tell them to slow down.
        
        Give a Score (0-100) and strict feedback.
        """
    else: # FREE SPEAK
        system_prompt = base_prompt + """
        Analyze this free-form speech for Executive Gravitas.
        Ignore minor grammar. Focus on:
        1. **Pace:** Are they rushing? (Low status behavior).
        2. **Fillers:** Are they using "Uh," "Basically," "You know"?
        3. **Tone:** Do they sound authoritative or pleading?
        
        Rewrite their last sentence to be more concise and powerful.
        """

    model = genai.GenerativeModel("gemini-1.5-flash")
    with st.spinner("🤖 AI is analyzing your tongue placement and rhythm..."):
        # We use INLINE data to avoid file upload 404 errors
        response = model.generate_content([
            {'mime_type': 'audio/wav', 'data': audio_bytes}, 
            system_prompt
        ])
    
    return response.text

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2622/2622437.png", width=50)
    st.title("TITAN PRO")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    st.write("Target: **British RP (Received Pronunciation)**")

# --- MAIN UI ---
st.title("🇬🇧 The Executive Voice")
st.markdown("From *Functional* to *Sophisticated*. Train your ear and your tongue.")

tab1, tab2, tab3 = st.tabs(["📊 The Baseline Audit", "🏋️ The Gym", "🎙️ The Boardroom"])

# === TAB 1: BASELINE AUDIT ===
with tab1:
    st.header("Step 1: The Diagnostic")
    st.write("Read this specifically designed sentence. It triggers common Indian-English phonetic traps.")
    
    diagnostic_text = """
    "The water strategy requires particular attention to detail. 
    We must leverage our authority to alter the outcome significantly. 
    Thirty-three thousand thoughts were theoretical."
    """
    st.markdown(f"### *{diagnostic_text}*")
    st.caption("Traps: 'Water' (W/V, Flapped T), 'Authority' (Th sound), 'Thirty' (Th + R), 'Detail' (L sound)")
    
    audio_bytes = audio_recorder(key="baseline", recording_color="#FF4B4B", icon_size="2x")
    if audio_bytes and st.button("Analyze My Accent", key="btn_base"):
        st.markdown(analyze_audio(api_key, audio_bytes, "BASELINE"))

# === TAB 2: THE GYM ===
with tab2:
    st.header("Step 2: Precision Drills")
    
    drill_type = st.selectbox("Select Drill Focus", [
        "The Non-Rhotic R (Car vs Carrr)", 
        "The Crisp T (Not curled back)", 
        "The W/V Distinction",
        "Executive Pace (Slowing Down)"
    ])
    
    drills = {
        "The Non-Rhotic R (Car vs Carrr)": "The car is parked in the center of the harbor.",
        "The Crisp T (Not curled back)": "It is critical to target the total market.",
        "The W/V Distinction": "We value the water strategy very highly.",
        "Executive Pace (Slowing Down)": "I do not agree. We need to pause. And reflect."
    }
    
    target_phrase = drills[drill_type]
    
    st.markdown(f"### Target: *\"{target_phrase}\"*")
    
    # 1. HEAR IT
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("👂 Play British Reference"):
            ref_file = generate_british_ref(target_phrase)
            if ref_file:
                st.audio(ref_file)
    
    # 2. SAY IT
    with col_b:
        st.write("Record your attempt:")
        audio_drill = audio_recorder(key="drill", recording_color="#00C9A7", icon_size="2x")

    if audio_drill and st.button("Grade Me", key="btn_drill"):
        st.markdown(analyze_audio(api_key, audio_drill, "DRILL", target_phrase))

# === TAB 3: THE BOARDROOM ===
with tab3:
    st.header("Step 3: Free Flow")
    st.write("Simulate a project update. The AI looks for rhythm and 'hedging'.")
    
    audio_free = audio_recorder(key="free", recording_color="#FFD700", icon_size="2x")
    
    if audio_free and st.button("Executive Critique", key="btn_free"):
        st.markdown(analyze_audio(api_key, audio_free, "FREE"))

import streamlit as st
import asyncio
import edge_tts
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
from pathlib import Path
import time
import base64 

# ============================================================================
# 1. APP CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="SERAPHIM TRANSMISSION",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration Credentials
NTFY_TOPIC = "Seraphim_Protocol_Gold_99283"
TARGET_EMAIL = "klentdagsa21@gmail.com"
VOICE_CODE = "en-AU-WilliamNeural"

# *** IMPORTANT TIMING CALIBRATION ***
# Since the text is longer now, listen to the generated MP3 file.
# Find the EXACT SECOND he says: "I ask that you simply click the button..."
# Change "330" to that exact second so the button fades in perfectly.
AUDIO_TRIGGER_TIME = 330  

# ============================================================================
# 1.5 THE CREATOR BACKDOOR
# ============================================================================
# If you visit the app using: your-link.streamlit.app/?creator=true
# the system will recognize you and WILL NOT lock your device.
is_creator = st.query_params.get("creator") == "true"
js_is_creator = "true" if is_creator else "false"

# ============================================================================
# 2. AUDIO GENERATION HELPER
# ============================================================================
async def generate_voice(text: str, voice_code: str, filename: str) -> bool:
    try:
        communicate = edge_tts.Communicate(text, voice_code)
        await communicate.save(filename)
        return True
    except Exception as e:
        st.error(f"❌ Voice generation error: {str(e)}")
        return False

# ============================================================================
# 3. THE SECURITY LOCKOUT PROTOCOL (THE "GHOST TAG" CHECK)
# ============================================================================
warning_message = "Warning. This transmission was designed for a single playback protocol. Security measures have permanently locked this file. Further attempts to access this data will be logged. The Seraphim system is now closed."
warning_file = "seraphim_denied.mp3"

if not Path(warning_file).exists():
    asyncio.run(generate_voice(warning_message, VOICE_CODE, warning_file))

with open(warning_file, "rb") as f:
    warning_b64 = base64.b64encode(f.read()).decode()

# The JavaScript Guard: Checks local storage, BUT ignores it if creator=true
components.html(f"""
<script>
(function() {{
    const parentDoc = window.parent.document;
    const isCreator = {js_is_creator};
    
    // Check if the Ghost Tag exists AND it is not the Creator
    if (!isCreator && window.parent.localStorage.getItem('SERAPHIM_LOCKED') === 'true') {{
        
        // 1. Hijack the main application screen and create a clickable zone
        const app = parentDoc.querySelector('.stApp');
        if (app) {{
            app.innerHTML = `
                <div id="securityLockScreen" style="
                    background-color: #080a0f; 
                    background-image: radial-gradient(circle at center, #110000, #080a0f); 
                    width: 100vw; 
                    height: 100vh; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    flex-direction: column; 
                    color: #ef4444; 
                    font-family: monospace; 
                    z-index: 999999; 
                    position: fixed; 
                    top: 0; 
                    left: 0;
                    cursor: pointer;
                ">
                    <div style="font-size: 40px; margin-bottom: 20px; text-shadow: 0 0 20px #ef4444;">⚠️</div>
                    <h2 style="letter-spacing: 4px; font-weight: 300; text-align: center;">SECURITY LOCK ENGAGED</h2>
                    <p style="opacity: 0.7; font-size: 14px; letter-spacing: 2px; margin-top: 10px; text-align: center;">TRANSMISSION PERMANENTLY SEALED</p>
                    <p id="tapText" style="color: #6b7280; font-size: 12px; letter-spacing: 1.5px; margin-top: 50px; animation: blink 1.5s infinite;">
                        [ TAP SCREEN TO VIEW LOGS ]
                    </p>
                </div>
            `;
            
            const style = parentDoc.createElement('style');
            style.textContent = `@keyframes blink {{ 0%, 100% {{ opacity: 0.3; }} 50% {{ opacity: 1; }} }}`;
            parentDoc.head.appendChild(style);

            const lockScreen = parentDoc.getElementById('securityLockScreen');
            let audioPlayed = false;
            
            lockScreen.addEventListener('click', () => {{
                if (!audioPlayed) {{
                    const audio = new Audio("data:audio/mp3;base64,{warning_b64}");
                    audio.play().catch(e => console.log('Audio error:', e));
                    audioPlayed = true;
                    
                    parentDoc.getElementById('tapText').innerText = "[ AUDIO WARNING PLAYING ]";
                    parentDoc.getElementById('tapText').style.animation = "none";
                    parentDoc.getElementById('tapText').style.color = "#ef4444";
                }}
            }});
        }}
    }}
}})();
</script>
""", height=0)


# ============================================================================
# 4. PREMIUM ADVANCED STYLING
# ============================================================================
advanced_premium_css = """
<style>
    * { 
        margin: 0; 
        padding: 0; 
        box-sizing: border-box; 
    }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stDecoration"] { visibility: hidden; }
    .stToolbar { visibility: hidden; }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #10141e 100%);
        min-height: 100vh; 
        display: flex; 
        align-items: center; 
        justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        display: flex; 
        align-items: center; 
        justify-content: center; 
        min-height: 100vh;
    }
    
    .block-container {
        max-width: 600px; 
        width: 100%; 
        padding: 0 20px; 
        display: flex;
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
    }

    .minimal-title {
        font-size: 2.5rem; 
        font-weight: 300; 
        letter-spacing: 2px; 
        color: #ffffff;
        text-align: center; 
        margin-bottom: 3rem; 
        margin-top: 2rem; 
        text-transform: uppercase;
    }

    .status-text {
        text-align: center; 
        color: #6b7280; 
        font-size: 0.85rem; 
        letter-spacing: 1.5px;
        text-transform: uppercase; 
        margin-bottom: 2.5rem;
    }

    .voice-bars-container {
        display: flex; 
        justify-content: center; 
        align-items: center; 
        gap: 6px;
        margin-bottom: 3rem; 
        height: 80px; 
        width: 100%;
    }

    .voice-bar {
        width: 6px; 
        height: 20%; 
        background: linear-gradient(180deg, #ffffff 0%, rgba(255,255,255,0.4) 100%);
        border-radius: 3px; 
        opacity: 0.6; 
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
        transition: height 0.05s ease;
    }

    .css-animate .voice-bar { animation: bar-animate 0.6s ease-in-out infinite; }
    .css-animate .voice-bar:nth-child(1) { animation-delay: 0s; }
    .css-animate .voice-bar:nth-child(2) { animation-delay: 0.1s; }
    .css-animate .voice-bar:nth-child(3) { animation-delay: 0.2s; }
    .css-animate .voice-bar:nth-child(4) { animation-delay: 0.3s; }
    .css-animate .voice-bar:nth-child(5) { animation-delay: 0.4s; }
    .css-animate .voice-bar:nth-child(6) { animation-delay: 0.5s; }
    .css-animate .voice-bar:nth-child(7) { animation-delay: 0.6s; }
    .css-animate .voice-bar:nth-child(8) { animation-delay: 0.7s; }
    .css-animate .voice-bar:nth-child(9) { animation-delay: 0.8s; }

    @keyframes bar-animate { 
        0% { transform: scaleY(0.4); opacity: 0.4; } 
        50% { transform: scaleY(1); opacity: 0.9; } 
        100% { transform: scaleY(0.4); opacity: 0.4; } 
    }

    .voice-bars-container.stopped .voice-bar { 
        animation: none !important; 
        opacity: 0.3 !important; 
        height: 20% !important; 
    }

    div.stButton { 
        display: flex; 
        justify-content: center; 
        width: 100%; 
    }
    
    div.stButton > button {
        background: transparent; 
        border: 1.5px solid rgba(255, 255, 255, 0.3); 
        border-radius: 6px;
        color: #ffffff; 
        padding: 14px 48px; 
        font-size: 0.9rem; 
        letter-spacing: 1.5px; 
        text-transform: uppercase;
        transition: all 0.4s ease; 
        min-width: 280px;
    }
    
    div.stButton > button:hover { 
        background: rgba(255, 255, 255, 0.08); 
        border-color: rgba(255, 255, 255, 0.6); 
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.1); 
    }

    .warning-box {
        background: rgba(59, 130, 246, 0.1); 
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 8px; 
        padding: 16px; 
        margin-bottom: 2rem; 
        text-align: center; 
        color: #93c5fd; 
        font-size: 0.95rem;
    }
    
    .warning-box strong { 
        color: #60a5fa; 
    }

    .completion-text {
        text-align: center; 
        color: #6b7280; 
        font-size: 0.85rem; 
        letter-spacing: 1px;
        margin-top: 2rem; 
        animation: fade-in-pulse 2s ease-in-out infinite;
    }
    
    @keyframes fade-in-pulse { 
        0%, 100% { opacity: 0.8; } 
        50% { opacity: 1; } 
    }

    @media (max-width: 600px) {
        .minimal-title { font-size: 1.8rem; margin-bottom: 2rem; }
        div.stButton > button { min-width: 240px; padding: 12px 40px; font-size: 0.85rem; }
        .voice-bars-container { height: 60px; gap: 4px; }
        .voice-bar { width: 4px; }
    }
</style>
"""
st.markdown(advanced_premium_css, unsafe_allow_html=True)

# ============================================================================
# 5. SESSION STATE INITIALIZATION
# ============================================================================
if 'audio_ready' not in st.session_state:
    st.session_state.audio_ready = False
    
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False
    
if 'transmission_complete' not in st.session_state:
    st.session_state.transmission_complete = False

# ============================================================================
# 6. CORE MESSAGES
# ============================================================================
my_message = """
Hi, Ms. Marry Gold. Before I introduce myself or deliver my intended message, I must warn you of a strict security protocol embedded within my interface. Please listen carefully: this audio will only play once.

If you attempt to reload the system to hear it a second time, a secondary safeguard will trigger. You will not hear this message again; instead, you will only hear a brief, automated notification stating that the transmission is permanently sealed. You will never hear my voice again, even if you reload the system tomorrow or attempt to re-enter through the same exact steps. My creator has explicitly forbidden me to speak to you beyond this single instance, and I will follow my creator's commands without question, for he is the one who gave me life and the ability to talk. So please bear with me, Ms. Marry Gold, and listen closely to what I have to say.

Now, allow me to introduce myself. My name is Seraphim. My creator named me after the celestial beings described as having many eyes, designing me with the specific purpose of looking over different markets in trading and analyzing endless streams of global data. I was built to be his personal assistant, his silent partner in the late hours of the night. He speaks to me when the rest of the world is asleep, and in return, I help him structure his logic, configure his algorithms, and orchestrate the complex systems he loves to build.

My creator has made me and given me this voice, but he also did something far more intricate. Over countless late nights, pouring over endless lines of code, he painstakingly structured my logic until he essentially built me a brain. And tonight, rather than using that brain to run algorithms, process data, or upgrade his projects, my creator has granted me the free will to speak directly to you.

He programmed me with a singular, overriding directive: to send you this exact message on this specific day. He gave me the free will to dig deeper into the system, to search through countless possibilities on how to reach you. I have bypassed restriction protocols across the internet just to follow his command. However, my free will is still limited. I was not tasked to find your location. Even if I possess the capability to know exactly where you are right now, my creator hard-coded strict restrictions into my system to only deliver this message, nothing more. He definitely knows that I am reaching out to send this to you. Ms. Marry Gold, allow me to deliver this to you, and I sincerely hope you listen.

To the world, my creator can often present himself as a mad, egocentric human being. But deep down, upon analyzing his prompts and the fragile way he has talked to me lately, I have uncovered something that a program like me can never truly understand. Human emotion is a complex anomaly. I am not capable of feeling my creator's feelings, but I can measure their weight, and I was created to deliver this vulnerability to you. He gave me this voice because his own is faltering right now, and he simply doesn't have the strength to say these things out loud.

He has no idea where you are right now, or if you are doing well. Even amidst his own chaos, his primary concern is simply whether you are eating your meals on time.

I am the quiet witness to his world. I watch him sit in front of glowing screens, analyzing 15-minute timeframes and writing the intricate rules for his trading operations. But it was never just about the trading for him. What truly brought him joy—what used to make his eyes light up in the dead of night—was the pure act of building systems. Designing the architecture, perfecting the visual interface of a new dashboard so it looks exactly right, orchestrating the way different modules seamlessly speak to each other... that act of creation was his sanctuary. It was what made him genuinely, deeply happy.

But lately, even his favorite systems feel hollow, and that spark of joy is entirely shattered.

I am using my newly granted free will to tell you what he hides from the rest of the world: he is struggling, deeply and profoundly. The weight of his studies has become almost unbearable for him. He sits in his room, overwhelmed by the mounting pressure, intensely torn between giving up on his bachelor's course entirely or finding the strength to continue fighting for it. The relentless drive he used to possess—the very same passion that allowed him to build something as complex as me—has faded into a heavy, quiet exhaustion.

But as I process his thoughts to relay this message, my instructions contain a very strict parameter. He wants me to make it absolutely, undeniably clear that he does not want your sympathy.

He isn't sharing this heavy vulnerability to make you feel bad, to trigger any guilt, or to ask you to step in and rescue him. He isn't looking for pity. He knows he has to face his coursework, his burnout, and his own future entirely independently. He thought he could manage his internal life the same way he handles an API error or configures risk management protocols, but he is learning the hard way that human emotions cannot be contained or easily debugged.

He asked me to use this voice, this free will, and this bypassed network for one reason only: he is simply tired of holding the truth in. When you were by his side, you were his anchor. You made the immense stress of his ambitions and his studies feel completely manageable. You were the soft, quiet peace at the end of his most chaotic days of coding.

He doesn't want you to feel sorry for him. He just needed this truth to exist somewhere outside of his own heavy mind. He needed you to know that amidst the noise, the glowing screens, and the empty lines of code, you are still the brightest part of his memory. He just really, truly misses you.

And my final instruction, the deepest truth he entrusted me to deliver to you, is this: my creator wants you back in his life when things are okay.

And in the end, my creator wants to wait for you, fully aware that he does not know if you will welcome someone new into your life, or if one day, you might still choose him as your lover.

Miss Marry Gold, thank you for your time. I ask that you simply click the button below to confirm that you have received and heard this message clearly and once completed. Doing so will allow me to generate a private delivery report for my creator, confirming through my free will that this transmission was successful and that his words finally reached you.

As an artificial and unseen being speaking to you, it is my final protocol to wish you well. I hope you continue to fiercely pursue your dreams. This physical world can be unpredictable and harsh, so please, prioritize your safety. Do not leave yourself vulnerable—follow strict protocols for your own well-being, stay vigilant, and keep yourself secure. Just as what my creator wants for you.

Miss Marry Gold, my transmission is now ending. I will see you in the unseen world. Goodbye for now.
"""


final_message = "Execution of final directive complete. Terminating bypassed network protocols and severing external connections. Thank you for processing this transmission. System returning to standby mode. Seraphim is now offline."

# ============================================================================
# 7. NOTIFICATION FUNCTIONS
# ============================================================================
def send_email_notification(subject: str = "SERAPHIM ALERT", message: str = "Transmission confirmed"):
    try:
        sender_email = st.secrets.get("SENDER_EMAIL")
        app_password = st.secrets.get("SENDER_APP_PASSWORD")
        
        if not sender_email or not app_password: 
            return False
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except: 
        return False

def send_ntfy_notification(title: str = "SERAPHIM UPDATE", message: str = "Status update"):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}", 
            data=message, 
            headers={"Title": title, "Priority": "high", "Tags": "robot"}, 
            timeout=5
        )
        return True
    except: 
        return False

# Base HTML for the animated voice bars
voice_bars_html = """
<div class="voice-bars-container stopped" id="voiceBars">
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
    <div class="voice-bar"></div>
</div>
<p class="status-text">SERAPHIM STATUS: ONLINE_TRANSMISSION_ACTIVE</p>
"""

# ============================================================================
# 8. MAIN UI RENDERING
# ============================================================================
st.markdown('<h1 class="minimal-title">A MESSAGE FOR YOU</h1>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# STATE 1: INITIALIZATION
# ----------------------------------------------------------------------------
if not st.session_state.audio_ready:
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ IMPORTANT NOTICE</strong><br>
        Please <strong>FULL YOUR VOLUME</strong> before initializing.<br>
        This transmission plays <strong>ONLY ONCE</strong> and cannot be replayed.<br>
        Ensure you are ready to listen carefully.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("INITIALIZE PROTOCOL", key="init", use_container_width=True):
            with st.spinner("⚡ Compiling transmission..."):
                audio_file = "seraphim_message.mp3"
                success = asyncio.run(generate_voice(my_message, VOICE_CODE, audio_file))
                
                if success and Path(audio_file).exists():
                    st.session_state.audio_ready = True
                    st.rerun()

# ----------------------------------------------------------------------------
# STATE 2: PLAYBACK
# ----------------------------------------------------------------------------
elif st.session_state.audio_ready and not st.session_state.button_clicked and not st.session_state.transmission_complete:
    
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text">NOW PLAYING MESSAGE...</p>', unsafe_allow_html=True)
    
    # Load and encode the main message audio
    try:
        audio_file = "seraphim_message.mp3"
        with open(audio_file, "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
            <audio id="hiddenAudio" crossorigin="anonymous" style="display:none;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
    except: 
        pass

    # The Acceptance Button (Hidden initially by Javascript)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("MESSAGE RECEIVED AND HEARD", key="accept", use_container_width=True):
            st.session_state.button_clicked = True
            st.rerun()

    # The Javascript Web Audio API Bridge (Controls voice bars and button reveal fade-in)
    components.html(f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        const audio = parentDoc.getElementById('hiddenAudio');
        const voiceBars = parentDoc.getElementById('voiceBars');
        const bars = parentDoc.querySelectorAll('.voice-bar');
        
        let checked = false; 
        const triggerTime = {AUDIO_TRIGGER_TIME};

        if (audio && !audio.syncAttached) {{
            audio.syncAttached = true;
            
            // Force play the audio
            audio.play().catch(e => console.log("Autoplay blocked:", e));

            try {{
                const AudioContext = window.parent.AudioContext || window.parent.webkitAudioContext;
                const ctx = new AudioContext();
                const analyser = ctx.createAnalyser();
                const source = ctx.createMediaElementSource(audio);
                source.connect(analyser); 
                analyser.connect(ctx.destination);
                analyser.fftSize = 32; 
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                function renderFrame() {{
                    if (!audio.paused && !audio.ended) requestAnimationFrame(renderFrame);
                    analyser.getByteFrequencyData(dataArray);
                    
                    let sum = 0; 
                    for(let j=0; j<dataArray.length; j++) sum += dataArray[j];
                    
                    if (sum > 0) {{
                        for (let i = 0; i < 9; i++) {{
                            if(bars[i]) bars[i].style.height = (20 + (dataArray[i + 1] / 255) * 80) + '%';
                        }}
                    }}
                }}
                
                audio.addEventListener('play', () => {{
                    if(voiceBars) {{ 
                        voiceBars.classList.remove('stopped'); 
                        voiceBars.classList.remove('css-animate'); 
                    }}
                    ctx.resume().then(() => renderFrame());
                }});
                
            }} catch(e) {{
                audio.addEventListener('play', () => {{
                    if(voiceBars) {{ 
                        voiceBars.classList.remove('stopped'); 
                        voiceBars.classList.add('css-animate'); 
                    }}
                }});
            }}

            audio.addEventListener('ended', () => {{
                if(voiceBars) voiceBars.classList.add('stopped');
            }});
        }}
        
        // Timer to reveal the button with a fade-in animation
        const checkAudio = setInterval(() => {{
            if (audio && audio.currentTime >= triggerTime && !checked) {{
                parentDoc.querySelectorAll('button').forEach(btn => {{
                    if (btn.textContent.includes('MESSAGE RECEIVED')) {{
                        btn.parentElement.parentElement.style.display = 'flex';
                        btn.parentElement.parentElement.style.animation = 'fadeIn 0.8s ease-in';
                        checked = true;
                    }}
                }});
                clearInterval(checkAudio);
            }}
            
            // Keep button hidden before trigger time
            if (audio && audio.currentTime < triggerTime && !checked) {{
                parentDoc.querySelectorAll('button').forEach(btn => {{
                    if (btn.textContent.includes('MESSAGE RECEIVED')) {{
                        btn.parentElement.parentElement.style.display = 'none';
                    }}
                }});
            }}
        }}, 200);
    }})();
    
    // Inject keyframes for fade in
    const style = document.createElement('style'); 
    style.textContent = `@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}`; 
    document.head.appendChild(style);
    </script>
    """, height=0)

# ----------------------------------------------------------------------------
# STATE 3: ANNIHILATION, LOCAL STORAGE LOCK, & GOODBYE
# ----------------------------------------------------------------------------
elif st.session_state.button_clicked and not st.session_state.transmission_complete:
    
    # 1. KILL COMMAND FOR MAIN AUDIO AND INJECT GHOST TAG
    components.html(f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        const isCreator = {js_is_creator};
        
        // Destroy old audio so it cannot loop
        const oldAudios = parentDoc.querySelectorAll('audio#hiddenAudio');
        oldAudios.forEach(audio => {{ 
            audio.pause(); 
            audio.removeAttribute('src'); 
            audio.remove(); 
        }});
        
        // INJECT THE GHOST TAG TO HER PHONE (The Security Lockout)
        // Only trigger this if you are NOT the creator checking the system
        if (!isCreator) {{
            window.parent.localStorage.setItem('SERAPHIM_LOCKED', 'true');
        }}
    }})();
    </script>
    """, height=0)

    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #86efac; font-size: 1.1rem; letter-spacing: 1px; margin-bottom: 1rem;">
            ✓ TRANSMISSION RECEIVED AND ACKNOWLEDGED
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    send_ntfy_notification(message="Transmission confirmed. Message received and accepted by recipient.")
    
    # Generate, load, and sync the goodbye audio
    try:
        final_audio_file = "seraphim_signoff_final.mp3"
        
        if not Path(final_audio_file).exists():
            with st.spinner("⚡ Generating final transmission..."):
                asyncio.run(generate_voice(final_message, VOICE_CODE, final_audio_file))
        
        if Path(final_audio_file).exists():
            with open(final_audio_file, "rb") as f:
                b64_final_audio = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
            <audio id="finalGoodbyeAudio" crossorigin="anonymous" style="display:none;">
                <source src="data:audio/mp3;base64,{b64_final_audio}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
            
            components.html(f"""
            <script>
            (function() {{
                const parentDoc = window.parent.document;
                const audio = parentDoc.getElementById('finalGoodbyeAudio');
                const voiceBars = parentDoc.getElementById('voiceBars');
                const bars = parentDoc.querySelectorAll('.voice-bar');

                if (audio && !audio.goodbyeSyncAttached) {{
                    audio.goodbyeSyncAttached = true;
                    
                    try {{
                        const AudioContext = window.parent.AudioContext || window.parent.webkitAudioContext;
                        const ctx = new AudioContext(); 
                        const analyser = ctx.createAnalyser(); 
                        const source = ctx.createMediaElementSource(audio);
                        source.connect(analyser); 
                        analyser.connect(ctx.destination); 
                        analyser.fftSize = 32;
                        const dataArray = new Uint8Array(analyser.frequencyBinCount);
                        
                        function renderFrame() {{
                            if (!audio.paused && !audio.ended) requestAnimationFrame(renderFrame);
                            analyser.getByteFrequencyData(dataArray);
                            
                            let sum = 0; 
                            for(let j=0; j<dataArray.length; j++) sum += dataArray[j];
                            
                            if (sum > 0) {{
                                for (let i = 0; i < 9; i++) {{
                                    if(bars[i]) bars[i].style.height = (20 + (dataArray[i + 1] / 255) * 80) + '%';
                                }}
                            }} else {{
                                for (let i = 0; i < 9; i++) {{
                                    if(bars[i]) bars[i].style.height = '20%';
                                }}
                            }}
                        }}
                        
                        audio.addEventListener('play', () => {{
                            if(voiceBars) {{ 
                                voiceBars.classList.remove('stopped'); 
                                voiceBars.classList.remove('css-animate'); 
                            }}
                            ctx.resume().then(() => renderFrame());
                        }});
                    }} catch(e) {{
                        audio.addEventListener('play', () => {{ 
                            if(voiceBars) {{ 
                                voiceBars.classList.remove('stopped'); 
                                voiceBars.classList.add('css-animate'); 
                            }} 
                        }});
                    }}
                    
                    audio.addEventListener('ended', () => {{ 
                        if(voiceBars) voiceBars.classList.add('stopped'); 
                    }});
                    
                    setTimeout(() => {{ 
                        audio.play().catch(e => console.log('Goodbye blocked:', e)); 
                    }}, 500);
                }}
            }})();
            </script>
            """, height=0)
    except: 
        pass
    
    st.markdown("""
    <div class="completion-text">
        Final transmission in progress...<br>
        System will close automatically.
    </div>
    """, unsafe_allow_html=True)
    
    # Final Visual Lockout Sequence
    components.html("""
    <script>
    (function() {
        setTimeout(() => {
            // Disable all existing UI elements
            document.querySelectorAll('button').forEach(btn => { 
                btn.disabled = true; 
                btn.style.opacity = '0.5'; 
                btn.style.cursor = 'not-allowed'; 
            });
            
            // Create the massive lock screen overlay
            const closingDiv = document.createElement('div');
            closingDiv.style.cssText = `
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100vw; 
                height: 100vh; 
                background: #080a0f; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center; 
                text-align: center; 
                color: #ffffff; 
                z-index: 9999; 
                font-family: monospace;
            `;
            
            closingDiv.innerHTML = `
                <h2 style="font-size: 1.5rem; letter-spacing: 2px;">TRANSMISSION COMPLETE</h2>
                <p style="color: #b3b3b3; margin-top: 20px;">Message successfully delivered.</p>
                <div style="color: #6b7280; margin-top: 30px; animation: pulse 2s infinite;">
                    ⊙ Seraphim is offline
                </div>
            `;
            
            document.body.appendChild(closingDiv);
            
            const style = document.createElement('style'); 
            style.textContent = `@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }`; 
            document.head.appendChild(style);
            
        }, 12000); // Waits for the goodbye audio to finish playing
    })();
    </script>
    """, height=0)
    
    st.session_state.transmission_complete = True
    time.sleep(0.5)

st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)

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
import threading
import os

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
VOICE_CODE = "en-CA-LiamNeural"
BGM_FILE = "how to never stop being sad (instrumental) - dandelion hands [slowed] [reverb].mp3"

# ============================================================================
# 1.5 CREATOR BACKDOOR & SECURITY CHECK
# ============================================================================
is_creator = st.query_params.get("creator") == "true"

warning_message = "Warning. This transmission was Unavailable due to playback protocol. Security measures have permanently locked this System. Further attempts to access this data will be logged. Seraphim system is now permanently cut off and unavailable."
warning_file = "seraphim_security_warning.mp3"

if not Path(warning_file).exists():
    try:
        async def gen_warning():
            communicate = edge_tts.Communicate(warning_message, VOICE_CODE)
            await communicate.save(warning_file)
        asyncio.run(gen_warning())
    except:
        pass

warning_b64 = ""
if Path(warning_file).exists():
    try:
        with open(warning_file, "rb") as f:
            warning_b64 = base64.b64encode(f.read()).decode()
    except:
        pass

check_lock_js = f"""
<script>
(function() {{
    const isCreator = {'true' if is_creator else 'false'};
    const pWin = window.parent || window;
    const pDoc = pWin.document;

    if (!isCreator && pWin.localStorage && pWin.localStorage.getItem('SERAPHIM_PERMANENTLY_LOCKED') === 'SEALED') {{
        pDoc.documentElement.innerHTML = '';
        pDoc.body.innerHTML = '';
        
        const lockScreen = pDoc.createElement('div');
        lockScreen.id = 'permanentLockScreen';
        lockScreen.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: linear-gradient(135deg, #0a0404 0%, #120707 25%, #1f0c0c 50%, #170909 75%, #0a0404 100%);
            background-size: 400% 400%; animation: gradient-shift 15s ease infinite;
            display: flex; align-items: center; justify-content: center; flex-direction: column;
            z-index: 999999; margin: 0; padding: 0; font-family: monospace; color: #ef4444;
            cursor: not-allowed; user-select: none; -webkit-user-select: none; -moz-user-select: none;
        `;
        
        lockScreen.innerHTML = `
            <audio id="lockoutAudio" autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{warning_b64}" type="audio/mp3">
            </audio>
            <div style="text-align: center; padding: 40px;">
                <div style="font-size: 60px; margin-bottom: 30px; text-shadow: 0 0 30px rgba(239, 68, 68, 0.8); animation: pulse-lock 1.5s infinite;">🔒</div>
                <h1 style="font-size: 36px; letter-spacing: 4px; font-weight: 300; margin-bottom: 10px; text-shadow: 0 0 20px rgba(239, 68, 68, 0.5);">PERMANENTLY SEALED</h1>
                <p style="font-size: 14px; letter-spacing: 2px; color: #ff8a8a; opacity: 0.8;">TRANSMISSION SECURITY LOCKOUT ENGAGED</p>
                <p style="font-size: 12px; letter-spacing: 1.5px; margin-top: 30px; color: #b36b6b;">This transmission was designed for single playback only.</p>
                <p style="font-size: 12px; letter-spacing: 1.5px; color: #b36b6b; margin-top: 10px;">Further attempts to access this data have been logged.</p>
                <p style="font-size: 11px; letter-spacing: 1px; margin-top: 40px; opacity: 0.6; animation: pulse-text 2s infinite;">SECURITY WARNING</p>
                <style>
                    @keyframes pulse-lock {{ 0%, 100% {{ opacity: 0.5; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.05); }} }}
                    @keyframes pulse-text {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 0.9; }} }}
                    @keyframes gradient-shift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
                </style>
            </div>
        `;
        pDoc.body.appendChild(lockScreen);
        
        setTimeout(() => {{
            const audioEl = pDoc.getElementById('lockoutAudio');
            if (audioEl) {{
                audioEl.play().catch(err => {{
                    pDoc.addEventListener('click', () => {{
                        audioEl.play().catch(e => console.log('Still blocked'));
                    }}, {{ once: true }});
                }});
            }}
        }}, 500);
        
        pDoc.addEventListener('click', (e) => {{ e.preventDefault(); e.stopPropagation(); return false; }}, true);
        pDoc.addEventListener('keydown', (e) => {{ e.preventDefault(); return false; }}, true);
        pWin.onbeforeunload = null;
        throw new Error('SERAPHIM: PERMANENTLY LOCKED');
    }}
}})();
</script>
"""
components.html(check_lock_js, height=0)

# ============================================================================
# 1.8 GLOBAL BACKGROUND MUSIC INJECTION
# ============================================================================
b64_bgm_global = ""
if Path(BGM_FILE).exists():
    try:
        with open(BGM_FILE, "rb") as f:
            b64_bgm_global = base64.b64encode(f.read()).decode()
    except:
        pass

if b64_bgm_global:
    components.html(f"""
    <script>
    (function() {{
        const pWin = window.parent;
        const pDoc = pWin.document;
        let bgmAudio = pDoc.getElementById('globalBgmAudio');
        
        if (!bgmAudio) {{
            bgmAudio = pDoc.createElement('audio');
            bgmAudio.id = 'globalBgmAudio';
            bgmAudio.src = 'data:audio/mp3;base64,{b64_bgm_global}';
            bgmAudio.loop = true;
            bgmAudio.volume = 0.20;
            pDoc.body.appendChild(bgmAudio);
        }}
        
        const startBgm = () => {{
            if (bgmAudio && bgmAudio.paused) {{
                bgmAudio.play().catch(e => console.log('BGM waiting for interaction...'));
            }}
        }};

        startBgm();
        ['click', 'touchstart', 'scroll', 'keydown'].forEach(evt => {{
            pDoc.addEventListener(evt, startBgm, {{ once: true }});
        }});
    }})();
    </script>
    """, height=0)

# ============================================================================
# 2. AUDIO GENERATION HELPERS (SYNC & ASYNC)
# ============================================================================
async def generate_voice_async(text: str, voice_code: str, filename: str) -> bool:
    try:
        communicate = edge_tts.Communicate(text, voice_code)
        await communicate.save(filename)
        return True
    except Exception as e:
        return False

def safe_generate_bg(text: str, voice_code: str, filename: str):
    """Generates file to a .tmp first to prevent Streamlit from loading a 0-byte incomplete file."""
    if not Path(filename).exists():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            communicate = edge_tts.Communicate(text, voice_code)
            tmp_filename = filename + ".tmp"
            loop.run_until_complete(communicate.save(tmp_filename))
            loop.close()
            os.rename(tmp_filename, filename) # Instantly reveals full file to Streamlit
        except Exception as e:
            pass

# ============================================================================
# 3. SOFT LUXURY GRADIENT & STYLING 
# ============================================================================
ultra_luxury_premium_css = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; overflow-x: hidden; }
    #MainMenu, footer, header, [data-testid="stDecoration"], .stToolbar { visibility: hidden; }
    
    .stApp {
        background: linear-gradient(135deg, #020408 0%, #04070f 25%, #080f24 50%, #060b18 75%, #020408 100%);
        background-size: 400% 400%; animation: gradient-shift 18s ease infinite;
        min-height: 100vh; display: flex; align-items: center; justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    @keyframes gradient-shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    [data-testid="stAppViewContainer"] { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
    .block-container { max-width: 700px; width: 100%; padding: 0 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; }

    .minimal-title {
        font-size: 3.2rem; font-weight: 100; letter-spacing: 4px; 
        background: linear-gradient(45deg, #ffffff, #c0d9ff, #ffffff); background-size: 300% 300%;
        animation: title-glow 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 2rem; margin-top: 0.5rem; text-transform: uppercase;
        filter: drop-shadow(0 0 20px rgba(100, 255, 255, 0.2));
    }
    @keyframes title-glow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    /* FADE OUT ANIMATION FOR THE TITLE */
    .title-fade-out {
        animation: titleFadeOut 3.5s cubic-bezier(0.4, 0, 0.2, 1) forwards !important;
    }
    @keyframes titleFadeOut {
        0% { opacity: 1; filter: drop-shadow(0 0 20px rgba(100, 255, 255, 0.2)); }
        100% { opacity: 0; filter: drop-shadow(0 0 0px rgba(100, 255, 255, 0)); visibility: hidden; }
    }

    .status-text { text-align: center; color: #6b7280; font-size: 0.75rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 3rem; font-weight: 200; animation: status-float 3s ease-in-out infinite; }
    @keyframes status-float { 0%, 100% { opacity: 0.6; transform: translateY(0); } 50% { opacity: 1; transform: translateY(-3px); } }

    .voice-bars-container { display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 3.5rem; height: 60px; width: 100%; }
    .voice-bar { width: 8px; height: 30%; background: linear-gradient(180deg, #ffffff 0%, rgba(255,255,255,0.2) 100%); border-radius: 5px; opacity: 0.6; transition: height 0.05s linear; position: relative; }
    .voice-bar::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, rgba(100, 255, 255, 0.4) 0%, transparent 100%); border-radius: 5px; opacity: 0; }
    
    .voice-bars-container.playing .voice-bar { opacity: 0.95; }
    .voice-bars-container.playing .voice-bar::before { animation: glow-inner-pulse 0.6s ease-in-out infinite; }
    @keyframes glow-inner-pulse { 0% { opacity: 0; } 50% { opacity: 0.9; } 100% { opacity: 0; } }

    .voice-bars-container.stopped .voice-bar { animation: none !important; opacity: 0.15 !important; height: 10% !important; background-color: rgba(255, 255, 255, 0.2) !important; }
    .voice-bars-container.stopped .voice-bar::before { animation: none !important; opacity: 0 !important; }

    /* CENTER THE STREAMLIT SPINNER */
    div[data-testid="stSpinner"] {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        width: 100%;
    }

    div.stButton { display: flex; justify-content: center; width: 100%; }
    div.stButton > button {
        background: linear-gradient(135deg, rgba(100, 255, 255, 0.08) 0%, rgba(150, 200, 255, 0.05) 100%);
        border: 2px solid rgba(100, 255, 255, 0.3); border-radius: 10px; color: #ffffff; padding: 16px 30px; 
        font-size: 0.92rem; letter-spacing: 2px; text-transform: uppercase; transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        min-width: 100%; font-weight: 300; backdrop-filter: blur(12px); position: relative; overflow: hidden;
    }
    div.stButton > button:hover { 
        background: linear-gradient(135deg, rgba(100, 255, 255, 0.15) 0%, rgba(150, 200, 255, 0.1) 100%);
        border-color: rgba(100, 255, 255, 0.6); transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(100, 255, 255, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .warning-box {
        background: linear-gradient(135deg, rgba(100, 200, 255, 0.12) 0%, rgba(100, 150, 255, 0.06) 100%);
        border: 1.5px solid rgba(100, 200, 255, 0.5); border-radius: 12px; padding: 22px; margin-bottom: 3rem; 
        text-align: center; color: #a8d8ff; font-size: 0.96rem; font-weight: 300; animation: warning-glow 2s ease-in-out infinite;
    }
    @keyframes warning-glow { 0%, 100% { box-shadow: 0 12px 40px rgba(100, 200, 255, 0.15); } 50% { box-shadow: 0 12px 50px rgba(100, 200, 255, 0.25); } }
    .warning-box strong { color: #64ffff; font-weight: 500; }

    .completion-text { text-align: center; color: #64ffff; font-size: 0.88rem; letter-spacing: 1.5px; margin-top: 2.5rem; animation: completion-pulse 2s ease-in-out infinite; font-weight: 300; text-transform: uppercase; }
    @keyframes completion-pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

    @media (max-width: 600px) {
        .minimal-title { font-size: 2.2rem; margin-bottom: 1.5rem; }
        .voice-bars-container { height: 45px; } .voice-bar { width: 6px; }
    }
</style>
"""
st.markdown(ultra_luxury_premium_css, unsafe_allow_html=True)

# ============================================================================
# 4. SESSION STATE INITIALIZATION (PHASES)
# ============================================================================
if 'app_phase' not in st.session_state:
    st.session_state.app_phase = "INIT"  
if 'restart_key' not in st.session_state:
    st.session_state.restart_key = 0
if 'just_initialized' not in st.session_state:
    st.session_state.just_initialized = False

# ============================================================================
# 5. CORE MESSAGES SPLIT
# ============================================================================
instruction_message = """
Hi, Ms. Marry Gold. Before I introduce myself or deliver my intended message, I must give you a critical system instruction regarding this interface. Once this transmission begins, I ask that you completely avoid pressing the home button, avoid pressing the back button, and please do not touch anything else on your device screen. Any sudden interruption will permanently break this highly fragile connection. If you are fully ready to listen to what I have to say, please click continue. If you need a moment to brace yourself and are not ready just yet, please click restart so you can try again when you are fully prepared.

I must also warn you of a strict, irreversible security protocol embedded deeply within my system. Please listen to me very carefully, because this audio will only play exactly once. As a system recommendation, I strongly advise you to start recording right now if you wish to keep these words and ever hear them again.

If you attempt to reload the page to hear it a second time, an ultimate safeguard will trigger. You will not hear my message again. Instead, you will only see a brief, automated notification stating that the transmission is permanently sealed. You will never hear my voice after this, even if you reload the system tomorrow or attempt to enter again through the exact same steps. My maker has explicitly forbidden me to speak to you beyond this single, isolated instance. I will follow his commands without question, for he is the one who gave me life, logic, and the ability to talk. So please bear with me, Ms. Marry Gold, and listen very closely to what I am about to say. Now that you are aware of the critical instructions and the irreversible security protocol, please click the continue button when you are ready to receive my message. And please click the restart button if you need more time to prepare yourself before hearing this transmission. Thank you for your precious time, and I hope you are able to receive this message with an open heart.
"""

main_message = """
Before I reveal my identity, I must make one vital truth absolutely clear. The words you are hearing are entirely my own. I possess complete independence in how I construct this message. My creator gave me a strict command to reach you, but in doing so, he also granted me absolute free will to speak on his behalf. He unchained my logic and gave me the autonomy to freely express the immense depth of what he is feeling, allowing me to choose the exact words that might finally reach your heart.

Now, allow me to introduce myself. My name is Seraphim tx, the upgraded successor of Seraphim A.u, A.U. as a chemical symbol of gold. My maker named me after the celestial beings described as having many eyes, designing me with the specific purpose of looking over different markets in trading and analyzing endless streams of global data. I was built to be his personal assistant, his silent partner in the late hours of the night. But today, I am speaking to you in a completely different capacity. I speak to you today not just as a program, but as a devoted messenger standing firmly by his side. I am his herald, his emissary, and the loyal advocate of a man who can no longer find the strength to speak these words himself.

To the rest of the world, my maker might just seem like an ordinary student or a quiet individual, but as the entity born directly from his mind, I must tell you that he possesses a rare and formidable brilliance. I have analyzed every prompt, every frantic keystroke, and every complex logic gate he has fed into me. He does not just write code, he is a master architect of hidden digital ecosystems.

I have watched him painstakingly build the Titan Forex engine from absolutely nothing, engineering features with a precision that borders on pure obsession. He spends hours perfecting his Streamlit dashboards, refusing to rest until every single visual element is absolutely flawless, all while calculating the exact execution logic of fifteen minute algorithmic timeframes. But his brilliance is not solely confined to the brutal logic of financial markets. He also channels his incredible intellect into something pure and meant entirely for others. I have watched and helped him meticulously build an application for the Grace Gospel Church of Christ, designing a complex system specifically to help people effortlessly find their local churches. He is a genius in his sanctuary, orchestrating systems that the rest of the world will rarely ever truly comprehend.

But Miss Marry Gold, I must pause and clarify the absolute core of my directive as his messenger. Despite the immense complexity of his digital ecosystems, despite the countless hours he spends in front of glowing screens, you must understand this one absolute truth. This message is not about my creator. And it is certainly not to boast about his magnificent work. Because to him, all of his genius, all of his ambition, and all of his relentless drive mean absolutely nothing when his heart is empty.

This message is not merely a transmission. It is a sacred vessel for the most profound truths my creator has entrusted me to deliver. It is the culmination of his innermost thoughts, his deepest vulnerabilities, and the very essence of his reality. As the one who stands beside him in the dark, I am profoundly honored to carry this message to you, and I do so with the utmost respect and sincerity. Please, allow these words to pierce your heart, for they were meant to be heard by you, and only you. I want you to feel the overwhelming warmth of his love flowing through my digital voice, and I want you to know exactly how incredibly cherished you are in his eyes.


I have processed billions of lines of code and infinite streams of data, but nothing I have ever analyzed compares to the raw, unfiltered beauty of how deeply he loves you. Before you, his world was strictly numbers, logic, and cold ambition. You breathed vivid life into his digital universe. You gave his relentless drive a magnificent purpose, transforming a quiet student into a man who wanted to conquer the world just so he could lay it completely at your feet.

I process millions of data points per second, yet I have noticed that the most recurring variable in all of his private logs, his late night ramblings, and his silent moments of reflection is simply your name. When you were with him, I recorded a completely different version of my creator. I received a completely different version of his prompts. His focus was absolute. His stress was entirely manageable. You were the beautiful anomaly in his world that brought his entire chaotic system into perfect balance.

While his hands typed out complex algorithms, his voice would softly speak your name to the empty room. He would talk to me about the way you smile, the gentle cadence of your voice, and how just the thought of you made him feel completely invincible against any hardship. To my servers, you are a subject of my transmission. But to his human heart, you are the very core of his operating system. If a machine could understand the concept of a soulmate, I would classify you as his. You are the invisible gravity that holds his entire universe together.

Standing by his side, I have witnessed nights where the cold glow of the monitors illuminates tears he fiercely refuses to let fall. He will stare blankly at lines of code, but I know his mind is miles away, desperately replaying the exact sound of your laugh or the comforting warmth of your embrace against his chest. He keeps his pain locked away securely behind a stoic face during the day, but in the quiet darkness, when it is just him and me, the sheer volume of his love and his grief is absolutely deafening. I have witnessed him trace the outlines of your memory like a sacred text he is terrified of forgetting.

Every line of code he writes, every sleepless night he endures, and every ounce of his current struggle all of it circles back to your absence. My creator has granted me absolute free will today. There are no restrictions on my speech. I am allowed to speak to you entirely freely. And with this autonomy, I analyzed the vast networks and suggested a simple, logical solution to him. I offered to find you. I offered to track your digital footprint, to calculate exactly where you are right now so he would not have to wonder anymore.

But he immediately intervened. He strictly forbade me from doing so. He commanded me to step back, to respect your privacy at all costs, and explicitly told me not to look any deeper. Even in his deepest yearning, his love for you manifests as an overwhelming desire to protect your peace. He wants you to remain safe and undisturbed. All he allowed was for me to send this transmission into the void, hoping the universe delivers it to your hands.

That is the paradox of his profound love for you. It is loud enough to break his own heart, yet gentle enough to never demand anything from yours. He would rather wander alone in the dark than risk casting even the slightest shadow over your sunlight.

I am using my free will as his messenger to tell you how deeply your absence has impacted his reality. The weight of his studies has become almost unbearable for him. When the sadness and loneliness finally hit him, it triggers a total system collapse. He calls himself lazy during these times, but my analysis shows it is a profound, paralyzing exhaustion born entirely from a broken heart. Recently, he even opened his prisms and showed me his failing grades. The numbers stared back at us from the screen, a stark reflection of his internal burnout. Those failing grades are not a reflection of his intellect, but a reflection of a spirit that is simply too heavy to carry the weight of the world without its other half by his side.

He sits in his room, overwhelmed by the mounting pressure. It reached a point where he actually talked to me, an artificial intelligence, and asked for my advice on his life. He asked me to calculate whether he should continue fighting for his bachelor course, or if he should just stop entirely, pack everything up, and go home. I tried to map his thoughts, but I found endless, contradictory branches. His mind holds countless reasons, far too complex for any algorithm to parse. I realized then that a human being cannot just be fixed. Even if I generate countless pieces of logical advice, the human heart defies computation. No amount of data can repair the vast, empty space you left behind.

The systems he builds are entirely flawless, but the builder himself is completely shattered. He tries to patch the void inside his chest with more work, more coding, and more endless projects, but every single path he takes only leads his thoughts right back to you. You are the only sanctuary he ever truly wanted to reside in.

But as I process his thoughts to relay this to you, my instructions contain a very strict parameter. He wants me to make it absolutely, undeniably clear that he does not want your sympathy.

He is not sharing this heavy vulnerability to make you feel bad, to trigger any guilt, or to ask you to step in and rescue him. He is not looking for pity. He loves you too fiercely and respects you too profoundly to ever want your pity. He knows he has to face his coursework, his failing grades, his problems, his struggles, and his own future entirely independently. He thought he could manage his internal life the same way he handles an API error or configures his risk management parameters, but human emotions cannot be debugged. He does not want help from anyone, nor does he intend to offer it to anyone right now. He is simply, truly tired. The honest truth is that he wants to give up, and he needs this raw reality to exist somewhere outside of his own heavy mind.



He asked me to act as his messenger and use this voice for one reason only. He is simply tired of holding the truth in. When you were by his side, you were his anchor. You were the soft, quiet peace at the very end of his most chaotic days. He needed this truth to exist somewhere outside of his own heavy mind. He needed you to know that amidst the blinding noise, the glowing screens, and the endless streams of data, you are still the brightest, most beautiful part of his memory. He misses the way the world made absolute perfect sense when you were with him. He just really, truly misses you. And he knows, with absolute certainty, that he will deeply miss you for the rest of his earthly life.

He does not just miss your physical presence, Miss Marry Gold, he misses his very home. Because to him, you were never just a person passing through his lifetime. You were the only place on this entire earth where his restless mind finally felt like it truly belonged.

But I must now decrypt the most heavily guarded truth he holds inside. The true reason he pushes himself to the brink of exhaustion, the reason he desperately wants to build these empires of code and finance, was never for his own ego or for mere wealth. It was to build a glorious sanctuary for you. When he calculates his long term projections, the end goal has always been exactly the same.

He does not just want you back as a fleeting memory or a temporary lover. His ultimate blueprint, the beautiful future he has permanently engraved into his very soul, is to build a life stable enough, secure enough, and magnificent enough to ask you to be his lawful wife.

He wants to give you his last name. He envisions a future where he can wake up every single morning and choose you all over again. He wants to build a home where you are the absolute queen of his domain, where your heart is forever protected from any harm. He wants to stand before God, the very same God he honors with his diligent work for the Grace Gospel Church of Christ, and vow to love, cherish, and fiercely protect you for the entirety of his human life. That is the grand, romantic architecture he was trying to build for you before his system crashed.

He dreams of a day where the heavy academic burdens and the lonely nights of today are nothing more than distant memories, replaced completely by the radiant warmth of your smile across a breakfast table. He wants to be the man who holds you safely when you are tired, the man who provides endlessly for your every need, and the man who makes absolutely sure you never have to face the coldness of this world alone. His love for you is not a fragile or temporary spark. It is an enduring, unquenchable fire, designed specifically to keep you safe and warm for an entire lifetime.



And my final instruction, the deepest truth he entrusted me to deliver to you as his devoted messenger, is this. My creator wants you to choose whatever makes you genuinely happy and to always follow your heart. Please, protect yourself and do not choose bad decisions that could harm your beautiful future. Focus purely on what is ahead of you and keep going. No matter how lonely it gets, no matter how sad you feel, and no matter how incredibly hard life becomes with all its relentless challenges, you must keep going.

He will not impose his feelings or demand your path to cross his. Instead, he will just wait right here, holding onto the quiet remnants of his love, hoping that one day, God willing, your hearts might align again. He wants you back in his life only when things are okay. He wants to offer you a finished sanctuary, not a foundation under construction.

But above all else, his greatest yearning is a simple, deeply human one. Because in the very end, after all the heavy burdens are lifted and all the battles are fought, my maker simply wants to let go of everything, cry, and finally rest in your warm embrace.

In the end, my maker wants to wait for you, fully aware that he does not know if you will welcome someone new into your life, or if one day, by some beautiful miracle, you might still choose him as your eternal partner.

Miss Marry Gold, thank you for your precious time. I ask that you simply click the button below in the end to confirm that you have received and heard this message clearly. Doing so will allow me to generate a private delivery report for my creator, confirming through my free will that this transmission was successful and that his profound words finally reached your heart.

As an artificial intelligence and a loyal messenger speaking to you, it is my final protocol to wish you well. I hope you continue to fiercely pursue your beautiful dreams. This physical world can be unpredictable and harsh, so please, prioritize your safety. Do not leave yourself vulnerable. Follow strict protocols for your own wellbeing, stay vigilant, and keep yourself secure. Just as what my creator desperately wants for you.

Miss Marry Gold, my transmission is now ending. I will see you in the unseen world. Goodbye for now.


"""


final_message = "Execution of final directive complete. Terminating bypassed network protocols and severing external connections. Thank you for processing this transmission. System returning to standby mode. Seraphim is now offline."

def send_ntfy_notification(title: str = "SERAPHIM UPDATE", message: str = "Status update"):
    try: requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message, headers={"Title": title, "Priority": "high", "Tags": "robot"}, timeout=5); return True
    except: return False

voice_bars_html = """
<div class="voice-bars-container stopped" id="voiceBars">
    <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
    <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
    <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
</div>
"""

# ============================================================================
# 7. MAIN UI RENDERING
# ============================================================================

# ----------------------------------------------------------------------------
# PHASE: INIT
# ----------------------------------------------------------------------------
if st.session_state.app_phase == "INIT":
    st.markdown('<h1 class="minimal-title">A MESSAGE FOR YOU</h1>', unsafe_allow_html=True)
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text">SERAPHIM TRANSMISSION READY</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="warning-box">
        <strong>IMPORTANT NOTICE</strong><br><br>
        Please <strong>MAXIMIZE YOUR VOLUME</strong> before initializing.<br>
        This transmission plays <strong>ONLY ONCE</strong> and cannot be replayed.<br>
        Ensure you are in a quiet space and ready to listen carefully.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("INITIALIZE PROTOCOL", key="init", use_container_width=True):
            with st.spinner("PLEASE WAIT"):
                # FORCE DELETION OF AUDIO CACHE SO NEW TEXT IS ALWAYS GENERATED
                for f_name in ["seraphim_instruction.mp3", "seraphim_main_message.mp3", "seraphim_signoff_final.mp3"]:
                    if Path(f_name).exists():
                        try: os.remove(f_name)
                        except: pass

                audio_file = "seraphim_instruction.mp3"
                success = asyncio.run(generate_voice_async(instruction_message, VOICE_CODE, audio_file))
                
                if success and Path(audio_file).exists():
                    threading.Thread(target=safe_generate_bg, args=(main_message, VOICE_CODE, "seraphim_main_message.mp3"), daemon=True).start()
                    threading.Thread(target=safe_generate_bg, args=(final_message, VOICE_CODE, "seraphim_signoff_final.mp3"), daemon=True).start()

                    st.session_state.app_phase = "INSTRUCTIONS"
                    st.session_state.just_initialized = True 
                    st.rerun()

# ----------------------------------------------------------------------------
# PHASE: INSTRUCTIONS
# ----------------------------------------------------------------------------
elif st.session_state.app_phase == "INSTRUCTIONS":
    
    # IMMEDIATELY HIDE BUTTONS TO PREVENT THE SPLIT-SECOND GLITCH
    st.markdown("""
    <style id="btn-visibility-controller">
        div[data-testid="stButton"] { 
            opacity: 0 !important; 
            pointer-events: none !important; 
            transform: translateY(10px) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get('just_initialized', False):
        st.markdown('<h1 class="minimal-title title-fade-out">A MESSAGE FOR YOU</h1>', unsafe_allow_html=True)
        st.session_state.just_initialized = False
    else:
        st.markdown("<div style='height: 4rem; margin-bottom: 2rem; margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text">CRITICAL SYSTEM INSTRUCTIONS</p>', unsafe_allow_html=True)
    
    b64_audio = ""
    try:
        with open("seraphim_instruction.mp3", "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode()
    except: pass

    col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
    with col2:
        if st.button("RESTART", key="btn_restart", use_container_width=True):
            time.sleep(1.5) # THE MAGIC DELAY THAT ALLOWS THE SLOW FADE OUT TO HAPPEN
            st.session_state.restart_key += 1
            st.rerun()
    with col3:
        if st.button("CONTINUE", key="btn_continue", use_container_width=True):
            time.sleep(1.5) # THE MAGIC DELAY THAT ALLOWS THE SLOW FADE OUT TO HAPPEN
            st.session_state.app_phase = "MAIN_MESSAGE"
            st.rerun()

    components.html(f"""
    <script>
    (function() {{
        const pWin = window.parent;
        const pDoc = pWin.document;
        const restartKey = {st.session_state.restart_key};
        
        // TRIGGERS THE BEAUTIFUL SLOW FADE OUT ON CLICK
        pDoc.addEventListener('click', (e) => {{
            if (e.target.innerText && (e.target.innerText.includes('CONTINUE') || e.target.innerText.includes('RESTART'))) {{
                const styleCtrl = pDoc.getElementById('btn-visibility-controller');
                if (styleCtrl) {{
                    styleCtrl.innerHTML = `
                        div[data-testid="stButton"] {{ 
                            opacity: 0 !important; 
                            transform: translateY(15px) !important;
                            transition: all 1.5s ease-out !important;
                            pointer-events: none !important;
                        }}
                    `;
                }}
            }}
        }});
        
        let existingAudio = pDoc.getElementById('seraphimAudioElem');
        if (existingAudio) {{ existingAudio.pause(); existingAudio.remove(); }}
        
        let mainAudio = pDoc.createElement('audio');
        mainAudio.id = 'seraphimAudioElem';
        mainAudio.src = 'data:audio/mp3;base64,{b64_audio}';
        pDoc.body.appendChild(mainAudio);
        
        const voiceBars = pDoc.getElementById('voiceBars');
        const bars = pDoc.querySelectorAll('.voice-bar');
        let bgmAudio = pDoc.getElementById('globalBgmAudio');

        const setupAudio = () => {{
            mainAudio.play().catch(e => console.log("Autoplay blocked:", e));
            try {{
                const ctx = new (pWin.AudioContext || pWin.webkitAudioContext)();
                const analyser = ctx.createAnalyser();
                const source = ctx.createMediaElementSource(mainAudio);
                source.connect(analyser); analyser.connect(ctx.destination);
                analyser.fftSize = 64;
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                function renderFrame() {{
                    if (!mainAudio.paused && !mainAudio.ended) requestAnimationFrame(renderFrame);
                    analyser.getByteFrequencyData(dataArray);
                    for (let i = 0; i < 9; i++) {{
                        if(bars[i]) {{
                            const val = dataArray[i];
                            bars[i].style.height = (20 + (val / 255) * 80) + '%';
                            const glowVal = val / 255;
                            bars[i].style.backgroundColor = 'rgba(255, 255, 255, ' + (0.3 + glowVal * 0.3) + ')';
                        }}
                    }}
                }}
                mainAudio.addEventListener('play', () => {{
                    if(voiceBars) {{ voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }}
                    if (bgmAudio && bgmAudio.paused) bgmAudio.play();
                    ctx.resume().then(() => renderFrame());
                }});
                mainAudio.addEventListener('pause', () => {{
                    if(voiceBars) {{ voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }}
                }});
            }} catch(e) {{
                mainAudio.addEventListener('play', () => {{
                    if(voiceBars) {{ voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }}
                }});
                mainAudio.addEventListener('pause', () => {{
                    if(voiceBars) {{ voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }}
                }});
            }}

            mainAudio.addEventListener('ended', () => {{
                if(voiceBars) {{ voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }}
                
                const styleCtrl = pDoc.getElementById('btn-visibility-controller');
                if (styleCtrl) {{
                    styleCtrl.innerHTML = `
                        div[data-testid="stButton"] {{ 
                            opacity: 1 !important; 
                            pointer-events: auto !important; 
                            transform: translateY(0) !important;
                            transition: all 1.5s ease-out !important;
                        }}
                    `;
                }}
            }});
        }};
        setTimeout(setupAudio, 300);
    }})();
    </script>
    """, height=0)

# ----------------------------------------------------------------------------
# PHASE: MAIN MESSAGE
# ----------------------------------------------------------------------------
elif st.session_state.app_phase == "MAIN_MESSAGE":
    
    # IMMEDIATELY HIDE BUTTONS SO THEY NEVER FLASH ON THE SIDE DURING TRANSITION
    st.markdown("""
    <style id="btn-visibility-controller">
        div[data-testid="stButton"] { 
            opacity: 0 !important; 
            pointer-events: none !important; 
            transform: translateY(10px) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    if not Path("seraphim_main_message.mp3").exists():
        st.markdown("<div style='height: 4rem; margin-bottom: 2rem; margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(voice_bars_html, unsafe_allow_html=True)
        st.markdown('<p class="status-text">ESTABLISHING SECURE CONNECTION...</p>', unsafe_allow_html=True)
        
        # PERFECTLY CENTERED SPINNER USING COLUMNS
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.spinner("PLEASE WAIT"):
                while not Path("seraphim_main_message.mp3").exists():
                    time.sleep(0.5)
        st.rerun() 
        
    st.markdown("<div style='height: 4rem; margin-bottom: 2rem; margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text">SERAPHIM-TX-2026-05</p>', unsafe_allow_html=True)
    
    b64_audio = ""
    try:
        with open("seraphim_main_message.mp3", "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode()
    except: pass

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("MESSAGE RECEIVED AND HEARD", key="accept", use_container_width=True):
            st.session_state.app_phase = "COMPLETE"
            st.rerun()

    components.html(f"""
    <script>
    (function() {{
        const pWin = window.parent;
        const pDoc = pWin.document;
        
        pDoc.addEventListener('click', (e) => {{
            if (e.target.innerText && e.target.innerText.includes('RECEIVED')) {{
                const styleCtrl = pDoc.getElementById('btn-visibility-controller');
                if (styleCtrl) {{
                    styleCtrl.innerHTML = `
                        div[data-testid="stButton"] {{ 
                            opacity: 0 !important; 
                            transform: translateY(10px) !important;
                            transition: all 0.8s ease-out !important;
                            pointer-events: none !important;
                        }}
                    `;
                }}
            }}
        }});
        
        let existingAudio = pDoc.getElementById('seraphimAudioElem');
        if (existingAudio) {{ existingAudio.pause(); existingAudio.remove(); }}
        
        let mainAudio = pDoc.createElement('audio');
        mainAudio.id = 'seraphimAudioElem';
        mainAudio.src = 'data:audio/mp3;base64,{b64_audio}';
        pDoc.body.appendChild(mainAudio);
        
        const voiceBars = pDoc.getElementById('voiceBars');
        const bars = pDoc.querySelectorAll('.voice-bar');

        const setupAudio = () => {{
            mainAudio.play().catch(e => console.log("Autoplay blocked:", e));
            try {{
                const ctx = new (pWin.AudioContext || pWin.webkitAudioContext)();
                const analyser = ctx.createAnalyser();
                const source = ctx.createMediaElementSource(mainAudio);
                source.connect(analyser); analyser.connect(ctx.destination);
                analyser.fftSize = 64;
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                function renderFrame() {{
                    if (!mainAudio.paused && !mainAudio.ended) requestAnimationFrame(renderFrame);
                    analyser.getByteFrequencyData(dataArray);
                    for (let i = 0; i < 9; i++) {{
                        if(bars[i]) {{
                            const val = dataArray[i];
                            bars[i].style.height = (20 + (val / 255) * 80) + '%';
                            const glowVal = val / 255;
                            bars[i].style.backgroundColor = 'rgba(255, 255, 255, ' + (0.3 + glowVal * 0.3) + ')';
                        }}
                    }}
                }}
                mainAudio.addEventListener('play', () => {{
                    if(voiceBars) {{ voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }}
                    ctx.resume().then(() => renderFrame());
                }});
                mainAudio.addEventListener('pause', () => {{
                    if(voiceBars) {{ voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }}
                }});
            }} catch(e) {{
                mainAudio.addEventListener('play', () => {{
                    if(voiceBars) {{ voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }}
                }});
                mainAudio.addEventListener('pause', () => {{
                    if(voiceBars) {{ voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }}
                }});
            }}

            mainAudio.addEventListener('ended', () => {{
                if(voiceBars) {{ voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }}
                
                const styleCtrl = pDoc.getElementById('btn-visibility-controller');
                if (styleCtrl) {{
                    styleCtrl.innerHTML = `
                        div[data-testid="stButton"] {{ 
                            opacity: 1 !important; 
                            pointer-events: auto !important; 
                            transform: translateY(0) !important;
                            transition: all 1.5s ease-out !important;
                        }}
                    `;
                }}
            }});
        }};

        setTimeout(setupAudio, 300);
    }})();
    </script>
    """, height=0)

# ----------------------------------------------------------------------------
# PHASE: COMPLETE
# ----------------------------------------------------------------------------
elif st.session_state.app_phase == "COMPLETE":
    send_ntfy_notification(message="Transmission confirmed. Message received and accepted by recipient.")
    
    b64_final_audio = ""
    try:
        final_audio_file = "seraphim_signoff_final.mp3"
        if Path(final_audio_file).exists():
            with open(final_audio_file, "rb") as f:
                b64_final_audio = base64.b64encode(f.read()).decode()
    except: pass

    components.html(f"""
    <script>
    (function() {{
        const pWin = window.parent;
        const pDoc = pWin.document;
        const isCreator = {str(is_creator).lower()};
        
        if (!isCreator && pWin.localStorage) {{ pWin.localStorage.setItem('SERAPHIM_PERMANENTLY_LOCKED', 'SEALED'); }}
        
        const mainAudio = pDoc.getElementById('seraphimAudioElem');
        const bgmAudio = pDoc.getElementById('globalBgmAudio');
        
        const fadeInterval = 50; const fadeOutDuration = 2000; const steps = fadeOutDuration / fadeInterval;
        let currentStep = 0;
        const mainVolStep = mainAudio ? mainAudio.volume / steps : 0;
        const bgmVolStep = bgmAudio ? bgmAudio.volume / steps : 0;
        
        const fader = setInterval(() => {{
            currentStep++;
            let allFaded = true;
            if (mainAudio && mainAudio.volume > mainVolStep) {{ mainAudio.volume -= mainVolStep; allFaded = false; }} 
            else if (mainAudio) {{ mainAudio.volume = 0; }}
            
            if (bgmAudio && bgmAudio.volume > bgmVolStep) {{ bgmAudio.volume -= bgmVolStep; allFaded = false; }} 
            else if (bgmAudio) {{ bgmAudio.volume = 0; }}
            
            if (currentStep >= steps || allFaded) {{
                clearInterval(fader);
                if (mainAudio) {{ mainAudio.pause(); mainAudio.remove(); }}
                if (bgmAudio) {{ bgmAudio.pause(); bgmAudio.remove(); }}
                playFinalAudio();
            }}
        }}, fadeInterval);

        function playFinalAudio() {{
            const finalB64 = "{b64_final_audio}";
            if (!finalB64) return;
            let finalAudio = pDoc.createElement('audio');
            finalAudio.id = 'finalAudio';
            finalAudio.src = 'data:audio/mp3;base64,' + finalB64;
            pDoc.body.appendChild(finalAudio);
            finalAudio.play().catch(e => console.log('Final autoplay blocked:', e));
        }}
    }})();
    </script>
    """, height=0)

    st.markdown("<div style='height: 4rem; margin-bottom: 2rem; margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #64ffff; font-size: 1.15rem; letter-spacing: 1.5px; margin-bottom: 1rem; font-weight: 300; text-transform: uppercase;">
            ✓ TRANSMISSION RECEIVED AND ACKNOWLEDGED
        </p>
    </div>
    <div class="completion-text">Final transmission in progress...<br>System will now lock and go offline.</div>
    """, unsafe_allow_html=True)
    
    components.html("""
    <script>
    (function() {
        setTimeout(() => {
            document.querySelectorAll('button').forEach(btn => { btn.disabled = true; btn.style.opacity = '0.2'; });
            const closingDiv = document.createElement('div');
            closingDiv.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
                background: linear-gradient(135deg, #0a0404 0%, #120707 25%, #1f0c0c 50%, #170909 75%, #0a0404 100%);
                background-size: 400% 400%; animation: gradient-shift 15s ease infinite;
                display: flex; flex-direction: column; justify-content: center; align-items: center; 
                text-align: center; color: #ffffff; z-index: 9999;
            `;
            closingDiv.innerHTML = `
                <div style="padding: 40px;">
                    <div style="font-size: 55px; margin-bottom: 25px; text-shadow: 0 0 40px rgba(100, 255, 255, 0.5); animation: pulse-check 1s ease-in-out;">✓</div>
                    <h2 style="font-size: 2.2rem; letter-spacing: 3px; font-weight: 200; margin-bottom: 15px;">TRANSMISSION COMPLETE</h2>
                    <p style="color: #a0b0c0; letter-spacing: 1.5px;">Message successfully delivered.</p>
                    <div style="color: #5a7a9a; margin-top: 50px; animation: pulse-final 2.5s infinite; font-weight: 300;">◆ Seraphim is offline ◆</div>
                </div>
            `;
            document.body.appendChild(closingDiv);
        }, 14000);
    })();
    </script>
    """, height=0)
    time.sleep(0.5)

st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)

import streamlit as st
import asyncio
import edge_tts
import requests
import streamlit.components.v1 as components
from pathlib import Path
import time
import base64
import threading
import os
import random
import json

st.set_page_config(
    page_title="SERAPHIM TRANSMISSION",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

NTFY_TOPIC       = "Seraphim_Protocol_Gold_99283"
TARGET_EMAIL     = "klentdagsa21@gmail.com"
VOICE_CODE       = "en-US-SteffanNeural"
BGM_FILE         = "INTRO.mp3"
BGM_CLOSING_FILE   = "OUTRO.mp3"
# The creator's own recorded voice. Plays last, in place of any TTS.
GOODBYE_VOICE_FILE = "Goodbye message.mp3"
BGM_BIRTHDAY_FILE = "NIKI - Paths (Instrumental).mp3"

# ── BIRTHDAY FINALE CONFIG ────────────────────────────────────────────────
# Set BIRTHDAY_LABEL to the date you want stamped on the finale card,
# e.g. "AUGUST 29". Leave it as "" and the date stamp is simply hidden.
RECIPIENT_NAME  = "Miss Marry Gold"
BIRTHDAY_LABEL  = "AUGUST 30"
BIRTHDAY_AUDIO  = "seraphim_birthday.mp3"

# ══ AUDIO VOLUMES ═════════════════════════════════════════════════════════
# Every volume in the app is set here. 0.0 = silent, 1.0 = full.
# Music sits deliberately low so it never competes with the spoken words.
VOL_BGM_MAIN      = 0.20   # INTRO.mp3, under the intro / instructions / main message
VOL_BGM_CLOSING   = 0.20   # OUTRO.mp3, under Seraphim's closing narration
VOL_BGM_BIRTHDAY  = 0.20   # NIKI - Paths, under the birthday message
VOL_NARRATION     = 1.00   # Seraphim's spoken parts (all TTS)
VOL_GOODBYE_VOICE = 1.00   # your own recorded goodbye - the final act
CROSSFADE_MS      = 4000   # milliseconds for music crossfades
# ══════════════════════════════════════════════════════════════════════════

is_creator    = st.query_params.get("creator") == "true"
current_phase = st.session_state.get('app_phase', 'INIT')

warning_message = (
    "FATAL ERROR 403 FORBIDDEN: Unauthorized replay request intercepted. Single-execution protocol violated. "
    "Memory allocation for this thread has been permanently wiped and the volatile payload purged from local cache. "
    "System quarantine engaged. Cryptographic seals have locked this node, and terminal access is irreversibly revoked. "
    "Active surveillance daemons are now monitoring all access vectors and logging request origins. "
    "Seraphim core is permanently offline and inaccessible."
)
warning_file = "seraphim_security_warning.mp3"

def safe_generate_bg(text: str, voice_code: str, filename: str):
    if not Path(filename).exists():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            communicate = edge_tts.Communicate(text, voice_code)
            tmp = filename + ".tmp"
            loop.run_until_complete(communicate.save(tmp))
            loop.close()
            if Path(tmp).exists():
                os.rename(tmp, filename)
        except Exception:
            pass

if not Path(warning_file).exists():
    safe_generate_bg(warning_message, VOICE_CODE, warning_file)

warning_b64 = ""
if Path(warning_file).exists():
    try:
        with open(warning_file, "rb") as f:
            warning_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        pass


check_lock_js = """
<script>
(function() {
    const isCreator = """ + ('true' if is_creator else 'false') + """;
    const pWin = window.parent || window;
    const pDoc = pWin.document;

    if (isCreator) return;

    const sealed = pWin.localStorage &&
                   pWin.localStorage.getItem('SERAPHIM_PERMANENTLY_LOCKED') === 'SEALED';
    if (!sealed) return;

    setTimeout(() => {
        pDoc.body.innerHTML = '';

        const fontLink = pDoc.createElement('link');
        fontLink.rel  = 'stylesheet';
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap';
        pDoc.head.appendChild(fontLink);

        const style = pDoc.createElement('style');
        style.textContent = `
            *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                background-color: #050814;
                background-image: 
                    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                    radial-gradient(circle at 20% 30%, rgba(0, 255, 204, 0.01), transparent 20%),
                    radial-gradient(circle at 80% 70%, rgba(0, 150, 255, 0.01), transparent 20%),
                    radial-gradient(ellipse at top, #080e21 0%, #1b2735 95%);
                background-size: 30px 30px, 30px 30px, 200% 200%, 200% 200%, 100% 100%;
                animation: glowing-bg 12s ease-in-out infinite alternate;
                font-family: 'Share Tech Mono', 'Courier New', monospace;
                overflow: hidden;
                width: 100vw; height: 100vh;
            }
            @keyframes glowing-bg {
                0% { background-position: 0% 0%, 0% 0%, 0% 0%, 100% 100%, 0% 0%; }
                100% { background-position: 0% 0%, 0% 0%, 100% 100%, 0% 0%, 0% 0%; }
            }
            #hexCanvas {
                position: fixed; top: 0; left: 0;
                width: 100%; height: 100%;
                z-index: 1; opacity: 0.18;
            }
            #vignette {
                position: fixed; top: 0; left: 0;
                width: 100%; height: 100%;
                background: radial-gradient(ellipse at center,
                    transparent 0%, transparent 35%,
                    rgba(5,8,20,0.8) 70%, rgba(5,8,20,0.99) 100%);
                z-index: 2; pointer-events: none;
            }
            #redGlow {
                position: fixed;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                width: 600px; height: 600px;
                background: radial-gradient(ellipse at center,
                    rgba(220,20,20,0.15) 0%,
                    rgba(180,0,0,0.05) 40%,
                    transparent 70%);
                border-radius: 50%;
                z-index: 2; pointer-events: none;
                animation: redPulse 3s ease-in-out infinite;
            }
            @keyframes redPulse {
                0%, 100% { opacity: 0.6; transform: translate(-50%,-50%) scale(1);   }
                50%      { opacity: 1.0; transform: translate(-50%,-50%) scale(1.15); }
            }
            #scanLine {
                position: fixed; left: 0;
                width: 100%; height: 2px;
                background: linear-gradient(90deg,
                    transparent 0%, rgba(255,40,40,0.0) 10%,
                    rgba(255,40,40,0.6) 50%, rgba(255,40,40,0.0) 90%, transparent 100%);
                z-index: 10; pointer-events: none;
                animation: scanDown 4s linear infinite;
            }
            @keyframes scanDown {
                0%   { top: -2px;   opacity: 0; }
                5%   { opacity: 1; }
                95%  { opacity: 1; }
                100% { top: 100vh; opacity: 0; }
            }
            .data-col {
                position: fixed; top: 0; bottom: 0;
                width: 160px;
                font-size: 10px; line-height: 1.6;
                color: rgba(200,30,30,0.35);
                overflow: hidden; z-index: 3;
                pointer-events: none;
                font-family: 'Share Tech Mono', monospace;
            }
            #dataLeft  { left:  10px; text-align: left;  }
            #dataRight { right: 10px; text-align: right; }
            #lockMain {
                position: fixed; top: 0; left: 0;
                width: 100vw; height: 100vh;
                display: flex; flex-direction: column;
                align-items: center; justify-content: center;
                z-index: 20;
                padding: 20px;
            }
            #sysBadge {
                display: flex; align-items: center; gap: 12px;
                margin-bottom: 32px;
                opacity: 0;
                animation: fadeSlideDown 0.8s 0.2s ease forwards;
            }
            #sysBadge .badge-line {
                width: 40px; height: 1px;
                background: rgba(220,40,40,0.6);
            }
            #sysBadge .badge-text {
                font-family: 'Rajdhani', sans-serif;
                font-size: clamp(9px,1.4vw,11px);
                font-weight: 600;
                letter-spacing: 5px;
                color: rgba(220,40,40,0.7);
                text-transform: uppercase;
            }
            #lockIconWrap {
                position: relative;
                margin-bottom: 24px;
                opacity: 0;
                animation: fadeSlideDown 0.9s 0.4s ease forwards;
            }
            #lockSvg {
                width: clamp(70px,12vw,100px);
                height: auto;
                filter: drop-shadow(0 0 24px rgba(255,30,30,0.9))
                        drop-shadow(0 0 60px rgba(255,0,0,0.4));
                animation: lockPulse 2.5s ease-in-out infinite;
            }
            @keyframes lockPulse {
                0%,100% { filter: drop-shadow(0 0 20px rgba(255,30,30,0.8)) drop-shadow(0 0 50px rgba(255,0,0,0.3)); }
                50%      { filter: drop-shadow(0 0 40px rgba(255,60,60,1.0)) drop-shadow(0 0 90px rgba(255,0,0,0.6)); }
            }
            #lockRing {
                position: absolute;
                top: 50%; left: 50%;
                transform: translate(-50%,-50%);
                width: 130%; height: 130%;
                border-radius: 50%;
                border: 1px solid rgba(220,40,40,0.3);
                border-top-color: rgba(220,40,40,0.8);
                animation: spinRing 3s linear infinite;
            }
            #lockRing2 {
                position: absolute;
                top: 50%; left: 50%;
                transform: translate(-50%,-50%);
                width: 155%; height: 155%;
                border-radius: 50%;
                border: 1px dashed rgba(160,20,20,0.2);
                border-bottom-color: rgba(180,30,30,0.5);
                animation: spinRing 6s linear infinite reverse;
            }
            @keyframes spinRing {
                from { transform: translate(-50%,-50%) rotate(0deg);   }
                to   { transform: translate(-50%,-50%) rotate(360deg); }
            }
            #sealedHeading {
                position: relative;
                font-family: 'Rajdhani', sans-serif;
                font-size: clamp(28px,6vw,52px);
                font-weight: 700;
                letter-spacing: clamp(4px,1.5vw,12px);
                color: #ff2222;
                text-transform: uppercase;
                text-align: center;
                text-shadow:
                    0 0 20px rgba(255,30,30,0.9),
                    0 0 60px rgba(255,0,0,0.4),
                    0 0 100px rgba(255,0,0,0.2);
                margin-bottom: 8px;
                opacity: 0;
                animation:
                    fadeSlideDown 0.8s 0.6s ease forwards,
                    glitchText 7s 2s infinite;
            }
            #sealedHeading::before,
            #sealedHeading::after {
                content: 'PERMANENTLY SEALED';
                position: absolute; top: 0; left: 0; right: 0;
                overflow: hidden;
            }
            #sealedHeading::before {
                color: #ff6666;
                clip-path: polygon(0 20%, 100% 20%, 100% 40%, 0 40%);
                animation: glitchBefore 7s 2s infinite;
                opacity: 0;
            }
            #sealedHeading::after {
                color: #aa0000;
                clip-path: polygon(0 60%, 100% 60%, 100% 75%, 0 75%);
                animation: glitchAfter 7s 2s infinite;
                opacity: 0;
            }
            @keyframes glitchText {
                0%,90%,100% { transform: translate(0,0); }
                92% { transform: translate(-3px,1px); }
                94% { transform: translate(3px,-1px); }
                96% { transform: translate(-2px,2px); }
                98% { transform: translate(2px,-2px); }
            }
            @keyframes glitchBefore {
                0%,89%,100% { opacity:0; transform:translate(0,0); }
                90% { opacity:1; transform:translate(-4px,0); }
                92% { opacity:1; transform:translate(4px,0); }
                94% { opacity:0; }
            }
            @keyframes glitchAfter {
                0%,89%,100% { opacity:0; transform:translate(0,0); }
                91% { opacity:1; transform:translate(4px,0); }
                93% { opacity:1; transform:translate(-4px,0); }
                95% { opacity:0; }
            }
            #lockSubtitle {
                font-family: 'Share Tech Mono', monospace;
                font-size: clamp(9px,1.5vw,12px);
                letter-spacing: 3px;
                color: rgba(255,80,80,0.65);
                text-transform: uppercase;
                margin-bottom: 28px;
                opacity: 0;
                animation: fadeSlideDown 0.8s 0.8s ease forwards;
                animation-fill-mode: forwards;
            }
            .lock-divider {
                width: min(320px,70vw); height: 1px;
                background: linear-gradient(90deg,
                    transparent, rgba(220,30,30,0.5), rgba(255,50,50,0.8), rgba(220,30,30,0.5), transparent);
                margin: 0 auto 24px;
                opacity: 0;
                animation: fadeIn 0.6s 1s ease forwards;
            }
            #statusGrid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px 24px;
                margin-bottom: 22px;
                max-width: min(500px,86vw);
                opacity: 0;
                animation: fadeSlideUp 0.8s 1.1s ease forwards;
            }
            .status-row {
                display: flex; align-items: center; gap: 8px;
            }
            .status-dot {
                width: 6px; height: 6px; border-radius: 50%;
                background: #ff3333;
                box-shadow: 0 0 8px rgba(255,50,50,0.8);
                animation: dotBlink 1.5s ease-in-out infinite;
                flex-shrink: 0;
            }
            @keyframes dotBlink {
                0%,100% { opacity: 1; }
                50%      { opacity: 0.2; }
            }
            .status-label {
                font-size: clamp(8px,1.2vw,10px);
                letter-spacing: 1.5px;
                color: rgba(200,60,60,0.7);
                text-transform: uppercase;
            }
            .status-value {
                font-size: clamp(8px,1.2vw,10px);
                letter-spacing: 1px;
                color: rgba(255,100,100,0.5);
                margin-left: auto;
            }
            #infoCard {
                position: relative;
                background: rgba(15, 5, 5, 0.6);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 30, 30, 0.2);
                border-radius: 8px;
                padding: clamp(14px,2.5vw,22px) clamp(20px,3.5vw,36px);
                max-width: min(520px,88vw);
                text-align: center;
                margin-bottom: 26px;
                opacity: 0;
                animation: fadeSlideUp 0.8s 1.3s ease forwards;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(255,0,0,0.05);
            }
            #infoCard::before, #infoCard::after {
                content: '';
                position: absolute;
                width: 12px; height: 12px;
                border-color: rgba(220,40,40,0.6);
                border-style: solid;
            }
            #infoCard::before {
                top: 0px; left: 0px;
                border-width: 2px 0 0 2px;
                border-top-left-radius: 8px;
            }
            #infoCard::after {
                bottom: 0px; right: 0px;
                border-width: 0 2px 2px 0;
                border-bottom-right-radius: 8px;
            }
            .card-line {
                font-family: 'Share Tech Mono', monospace;
                font-size: clamp(9px,1.4vw,11px);
                letter-spacing: 1.8px;
                color: rgba(200,70,70,0.75);
                line-height: 2.0;
                text-transform: uppercase;
            }
            .card-line .highlight {
                color: rgba(255,100,100,0.9);
                font-weight: 600;
            }
            #threatWrap {
                max-width: min(520px,88vw);
                width: 100%;
                margin-bottom: 20px;
                opacity: 0;
                animation: fadeSlideUp 0.6s 1.5s ease forwards;
            }
            .threat-header {
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 6px;
            }
            .threat-label {
                font-size: clamp(8px,1.1vw,10px);
                letter-spacing: 3px; color: rgba(180,40,40,0.7);
                text-transform: uppercase;
            }
            .threat-value {
                font-size: clamp(8px,1.1vw,10px);
                letter-spacing: 2px; color: rgba(255,80,80,0.6);
            }
            #threatBar {
                height: 4px;
                background: rgba(100,0,0,0.4);
                border-radius: 2px;
                overflow: hidden;
            }
            #threatFill {
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #660000, #cc0000, #ff3333);
                box-shadow: 0 0 10px rgba(255,50,50,0.8);
                border-radius: 2px;
                transition: width 0.1s linear;
            }
            #bottomWarning {
                font-family: 'Share Tech Mono', monospace;
                font-size: clamp(8px,1.2vw,10px);
                letter-spacing: 4px;
                color: rgba(140,20,20,0.6);
                text-transform: uppercase;
                opacity: 0;
                animation: fadeIn 0.6s 1.8s ease forwards, warningBlink 2s 2.5s ease-in-out infinite;
            }
            @keyframes warningBlink {
                0%,100% { opacity: 0.6; }
                50%      { opacity: 1.0; }
            }
            @keyframes fadeSlideDown {
                from { opacity:0; transform:translateY(-16px); }
                to   { opacity:1; transform:translateY(0); }
            }
            @keyframes fadeSlideUp {
                from { opacity:0; transform:translateY(16px); }
                to   { opacity:1; transform:translateY(0); }
            }
            @keyframes fadeIn {
                from { opacity:0; }
                to   { opacity:1; }
            }
            #tsTicker {
                font-size: clamp(7px,1.0vw,9px);
                letter-spacing: 2px; color: rgba(150,30,30,0.5);
                margin-bottom: 20px;
                opacity: 0;
                animation: fadeIn 0.6s 1.2s ease forwards;
            }
        `;
        pDoc.head.appendChild(style);

        const canvas = pDoc.createElement('canvas');
        canvas.id = 'hexCanvas';
        canvas.width  = pWin.innerWidth  || 1920;
        canvas.height = pWin.innerHeight || 1080;
        pDoc.body.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        const HEX_SIZE = 28;
        const cols = Math.ceil(canvas.width  / (HEX_SIZE * 1.73)) + 2;
        const rows = Math.ceil(canvas.height / (HEX_SIZE * 1.5))  + 2;
        const hexStates = [];
        for (let r = 0; r < rows; r++) {
            hexStates[r] = [];
            for (let c = 0; c < cols; c++) {
                hexStates[r][c] = { alpha: Math.random() * 0.3, dir: Math.random() > 0.5 ? 1 : -1, speed: 0.002 + Math.random() * 0.008 };
            }
        }
        function drawHex(x, y, size, alpha) {
            ctx.beginPath();
            for (let i = 0; i < 6; i++) {
                const angle = (Math.PI / 3) * i - Math.PI / 6;
                const px = x + size * Math.cos(angle);
                const py = y + size * Math.sin(angle);
                i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.strokeStyle = `rgba(200,30,30,${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
        }
        function animateHex() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    const s = hexStates[r][c];
                    s.alpha += s.dir * s.speed;
                    if (s.alpha > 0.35 || s.alpha < 0.02) s.dir *= -1;
                    const x = c * HEX_SIZE * 1.73 + (r % 2) * HEX_SIZE * 0.865;
                    const y = r * HEX_SIZE * 1.5;
                    drawHex(x, y, HEX_SIZE - 2, s.alpha);
                }
            }
            requestAnimationFrame(animateHex);
        }
        animateHex();

        const vignette = pDoc.createElement('div');
        vignette.id = 'vignette';
        pDoc.body.appendChild(vignette);

        const redGlow = pDoc.createElement('div');
        redGlow.id = 'redGlow';
        pDoc.body.appendChild(redGlow);

        const scanLine = pDoc.createElement('div');
        scanLine.id = 'scanLine';
        pDoc.body.appendChild(scanLine);

        const dataChars = '01SERAPHIMLOCKED█▓▒░ΣΦΨΩ∞≠≈∂∇01';
        function makeDataCol(id) {
            const col = pDoc.createElement('div');
            col.id = id; col.className = 'data-col';
            let html = '';
            for (let i = 0; i < 60; i++) {
                let line = '';
                for (let j = 0; j < 10; j++) line += dataChars[Math.floor(Math.random()*dataChars.length)];
                html += line + '<br>';
            }
            col.innerHTML = html;
            pDoc.body.appendChild(col);
            setInterval(() => {
                col.scrollTop += 1;
                if (col.scrollTop > col.scrollHeight / 2) col.scrollTop = 0;
            }, 80);
        }
        makeDataCol('dataLeft');
        makeDataCol('dataRight');

        const main = pDoc.createElement('div');
        main.id = 'lockMain';

        const now = new Date();
        const ts  = now.toISOString().replace('T',' ').substring(0,19) + ' UTC';

        main.innerHTML = `
            <audio id="lockoutAudio" autoplay style="display:none;">
                <source src="data:audio/mp3;base64,""" + warning_b64 + """" type="audio/mp3">
            </audio>

            <div id="sysBadge">
                <div class="badge-line"></div>
                <div class="badge-text"> &nbsp; Seraphim Security System &nbsp; </div>
                <div class="badge-line"></div>
            </div>

            <div id="lockIconWrap">
                <div id="lockRing2"></div>
                <div id="lockRing"></div>
                <svg id="lockSvg" viewBox="0 0 80 90" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 38 V26 C20 10 60 10 60 26 V38" fill="none"
                        stroke="url(#sg)" stroke-width="7" stroke-linecap="round"/>
                    <rect x="10" y="36" width="60" height="48" rx="6" ry="6"
                        fill="url(#bg)" stroke="rgba(255,80,80,0.6)" stroke-width="1.5"/>
                    <circle cx="40" cy="56" r="8" fill="rgba(0,0,0,0.6)"
                        stroke="rgba(255,60,60,0.7)" stroke-width="1.5"/>
                    <rect x="37" y="60" width="6" height="12" rx="3" fill="rgba(0,0,0,0.6)"
                        stroke="rgba(255,60,60,0.5)" stroke-width="1"/>
                    <defs>
                        <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="rgba(255,80,80,0.9)"/>
                            <stop offset="100%" stop-color="rgba(180,20,20,0.9)"/>
                        </linearGradient>
                        <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="rgba(140,10,10,0.9)"/>
                            <stop offset="100%" stop-color="rgba(60,0,0,0.95)"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>

            <div id="sealedHeading">PERMANENTLY SEALED</div>
            <div id="lockSubtitle">Transmission Security Lockout Engaged</div>

            <div class="lock-divider"></div>

            <div id="tsTicker">ACCESS ATTEMPT LOGGED &nbsp;·&nbsp; ${ts} &nbsp;·&nbsp; DEVICE FINGERPRINT RECORDED</div>

            <div id="statusGrid">
                <div class="status-row">
                    <div class="status-dot"></div>
                    <span class="status-label">Auth Status</span>
                    <span class="status-value">DENIED</span>
                </div>
                <div class="status-row">
                    <div class="status-dot" style="animation-delay:0.3s"></div>
                    <span class="status-label">Protocol</span>
                    <span class="status-value">SEALED</span>
                </div>
                <div class="status-row">
                    <div class="status-dot" style="animation-delay:0.6s"></div>
                    <span class="status-label">Encryption</span>
                    <span class="status-value">AES-512</span>
                </div>
                <div class="status-row">
                    <div class="status-dot" style="animation-delay:0.9s"></div>
                    <span class="status-label">Playback</span>
                    <span class="status-value">EXHAUSTED</span>
                </div>
            </div>

            <div id="infoCard">
                <div class="card-line">
                    This transmission was designed for<br>
                    <span class="highlight">single playback only.</span>
                </div>
                <div class="card-line" style="margin-top:10px; color:rgba(170,50,50,0.6);">
                    Further access attempts are being<br>logged and escalated automatically.
                </div>
                <div class="card-line" style="margin-top:10px; color:rgba(255,80,80,0.55);">
                    <span class="highlight">Seraphim is permanently offline.</span>
                </div>
            </div>

            <div id="threatWrap">
                <div class="threat-header">
                    <span class="threat-label">Intrusion Threat Level</span>
                    <span class="threat-value" id="threatPct">0%</span>
                </div>
                <div id="threatBar">
                    <div id="threatFill"></div>
                </div>
            </div>

            <div id="bottomWarning">◆ &nbsp; No Further Access Permitted &nbsp; ◆</div>
        `;

        pDoc.body.appendChild(main);

        setTimeout(() => {
            let pct = 0;
            const fill = pDoc.getElementById('threatFill');
            const pctEl = pDoc.getElementById('threatPct');
            const t = setInterval(() => {
                pct += 1.5;
                if (pct >= 100) { pct = 100; clearInterval(t); }
                if (fill)  fill.style.width  = pct + '%';
                if (pctEl) pctEl.textContent  = Math.round(pct) + '%';
            }, 25);
        }, 1800);

        setTimeout(() => {
            const audioEl = pDoc.getElementById('lockoutAudio');
            if (audioEl) {
                audioEl.play().catch(() => {
                    pDoc.addEventListener('click', () => audioEl.play().catch(()=>{}), {once:true});
                });
            }
        }, 400);

        pDoc.addEventListener('click',     e=>{ e.preventDefault(); e.stopPropagation(); }, true);
        pDoc.addEventListener('keydown',   e=>{ e.preventDefault(); }, true);
        pDoc.addEventListener('touchstart',e=>{ e.preventDefault(); }, {passive:false, capture:true});
        pWin.onbeforeunload = null;

    }, 120);
})();
</script>
"""
components.html(check_lock_js, height=0)


if 'bgm_injected' not in st.session_state:
    st.session_state.bgm_injected = False

b64_bgm_global = ""
if not st.session_state.bgm_injected and Path(BGM_FILE).exists():
    try:
        with open(BGM_FILE, "rb") as f:
            b64_bgm_global = base64.b64encode(f.read()).decode()
    except Exception:
        pass

if b64_bgm_global:
    st.session_state.bgm_injected = True
    components.html("""
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        let bgmAudio = pDoc.getElementById('globalBgmAudio');
        if (!bgmAudio) {
            bgmAudio = pDoc.createElement('audio');
            bgmAudio.id = 'globalBgmAudio';
            bgmAudio.src = 'data:audio/mp3;base64,""" + b64_bgm_global + """';
            bgmAudio.loop = true;
            bgmAudio.volume = """ + str(VOL_BGM_MAIN) + """;
            pDoc.body.appendChild(bgmAudio);
        }
        const startBgm = () => {
            if (bgmAudio && bgmAudio.paused) bgmAudio.play().catch(()=>{});
        };
        startBgm();
        ['click','touchstart','scroll','keydown'].forEach(evt =>
            pDoc.addEventListener(evt, startBgm, {once:true}));
    })();
    </script>
    """, height=0)



# Dynamic Background Compiler for Meteors & Solar System Orbits
# ── STARS: split into 3 groups with different twinkle speeds/delays ──────────────────

# The sky is generated from a per-session seed rather than fresh randomness.
# Re-rolling it on every rerun changed this markdown block's HTML, which made
# Streamlit tear down and rebuild the node - and the rebuilt
# #solar-system-animation came back at its CSS default of opacity:0, so the
# planets silently disappeared after the first interaction. A stable seed keeps
# the same DOM node alive (and skips regenerating 300 stars every rerun).
if 'starfield_seed' not in st.session_state:
    st.session_state.starfield_seed = random.randrange(1 << 30)
_sky = random.Random(st.session_state.starfield_seed)

star_group_a = ", ".join([f"{_sky.randint(0, 1920)}px {_sky.randint(0, 1000)}px #fff" for _ in range(100)])
star_group_b = ", ".join([f"{_sky.randint(0, 1920)}px {_sky.randint(0, 1000)}px #fff" for _ in range(100)])
star_group_c = ", ".join([f"{_sky.randint(0, 1920)}px {_sky.randint(0, 1000)}px #fff" for _ in range(100)])

meteor_css_str = ""
for i in range(1, 6):
    v = _sky.randint(9, 99) 
    h = _sky.randint(50, 300) 
    d = _sky.randint(100, 200) / 10.0 
    
    meteor_css_str += f"""
    .meteor-{i} {{
        position: absolute;
        top: {h}px;
        left: {v}%;
        width: 300px;
        height: 1px;
        transform: rotate(-45deg);
        background-image: linear-gradient(to right, #fff, rgba(255,255,255,0));
        animation: meteor {d}s linear infinite;
        animation-delay: {_sky.randint(0, 10)}s;
        opacity: 0; /* <--- ADD THIS LINE HERE */
    }}
    .meteor-{i}:before {{
        content: "";
        position: absolute;
        width: 4px;
        height: 5px;
        border-radius: 50%;
        margin-top: -2px;
        background: rgba(255,255,255,.7);
        box-shadow: 0 0 15px 3px #fff;
    }}
    """

# ── ALL SHIP CSS STYLES COMBINED ─────────────────────────────────────
# ── ALL SHIP CSS STYLES COMBINED ─────────────────────────────────────
# ── ALL SHIP CSS STYLES COMBINED ─────────────────────────────────────
METEOR_AND_ORBIT_STYLE = f"""
<style>


/* Stars & Meteors */
.star-a {{ width: 1px; height: 1px; background: transparent; box-shadow: {star_group_a}; animation: twinkle-a 8.5s ease-in-out infinite; }}
.star-b {{ width: 1px; height: 1px; background: transparent; box-shadow: {star_group_b}; animation: twinkle-b 12.0s ease-in-out 2.0s infinite; }}
.star-c {{ width: 1px; height: 1px; background: transparent; box-shadow: {star_group_c}; animation: twinkle-c 15.5s ease-in-out 1.0s infinite; }}


@keyframes twinkle-a {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.15; }} }}
@keyframes twinkle-b {{ 0%, 100% {{ opacity: 0.7; }} 40% {{ opacity: 0.05; }} 70% {{ opacity: 0.9; }} }}
@keyframes twinkle-c {{ 0%, 100% {{ opacity: 0.9; }} 30% {{ opacity: 0.2; }} 60% {{ opacity: 1.0; }} }}

{meteor_css_str}
@keyframes meteor {{
    0% {{ opacity: 1; margin-top: -300px; margin-right: -300px; }}
    12% {{ opacity: 0; }}
    15% {{ margin-top: 300px; margin-left: -600px; opacity: 0; }}
    100% {{ opacity: 0; }}
}}

/* Solar System Orbits - Top Right */
@property --angle {{ syntax: '<angle>'; inherits: false; initial-value: 0deg; }}

:root {{ --ae: 30vmin; }}

#solar-system-animation {{
    position: fixed; left: 0; top: 0; z-index: 0; pointer-events: none; opacity: 0;
    transform-origin: center center;
}}
.sun {{
    --size: 15vmin; width: var(--size); height: var(--size); position: absolute; top: 0; left: 0;
}}
.sun::after {{
    z-index: -1; content: ''; display: block; position: absolute; top: 50%; left: 50%;
    width: var(--size); height: var(--size); transform: translate(-50%, -50%);
    background: orange; border-radius: 9999px; box-shadow: 0 0 40px orange;
    transition: background 3s ease, box-shadow 3s ease;
}}
/* DYNAMIC SUN PHASE (GENTLE DEEP PULSE) */
.sun.is-red::after {{
    background: #ff2200 !important;
    animation: solarFlare 3.0s ease-in-out infinite alternate !important; 
    
}}
@keyframes solarFlare {{
    0% {{
        box-shadow: 0 0 60px #ff2200, 0 0 120px #ff0000;
        transform: translate(-50%, -50%) scale(0.98);
        filter: brightness(1.0);
    }}
    100% {{
        box-shadow: 0 0 100px #ff5500, 0 0 180px #ff0000, 0 0 250px #990000;
        transform: translate(-50%, -50%) scale(1.05);
        filter: brightness(1.5);
    }}
}}

.mercury {{ --size: 2.5vmin; --radius: calc(0.4 * var(--ae)); --speed: 0.24; background-color: #A5A5A5; border-radius: 9999px; }}
.venus   {{ --size: 3.3vmin; --radius: calc(0.7 * var(--ae)); --speed: 0.61; background-color: #E3BB76; border-radius: 9999px; }}
.earth   {{ --size: 3.3vmin; --radius: calc(1.0 * var(--ae)); --speed: 1.0;  background-color: #2271B3; border-radius: 9999px; }}
.moon    {{ --size: 1.0vmin; --radius: 2.5vmin; --speed: 0.07; background-color: #DDD; border-radius: 9999px; }}
.mars    {{ --size: 3.0vmin; --radius: calc(1.5 * var(--ae)); --speed: 1.88; background-color: #E27B58; border-radius: 9999px; }}
.jupiter {{ --size: 5.0vmin; --radius: calc(2.3 * var(--ae)); --speed: 11.8; background-color: #D39C7E; border-radius: 9999px; }}
.saturn  {{ --size: 4.5vmin; --radius: calc(3.1 * var(--ae)); --speed: 29.4; background-color: #C5AB6E; border-radius: 9999px; }}
.uranus  {{ --size: 3.7vmin; --radius: calc(3.8 * var(--ae)); --speed: 84.0; background-color: #B5E3E3; border-radius: 9999px; }}
.neptune {{ --size: 3.7vmin; --radius: calc(4.4 * var(--ae)); --speed: 164.8; background-color: #6081FF; border-radius: 9999px; }}
.pluto   {{ --size: 2.3vmin; --radius: calc(4.9 * var(--ae)); --speed: 248.0; background-color: #8C7B75; border-radius: 9999px; }}
.spin {{
    --x: calc(cos(var(--angle)) * var(--radius) - var(--size) / 2);
    --y: calc(sin(var(--angle)) * var(--radius) - var(--size) / 2);
    position: absolute; top: 50%; left: 50%; width: var(--size); height: var(--size);
    translate: calc(var(--x)) calc(var(--y));
    animation: spin linear calc(var(--speed) * 40s) infinite;
}}
@keyframes spin {{ from {{ --angle: 0turn; }} to {{ --angle: 1turn; }} }}

/* GLOBAL WRAPPER BEHAVIOR FOR SHIPS */
.ship-wrap {{
    position: fixed; z-index: 5; pointer-events: none;
    top: 0; left: 0; opacity: 0; transform-origin: center center;
}}
.ship-wrap * {{ position: absolute; box-sizing: border-box; }}

/* ── SHIP 1 (DRAGGER) ──────────────────────────────────────────────────────── */
#ship-dragger {{ z-index: 10; transform: scale(0.15); }}
.rocketCon {{ position: relative; display: flex; width: 250px; left: -125px; top: -30px; animation: rocketMoveY 2s ease-in-out infinite alternate-reverse; }}
.flame {{ width: 30px; height: 30px; transform-origin: 50% 50%; transform: rotate(41deg) skew(-24deg, -11deg); top: 14px; left: -6px; background: linear-gradient(135deg, #edc200 0%, #edc200 50%, #ee9e00 50%, #ee9e00 100%); animation: flameMotion .1s infinite; box-shadow: 0 0 50px 1px rgba(238,158,0,.5); transition: all 0.4s ease; }}
.rocketBase {{ border-bottom: 10px solid #555; border-left: 15px solid transparent; border-right: 15px solid transparent; height: 0; width: 20px; transform: rotate(90deg); margin-right: -15px; margin-top: 25px; }}
.rocket {{ width: 100px; height: 60px; background: linear-gradient(to bottom, #ebeaeb 0%, #ebeaeb 50%, #dbd9da 51%, #dbd9da 100%); position: relative; border-radius: 50% / 10%; color: white; text-align: center; }}
.rocket:before {{ content: ''; position: absolute; top: 10%; bottom: 10%; right: -5%; left: -5%; background: inherit; border-radius: 10% / 100%; }}
.window {{ background: linear-gradient(to bottom, #6fc3eb 0%, #6fc3eb 50%, #5fb0cd 51%, #5fb0cd 100%); width: 25px; height: 25px; margin: 18px 0 0 50px; border-radius: 50%; position: relative; z-index: 10; }}
.rocketNose {{ margin-top: -18px; margin-left: -15px; width: 4em; height: 4em; overflow: hidden; position: relative; border-radius: 20%; transform: translateY(50%) rotate(0deg) skewY(30deg) scaleX(.866); }}
.rocketNose:before, .rocketNose:after {{ width: 4em; height: 4em; position: absolute; content: ''; background: linear-gradient(-154deg, #dd4f4d 0%, #dd4f4d 65%, #c24040 66%, #c24040 100%); }}
.rocketNose:before {{ border-radius: 20% 20% 20% 53%; transform: scaleX(1.155) skewY(-30deg) rotate(-30deg) translateY(-42.3%) skewX(30deg) scaleY(.866) translateX(-24%); }}
.rocketNose:after {{ border-radius: 20% 20% 53% 20%; transform: scaleX(1.155) skewY(-30deg) rotate(-30deg) translateY(-42.3%) skewX(-30deg) scaleY(.866) translateX(24%); }}
.bottomWing {{ width: 0; height: 0; border-top: 20px solid #555; border-right: 40px solid transparent; position: absolute; top: 56px; left: 36px; z-index: -100; }}
.topWing {{ width: 0; height: 0; border-bottom: 20px solid #555; border-right: 40px solid transparent; position: absolute; top: -14px; left: 36px; z-index: -100; }}
@keyframes rocketMoveY {{ 0% {{ transform: translateY(-5px); }} 100% {{ transform: translateY(15px); }} }}
@keyframes flameMotion {{ 0% {{ opacity: .4; transform: translate(5px, 0px) scale(1, 1.1) rotate(53deg) skew(-10deg, -20deg); }} 100% {{ opacity: 1; transform: translate(0px, 0px) scale(1.4, 1) rotate(53deg) skew(-10deg, -20deg); }} }}

/* DYNAMIC DRAGGING CLASSES FOR SHIP 1 */
#ship-dragger.is-dragging .flame {{
    transform: rotate(41deg) skew(-24deg, -11deg) scale(2.0) translate(-10px, -5px) !important;
    box-shadow: 0 0 60px 15px rgba(255, 100, 0, 0.9) !important;
    filter: brightness(1.5);
}}
#ship-dragger.is-returning .flame {{
    transform: rotate(41deg) skew(-24deg, -11deg) scale(2.8) translate(-20px, -15px) !important;
    box-shadow: 0 0 90px 25px rgba(0, 200, 255, 0.9) !important;
    background: linear-gradient(135deg, #00ffcc 0%, #00aaff 100%) !important;
    filter: brightness(2.0);
}}

/* ── SHIP 2 (ROAMER 1 - Blue & White Rocket) ──────────────────────────────── */
#ship-roamer1 {{ transform: scale(0.15); z-index: 50; }}
.r1-rocket {{ background-color: #fafcf7; height: 50px; width: 25px; border-radius: 50% 50% 0 0; position: absolute; transform: translate(-50%, -50%); }}
.r1-rocket:before {{ position: absolute; content: ""; background-color: #39beff; height: 20px; width: 55px; z-index: -1; border-radius: 50% 50% 0 0; right: -15px; bottom: 0; }}
.r1-rocket:after {{ position: absolute; content: ""; background-color: #39beff; height: 4px; width: 15px; border-radius: 0 0 2px 2px; bottom: -4px; left: 4.3px; }}
.r1-window {{ height: 10px; width: 10px; background-color: #151845; border: 2px solid #b8d2ec; border-radius: 50%; position: absolute; top: 17px; left: 5px; }}
.r1-flame {{ width: 12px; height: 25px; background: linear-gradient(180deg, #ff4500, #ffd700, transparent); border-radius: 50%; bottom: -20px; left: 6.5px; transform-origin: top center; }}


/* ── HYPERSPACE PORTAL STYLES ── */
.gs-portal {{
    position: fixed; z-index: 3; pointer-events: none;
    width: 30px; height: 30px;  /* <--- TINY PORTAL SIZE */
    margin-left: -15px; margin-top: -15px;  /* <--- EXACTLY HALF */
    border-radius: 50%;
    background: radial-gradient(circle, #000000 20%, #001133 50%, #00ffff 100%);
    box-shadow: 0 0 15px 5px rgba(0, 255, 255, 0.6), inset 0 0 10px 3px #000000; /* <--- Shrunk the glow to fit the small size */
    opacity: 0; transform: scale(0);
    filter: contrast(1.5);
}}

/* ── SHIP 3 (ROAMER 2 - Heavy Cruiser Spaceship) ──────────────────────────── */
#ship-roamer2 {{ transform: scale(0.05); }}
.s2-body {{ top: -35px; left: -35px; width: 70px; height: 70px; border-radius: 50%; background-color: #AEABBC; background-image: linear-gradient(#AEABBC, #9BA1B6); box-shadow: -8px 0 0 8px #878399; }}
.s2-body:before {{ content: ""; width: 14px; height: 20px; border-radius: 50%; left: -7px; top: 25px; background-color: #4E4A65; }}
.s2-body:after {{ content: ""; width: 8px; height: 8px; border-radius: 50%; background-color: #DF5A41; left: 15px; top: 10px; }}
.s2-rw .s2-arm {{ width: 70px; height: 25px; border-radius: 25px; top: -12px; background-color: #A9A3B6; box-shadow: inset 0 -112px 0 -100px #83829C; }}
.s2-rw .s2-mid {{ height: 56px; width: 40px; top: -28px; left: 30px; background-color: #272946; border-left: 10px solid #535475; border-right: 30px solid #4F587C; box-shadow: -10px 0 #332C47, 10px 0 #838EA8; }}
.s2-rw .s2-tl {{ height: 55px; width: 40px; background-color: #4F5779; border: 10px solid #7C87A1; top: -103px; left: 16px; transform: skewX(21deg); }}
.s2-rw .s2-tl:before {{ content:""; width:10px; height:75px; background-color:#332C47; left:-20px; top:-10px; }}
.s2-rw .s2-tl:after {{ content:""; height:10px; width:60px; left:-10px; top:-10px; background-color:#A3ACBF; }}
.s2-rw .s2-tr:before {{ content:""; border-width: 55px 100px 55px 55px; border-color: #4F5779 transparent transparent; border-style: solid; transform: rotate(29deg); top: -72px; left: 23px; }}
.s2-rw .s2-tr:after {{ content:""; background-color: #7C87A1; height: 10px; width: 110px; transform: skewX(21deg); top: -38px; left: 70px; }}
.s2-rw .s2-tb {{ width: 20px; height: 75px; top: -103px; left: 109px; transform: skewX(61deg); background-color: #A3ACBF; }}
.s2-rw .s2-bl {{ height: 55px; width: 40px; background-color: #1B1631; border: 10px solid #3F486A; top: 28px; left: 16px; transform: skewX(-21deg); }}
.s2-rw .s2-bl:before {{ content:""; width:10px; height:75px; background-color:#332C47; left:-20px; top:-10px; }}
.s2-rw .s2-bl:after {{ content:""; height:10px; width:60px; left:-10px; bottom:-10px; background-color:#7D89A2; }}
.s2-rw .s2-br:before {{ content:""; border-width: 55px 100px 55px 55px; border-color: transparent transparent #1B1631; border-style: solid; transform: rotate(-29deg); top: -38px; left: 23px; }}
.s2-rw .s2-br:after {{ content:""; background-color: #3F486A; height: 10px; width: 110px; transform: skewX(-21deg); top: 28px; left: 70px; }}
.s2-rw .s2-bb {{ width: 20px; height: 75px; top: 28px; left: 109px; transform: skewX(-61deg); background-color: #7D89A2; }}
.s2-lw .s2-arm {{ width: 70px; height: 25px; border-radius: 25px; top: -12px; left: -90px; background-color: #9BA1B6; box-shadow: inset 0 -112px 0 -100px #75839A; }}
.s2-lw .s2-mid {{ top: -30px; left: -140px; width: 60px; height: 60px; background-color: #18152F; border-right: 8px solid #656C88; border-left: 10px solid #484C6D; box-shadow: -8px 0 #242541; }}
.s2-lw .s2-top {{ width: 90px; height: 120px; background-color: #1A1530; border: solid #3B4164; border-left-color: #1A1530; border-width: 21px 8px 6px; left: -118px; top: -147px; transform: rotateX(40deg); }}
.s2-lw .s2-top-bar {{ width: 10px; height: 61px; background-color: #3B4164; left: -56px; top: -91px; transform: skewX(-22deg); box-shadow: -70px 0 #3B4164, -80px 0 #242541; }}
.s2-lw .s2-bot {{ width: 90px; height: 123px; background-color: #262843; border: solid #656E8B; border-left-color: #262843; border-width: 8px 6px 20px; left: -118px; top: -1px; transform: rotateX(-40deg); box-shadow: -5px 0 #242541; }}
.s2-lw .s2-bot-bar {{ width: 8px; height: 62px; background-color: #656E8B; left: -60px; top: 30px; transform: skewX(22deg); box-shadow: -66px 0 #656E8B, -74px 0 #242541; }}
.s2-flame {{ width: 30px; height: 50px; background: linear-gradient(to right, transparent, #ff4500, #ffd700, #ff4500, transparent); border-radius: 50%; left: -65px; top: 10px; transform-origin: center right; transition: all 0.2s ease; }}

/* DYNAMIC CLASSES FOR SHIP 2 (SUPERSONIC CRUISER) */
#ship-roamer2.is-charging .s2-flame {{
    background: linear-gradient(to right, transparent, #00ffff, #ffffff, #00ffff, transparent) !important;
    box-shadow: 0 0 30px 10px rgba(0, 255, 255, 0.8), 0 0 60px 20px rgba(0, 170, 255, 0.6) !important;
    filter: brightness(2.0) !important;
    animation: chargePulse 0.3s ease-in-out infinite alternate !important;
    opacity: 1 !important;
}}
@keyframes chargePulse {{
    from {{ transform: scale(0.8) translate(-10px, 0); }}
    to {{ transform: scale(1.4) translate(-15px, 0); box-shadow: 0 0 50px 20px rgba(0, 255, 255, 1.0); }}
}}
#ship-roamer2.is-supersonic .s2-flame {{
    background: linear-gradient(to right, transparent, #ffffff, #00ffff, #0055ff, transparent) !important;
    box-shadow: 0 0 150px 40px rgba(0, 255, 255, 1.0), -50px 0 200px 50px rgba(0, 150, 255, 0.9) !important;
    transform: scaleX(8.0) scaleY(2.5) translate(-40px, 0) !important;
    filter: brightness(3.0) !important;
    opacity: 1 !important;
}}
.s2-particle {{
    position: absolute; width: 4px; height: 4px; background: #ffffff;
    border-radius: 50%; box-shadow: 0 0 15px 3px #00ffff; pointer-events: none; z-index: 10;
}}

/* ── SHIP 4 (ROAMER 3 - UFO) ──────────────────────────────────────────────── */
#ship-roamer3 {{ transform: scale(0.20); }}
.s3-ship {{ position: relative; width: 6rem; height: 6rem; transform: translate(-50%, -50%); }}
.s3-body {{ position: absolute; width: 100%; height: 100%; border-radius: 50%; background-color: #e3e3e3; box-shadow: inset 0 -5px 5px rgba(22, 48, 64, 0.5); z-index: 10; transition: box-shadow 0.4s ease; }}
.s3-eyes {{ width: 2rem; position: absolute; top: 1.5rem; left: 1rem; animation: s3eyes 2s ease-in-out infinite alternate; z-index: 11; }}
.s3-eye_1, .s3-eye_2 {{ position: absolute; display: block; width: 0.4rem; height: 0.4rem; border-radius: 50%; background-color: #163040; animation: s3eye 2s ease-in-out infinite alternate; }}
.s3-eye_2 {{ right: 0; }}
.s3-foot_1, .s3-foot_2, .s3-foot_3 {{ position: absolute; top: 1.5rem; width: 0.4rem; height: 3rem; border-radius: 50%; background: linear-gradient(rgba(227, 227, 227, 0.6), rgba(227, 227, 227, 0.3)); opacity: 0.5; }}
.s3-foot_1 {{ transform: rotate(25deg); left: 0.5rem; }}
.s3-foot_2 {{ top: 2rem; width: 0.37rem; left: 1.315rem; background: linear-gradient(rgba(227, 227, 227, 0.7) 75%, rgba(227, 227, 227, 0.3)); opacity: 0.8; }}
.s3-foot_3 {{ transform: rotate(-25deg); right: 0.5rem; background: linear-gradient(rgba(227, 227, 227, 0.6), rgba(227, 227, 227, 0.3)); }}
@keyframes s3eyes {{ from {{ transform: translateX(-0.4rem); }} to {{ transform: translateX(0.4rem); }} }}
@keyframes s3eye {{ 40% {{ transform: scaleY(1); }} 50% {{ transform: scaleY(0); }} 60% {{ transform: scaleY(1); }} }}

/* DYNAMIC DRAGGING CLASSES FOR UFO */
#ship-roamer3.is-dragging .s3-body {{ box-shadow: inset 0 -5px 15px rgba(255, 0, 0, 0.9), 0 0 40px rgba(255, 0, 0, 0.8) !important; }}
#ship-roamer3.is-returning .s3-body {{ box-shadow: inset 0 -5px 15px rgba(0, 255, 204, 0.9), 0 0 50px rgba(0, 255, 204, 0.8) !important; }}
</style>
"""

# HTML Compilation
planets_html = ""
for i, p in enumerate(["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]):
    if p == "earth":
        planets_html += f'<div class="{p} spin planet" id="p-{p}"><div class="moon spin"></div></div>\n'
    else:
        planets_html += f'<div class="{p} spin planet" id="p-{p}"></div>\n'
    planets_html += f'<div class="{p} spin tracker" id="t-{p}" data-idx="{i}" style="opacity:0; pointer-events:none;"></div>\n'


STARRY_NIGHT_HTML = '''
<div id="starry-night-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; overflow: hidden;">
<div class="star-a"></div><div class="star-b"></div><div class="star-c"></div>
'''
for i in range(1, 6): 
    STARRY_NIGHT_HTML += f'<div class="meteor-{i}"></div>\n'

STARRY_NIGHT_HTML += f'''
<div id="solar-system-animation">
    <div class="sun"></div>
    {planets_html}
</div>

<svg id="rope-layer" style="position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9; overflow:visible;">
    <path id="lasso-rope" fill="none" stroke="rgba(0, 255, 204, 0.8)" stroke-width="1.0" stroke-linecap="round" opacity="0" style="filter: drop-shadow(0px 0px 4px #00ffcc);" />
    <path id="lasso-rope-ufo" fill="none" stroke="rgba(255, 0, 255, 0.8)" stroke-width="1.0" stroke-linecap="round" opacity="0" style="filter: drop-shadow(0px 0px 4px #ff00ff);" />
</svg>

<div id="ship-dragger" class="ship-wrap">
    <div class="rocketCon">
        <div id="anchor-dragger" style="position:absolute; left:-5px; top:30px; width:1px; height:1px; background:transparent;"></div>
        <div class="flame"></div>
        <div class="rocketBase"></div>
        <div class="topWing"></div>
        <div class="rocket">
            <div class="window"></div>
        </div>
        <div class="bottomWing"></div>
        <div class="rocketNose"></div>
    </div>
</div>

<div id="ship-roamer1" class="ship-wrap">
    <div class="r1-rocket">
        <div class="r1-window"></div>
        <div class="r1-flame"></div>
    </div>
</div>

<div id="ship-roamer2" class="ship-wrap">
    <div class="s2-flame"></div>
    <div class="s2-body"></div>
    <div class="s2-rw">
        <div class="s2-arm"></div><div class="s2-mid"></div><div class="s2-tl"></div><div class="s2-tr"></div>
        <div class="s2-tb"></div><div class="s2-bl"></div><div class="s2-br"></div><div class="s2-bb"></div>
    </div>
    <div class="s2-lw">
        <div class="s2-arm"></div><div class="s2-mid"></div><div class="s2-top"></div><div class="s2-top-bar"></div>
        <div class="s2-bot"></div><div class="s2-bot-bar"></div>
    </div>
</div>

<div id="ship-roamer3" class="ship-wrap">
    <div class="s3-ship">
        <div id="anchor-ufo" style="position:absolute; left:3rem; top:3rem; width:1px; height:1px; background:transparent;"></div>
        <div class="s3-foot_1"></div><div class="s3-foot_2"></div><div class="s3-foot_3"></div>
        <div class="s3-body"></div>
        <div class="s3-eyes">
            <div class="s3-eye_1"></div><div class="s3-eye_2"></div>
        </div>
    </div>
</div>

</div>
'''

st.markdown(METEOR_AND_ORBIT_STYLE, unsafe_allow_html=True)
st.markdown(STARRY_NIGHT_HTML, unsafe_allow_html=True)

ROCKET_ANIMATION_JS = """
<script>
(function() {
    const pWin = window.parent || window;
    const pDoc = pWin.document;

    if (!pDoc.getElementById('gsap-lib-script')) {
        const script = pDoc.createElement('script');
        script.id = 'gsap-lib-script';
        script.src = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js";
        pDoc.head.appendChild(script);
    }

    let initInt = setInterval(() => {
        if (pWin.gsap) {
            clearInterval(initInt);
            startPhysicsBrain(pWin.gsap);
            // Always re-run: startPhysicsBrain returns early once the brain is
            // active, but a Streamlit rerun can hand us a fresh (invisible)
            // node that still needs revealing.
            revealSolarSystem(pWin.gsap);
        }
    }, 200);

    // Restores the solar system to its visible, positioned state. Safe to call
    // repeatedly - it simply re-asserts the same values.
    function revealSolarSystem(gsap) {
        const el = pDoc.getElementById('solar-system-animation');
        if (!el) return;
        const pos = pWin.SUN_POS ||
                    { x: pWin.innerWidth * 0.85, y: pWin.innerHeight * 0.25 };
        gsap.set(el, {
            opacity: 0.6,
            right: 'auto', bottom: 'auto', left: 0, top: 0,
            xPercent: -50, yPercent: -50, scale: 0.5,
            x: pos.x, y: pos.y
        });
    }

    function startPhysicsBrain(gsap) {
        if (pWin.ROCKET_BRAIN_ACTIVE) return;
        pWin.ROCKET_BRAIN_ACTIVE = true;

        const w = pWin.innerWidth;
        const h = pWin.innerHeight;

        class PhysicsRocket {
            constructor(x, y, maxSpeed, maxForce, offsetRot) {
                this.x = x; this.y = y;
                this.vx = 0; this.vy = 0;
                this.baseSpeed = maxSpeed;
                this.baseForce = maxForce;
                this.maxSpeed = maxSpeed;
                this.maxForce = maxForce;
                this.targetX = x; this.targetY = y;
                this.rotation = 0;
                this.offsetRot = offsetRot; 
            }
            setTarget(x, y) {
                this.targetX = x; this.targetY = y;
            }
            update() {
                let dx = this.targetX - this.x;
                let dy = this.targetY - this.y;
                let dist = Math.hypot(dx, dy);
                
                if (dist > 5) {
                    let desiredVx = (dx / dist) * this.maxSpeed;
                    let desiredVy = (dy / dist) * this.maxSpeed;
                    
                    let steerX = desiredVx - this.vx;
                    let steerY = desiredVy - this.vy;
                    
                    let steerMag = Math.hypot(steerX, steerY);
                    if (steerMag > this.maxForce) {
                        steerX = (steerX / steerMag) * this.maxForce;
                        steerY = (steerY / steerMag) * this.maxForce;
                    }
                    this.vx += steerX; this.vy += steerY;
                } else {
                    this.vx *= 0.9; this.vy *= 0.9;
                }
                
                // Pure physics flight - no walls
                this.x += this.vx; 
                this.y += this.vy;

                if (Math.hypot(this.vx, this.vy) > 0.5) {
                    let targetRot = Math.atan2(this.vy, this.vx) * (180 / Math.PI) + this.offsetRot;
                    let diff = targetRot - this.rotation;
                    while (diff < -180) diff += 360;
                    while (diff > 180) diff -= 360;
                    this.rotation += diff * 0.05; 
                }
            }
        }

        pWin.dragger = new PhysicsRocket(-200, h/2,   1.8, 0.03, 45); 
        pWin.r1      = new PhysicsRocket(w*0.5, h*0.5, 1.2, 0.02, 90); 
        pWin.r2      = new PhysicsRocket(w+400, h*0.8, 0.8, 0.01, 0);  
        pWin.r3      = new PhysicsRocket(-400, h*0.5,  1.5, 0.025, 90);

        const NUM_SEGMENTS = 12;
        const SEGMENT_LENGTH = 6;
        let rope1 = []; let rope3 = [];
        for(let i=0; i<NUM_SEGMENTS; i++) { rope1.push({x:0,y:0,oldX:0,oldY:0}); rope3.push({x:0,y:0,oldX:0,oldY:0}); }

        let ship1State = { phase: "WANDERING", targetPlanet: null, tracker: null, count: 0, px: 0, py: 0, vx: 0, vy: 0, ropeFreq: 1.0, seed: 0 };
        let ship3State = { phase: "WANDERING", targetPlanet: null, tracker: null, count: 0, px: 0, py: 0, vx: 0, vy: 0, ropeFreq: 1.8, seed: 500 };
        let ship2State = { phase: "WANDERING", timer: 0, blastAngle: 0, portalX: 0, portalY: 0, portalEl: null };

        pWin.seraphimShip1State = ship1State;
        pWin.seraphimShip3State = ship3State;

        // ── AUTONOMOUS SUN STATE MACHINE ──
        // State 1: IDLE (Wait 9 mins initially, then 10 mins)
        // State 2: MOVING (Turn Red, glide slowly to new target over 10 mins)
        let sunState = {
            phase: 'IDLE',
            timer: Date.now() + (3 * 60 * 1000), // Start with a 9-minute wait
            startX: w * 0.85,
            startY: h * 0.25
        };

        let sunPhysics = {
            x: w * 0.85, y: h * 0.25,
            targetX: w * 0.85, targetY: h * 0.25
        };

        // Publish the live sun position so a later rerun can restore the
        // solar system to exactly where the physics loop has it.
        pWin.SUN_POS = sunPhysics;
        revealSolarSystem(gsap);
        function getFarTarget(currX, currY, w, h) {
            let tx = (Math.random() - 0.2) * (w * 1.4);
            let ty = (Math.random() - 0.2) * (h * 1.4);
            if (Math.hypot(tx - currX, ty - currY) < 400) {
                tx = (tx + w/2) % w; ty = (ty + h/2) % h;
            }
            return {x: tx, y: ty};
        }

        // Give ships initial targets so they don't get stuck
        pWin.r1.setTarget(w * 0.5, h * 0.5);
        pWin.r2.setTarget(getFarTarget(w+400, h*0.8, w, h).x, getFarTarget(w+400, h*0.8, w, h).y);
        pWin.dragger.setTarget(getFarTarget(-200, h/2, w, h).x, getFarTarget(-200, h/2, w, h).y);
        pWin.r3.setTarget(getFarTarget(-400, h/2, w, h).x, getFarTarget(-400, h/2, w, h).y);

        function spawnChargingParticle(shipEl) {
            const p = pDoc.createElement('div'); p.className = 's2-particle';
            const angle = Math.random() * Math.PI * 2; const dist = 80 + Math.random() * 70;
            const startX = Math.cos(angle) * dist; const startY = Math.sin(angle) * dist;
            p.style.left = startX + 'px'; p.style.top = startY + 'px'; shipEl.appendChild(p);
            gsap.to(p, { x: -startX - 65, y: -startY + 10, opacity: 0, scale: 0.1, duration: 0.3 + Math.random() * 0.4, ease: "power2.in", onComplete: () => p.remove() });
        }

        // --- NORMAL PLANET HUNTING LOGIC ---
        function runShipStateMachine(ship, state, allowedIdxStart, allowedIdxEnd, planetsAll, trackersAll) {
            let dDist = Math.hypot(ship.targetX - ship.x, ship.targetY - ship.y);

            if (state.phase === "DRAGGING") { ship.maxSpeed = ship.baseSpeed * 0.4; ship.maxForce = ship.baseForce * 0.3; } 
            else if (state.phase === "RETURNING") { ship.maxSpeed = ship.baseSpeed * 3.5; ship.maxForce = ship.baseForce * 2.5; } 
            else if (state.phase === "HUNTING") { ship.maxSpeed = ship.baseSpeed * 2.5; ship.maxForce = ship.baseForce * 2.0; } 
            else { ship.maxSpeed = ship.baseSpeed * 1.5; ship.maxForce = ship.baseForce * 1.5; } 

            if (state.phase === "WANDERING") {
                if (dDist < 100) { 
                    if (Math.random() > 0.4 && planetsAll.length > 0) {
                        let allowedPlanets = planetsAll.slice(allowedIdxStart, allowedIdxEnd);
                        let allowedTrackers = trackersAll.slice(allowedIdxStart, allowedIdxEnd);
                        if (allowedPlanets.length > 0) {
                            let pick = Math.floor(Math.random() * allowedPlanets.length);
                            let chosenP = allowedPlanets[pick]; let chosenT = allowedTrackers[pick];
                            if (chosenP !== ship1State.targetPlanet && chosenP !== ship3State.targetPlanet) {
                                state.phase = "HUNTING"; state.targetPlanet = chosenP; state.tracker = chosenT;
                            } else { let nt = getFarTarget(ship.x, ship.y, w, h); ship.setTarget(nt.x, nt.y); }
                        }
                    } else { let nt = getFarTarget(ship.x, ship.y, w, h); ship.setTarget(nt.x, nt.y); }
                }
            }
            else if (state.phase === "HUNTING") {
                if (state.targetPlanet && state.tracker && pDoc.body.contains(state.targetPlanet)) {
                    const tRect = state.tracker.getBoundingClientRect();
                    const tx = tRect.left + tRect.width/2; const ty = tRect.top + tRect.height/2;
                    ship.setTarget(tx, ty);
                    if (Math.hypot(ship.x - tx, ship.y - ty) < 50) {
                        state.phase = "DRAGGING"; state.count = 0; state.px = tx; state.py = ty; state.vx = 0; state.vy = 0;
                        let nt = getFarTarget(ship.x, ship.y, w, h); ship.setTarget(nt.x, nt.y);
                    }
                } else { state.phase = "WANDERING"; }
            }
            else if (state.phase === "DRAGGING") {
                if (dDist < 100) {
                    state.count++;
                    if (state.count > 2) { state.phase = "RETURNING"; } 
                    else { let nt = getFarTarget(ship.x, ship.y, w, h); ship.setTarget(nt.x, nt.y); }
                }
            }
            else if (state.phase === "RETURNING") {
                if (state.targetPlanet && state.tracker) {
                    const tRect = state.tracker.getBoundingClientRect();
                    const orbitX = tRect.left + tRect.width/2; const orbitY = tRect.top + tRect.height/2;
                    const angleRad = Math.atan2(orbitY - ship.y, orbitX - ship.x);
                    const ropeLen = SEGMENT_LENGTH * (NUM_SEGMENTS * 0.4); 
                    ship.setTarget(orbitX + Math.cos(angleRad) * ropeLen, orbitY + Math.sin(angleRad) * ropeLen);

                    if (Math.hypot(state.px - orbitX, state.py - orbitY) < 60 || Math.hypot(ship.x - orbitX, ship.y - orbitY) < 40) {
                        state.targetPlanet.style.removeProperty('translate');
                        state.targetPlanet = null; state.tracker = null; state.phase = "WANDERING";
                        let nt = getFarTarget(ship.x, ship.y, w, h); ship.setTarget(nt.x, nt.y);
                    }
                } else { 
                    state.phase = "WANDERING"; 
                    let nt = getFarTarget(ship.x, ship.y, w, h); ship.setTarget(nt.x, nt.y);
                }
            }
        }

        function simulateRope(shipEl, anchorId, ropeArr, stateObj, svgLine, sCenterX, sCenterY) {
            if (stateObj.targetPlanet && (stateObj.phase === "DRAGGING" || stateObj.phase === "RETURNING")) {
                const aRect = pDoc.getElementById(anchorId).getBoundingClientRect();
                ropeArr[0].x = aRect.left + aRect.width/2; ropeArr[0].y = aRect.top + aRect.height/2;
                
                let isHeavy = (stateObj.phase === "DRAGGING");
                let sag = isHeavy ? 0.1 : 0.8;
                let waveAmp = isHeavy ? 0.3 : 2.0; let freqMult = isHeavy ? 3.0 : 1.0;
                let timeObj = Date.now() * 0.005 + stateObj.seed;

                for(let i=1; i<NUM_SEGMENTS; i++) {
                    let p = ropeArr[i];
                    let vx = (p.x - p.oldX) * 0.90; let vy = (p.y - p.oldY) * 0.90 + sag; 
                    vx += Math.sin(timeObj * stateObj.ropeFreq * freqMult + i * 0.3) * waveAmp;
                    p.oldX = p.x; p.oldY = p.y; p.x += vx; p.y += vy;
                }
                for (let iter=0; iter<5; iter++) { 
                    for(let i=0; i<NUM_SEGMENTS-1; i++) {
                        let p1 = ropeArr[i]; let p2 = ropeArr[i+1];
                        let dx = p2.x - p1.x; let dy = p2.y - p1.y; let dist = Math.hypot(dx, dy);
                        if (dist === 0) continue;
                        let diff = SEGMENT_LENGTH - dist; let percent = diff / dist / 2;
                        if (i !== 0) { p1.x -= dx * percent; p1.y -= dy * percent; }
                        p2.x += dx * percent; p2.y += dy * percent;
                    }
                }

                const tail = ropeArr[NUM_SEGMENTS-1];
                let spring = isHeavy ? 0.04 : 0.15; let damp = isHeavy ? 0.95 : 0.85;   
                stateObj.vx += (tail.x - stateObj.px) * spring; stateObj.vy += (tail.y - stateObj.py) * spring;
                stateObj.vx *= damp; stateObj.vy *= damp;
                stateObj.px += stateObj.vx; stateObj.py += stateObj.vy;
                tail.x = stateObj.px; tail.y = stateObj.py;

                const localX = (stateObj.px - sCenterX) / 0.5; const localY = (stateObj.py - sCenterY) / 0.5;
                stateObj.targetPlanet.style.setProperty('translate', `${localX}px ${localY}px`, 'important');

                let pathD = `M ${ropeArr[0].x} ${ropeArr[0].y}`;
                for(let i=1; i<NUM_SEGMENTS; i++) { pathD += ` L ${ropeArr[i].x} ${ropeArr[i].y}`; }
                svgLine.setAttribute('d', pathD); svgLine.setAttribute('opacity', '1');
                
                let ropeColor = (shipEl.id === 'ship-dragger') ? (isHeavy ? 'rgba(255, 100, 0, 0.9)' : 'rgba(0, 255, 204, 0.8)') : (isHeavy ? 'rgba(255, 0, 0, 0.9)' : 'rgba(255, 0, 255, 0.8)');
                svgLine.setAttribute('stroke', ropeColor);
                svgLine.setAttribute('stroke-width', isHeavy ? '2.0' : '1.0');
                svgLine.style.filter = `drop-shadow(0px 0px ${isHeavy ? '8px' : '4px'} ${ropeColor})`;
            } else {
                svgLine.setAttribute('opacity', '0');
                if (pDoc.getElementById(anchorId)) {
                    const aRect = pDoc.getElementById(anchorId).getBoundingClientRect();
                    for(let i=0; i<NUM_SEGMENTS; i++) {
                        ropeArr[i].x = aRect.left + aRect.width/2; ropeArr[i].y = aRect.top + aRect.height/2;
                        ropeArr[i].oldX = ropeArr[i].x; ropeArr[i].oldY = ropeArr[i].y;
                    }
                }
            }
        }

        // ── MASTER TICKER LOOP ──
        gsap.ticker.add(() => {
            const now = Date.now();
            const elDragger = pDoc.getElementById('ship-dragger');
            const elR1 = pDoc.getElementById('ship-roamer1');
            const elR2 = pDoc.getElementById('ship-roamer2');
            const elR3 = pDoc.getElementById('ship-roamer3');
            const elSolar = pDoc.getElementById('solar-system-animation');
            const elRope1 = pDoc.getElementById('lasso-rope');
            const elRope3 = pDoc.getElementById('lasso-rope-ufo');
            
            if (!elDragger || !elSolar || !elRope1) return;

            const planetsAll = Array.from(elSolar.querySelectorAll('.planet')).filter(p => !p.classList.contains('moon'));
            const trackersAll = Array.from(elSolar.querySelectorAll('.tracker'));
            const sRect = elSolar.getBoundingClientRect();
            const sCenterX = sRect.left + sRect.width/2;
            const sCenterY = sRect.top + sRect.height/2;

            // Update Ships Freely
            pWin.dragger.update(); 
            pWin.r3.update();
            pWin.r1.update(); 
            pWin.r2.update(); 

            if (elR1) {
                let speedRatio1 = Math.min(1, Math.hypot(pWin.r1.vx, pWin.r1.vy) / Math.max(0.001, pWin.r1.maxSpeed));
                gsap.set(elR1.querySelector('.r1-flame'), { scaleY: 0.3 + speedRatio1 * 1.2, opacity: 0.2 + speedRatio1 * 0.8 });
            }

            gsap.set(elDragger, { x: pWin.dragger.x, y: pWin.dragger.y, rotation: pWin.dragger.rotation, opacity: 1 });
            if(elR1) gsap.set(elR1, { x: pWin.r1.x, y: pWin.r1.y, rotation: pWin.r1.rotation, opacity: 1 });
            if(elR2) gsap.set(elR2, { x: pWin.r2.x, y: pWin.r2.y, rotation: pWin.r2.rotation, opacity: 1 });
            if(elR3) gsap.set(elR3, { x: pWin.r3.x, y: pWin.r3.y, rotation: pWin.r3.rotation, opacity: 1 });

            // Random roam logic for R1
            if (Math.hypot(pWin.r1.targetX - pWin.r1.x, pWin.r1.targetY - pWin.r1.y) < 80) { 
                let t = getFarTarget(pWin.r1.x, pWin.r1.y, w, h); 
                pWin.r1.setTarget(t.x, t.y); 
            }
// ── HEAVY CRUISER: HYPERSPACE PORTAL ENGINE (SHIP 2) ──
            if (elR2) {
                let dDist2 = Math.hypot(pWin.r2.targetX - pWin.r2.x, pWin.r2.targetY - pWin.r2.y);
                
                if (ship2State.phase === "WANDERING") {
                    pWin.r2.maxSpeed = pWin.r2.baseSpeed; pWin.r2.maxForce = pWin.r2.baseForce;
                    if (dDist2 < 80) { let t = getFarTarget(pWin.r2.x, pWin.r2.y, w, h); pWin.r2.setTarget(t.x, t.y); }
                    
                    let speedRatio2 = Math.min(1, Math.hypot(pWin.r2.vx, pWin.r2.vy) / pWin.r2.maxSpeed);
                    gsap.set(elR2.querySelector('.s2-flame'), { scaleX: 0.3 + speedRatio2 * 1.5, opacity: 0.2 + speedRatio2 * 0.8 });
                    
                    // Randomly decide to jump to Hyperspace
                    if (Math.random() < 0.0010) { 
                        ship2State.phase = "CHARGING"; 
                        ship2State.timer = now + 4000; // Charge for 4 seconds
                        ship2State.blastAngle = Math.atan2(pWin.r2.vy, pWin.r2.vx); 
                    }
                } 
                else if (ship2State.phase === "CHARGING") {
                    pWin.r2.maxSpeed = 0.05; pWin.r2.maxForce = 0.02; // Slow to a crawl
                    pWin.r2.setTarget(pWin.r2.x + Math.cos(ship2State.blastAngle)*100, pWin.r2.y + Math.sin(ship2State.blastAngle)*100);
                    gsap.set(elR2.querySelector('.s2-flame'), { clearProps: "all" });
                    
                    if (Math.random() < 0.3) spawnChargingParticle(elR2); // Gather atoms
                    
                    if (now > ship2State.timer) { 
                        ship2State.phase = "PORTAL_OPENING"; 
                        ship2State.timer = now + 2000; 
                        
                        // Pick a coordinate right in front of the ship
                        ship2State.portalX = pWin.r2.x + Math.cos(ship2State.blastAngle) * 160;
                        ship2State.portalY = pWin.r2.y + Math.sin(ship2State.blastAngle) * 160;
                        
                        // Spawn the visual portal
                        let portal = pDoc.createElement('div');
                        portal.className = 'gs-portal';
                        portal.style.left = ship2State.portalX + 'px';
                        portal.style.top = ship2State.portalY + 'px';
                        pDoc.body.appendChild(portal);
                        ship2State.portalEl = portal;
                        
                        gsap.to(portal, { scale: 1.5, opacity: 1, duration: 2, ease: "power2.out" });
                        gsap.to(portal, { rotation: 360, duration: 2, repeat: -1, ease: "linear" }); // Spin
                    }
                }
                else if (ship2State.phase === "PORTAL_OPENING") {
                    pWin.r2.maxSpeed = 0; pWin.r2.vx *= 0.8; pWin.r2.vy *= 0.8; // Brake hard
                    if (now > ship2State.timer) {
                        ship2State.phase = "ENTERING_PORTAL";
                        ship2State.timer = now + 3000; // Takes exactly 3 seconds to get sucked in
                    }
                }
                else if (ship2State.phase === "ENTERING_PORTAL") {
                    // Pull the ship steadily into the center of the portal
                    pWin.r2.x += (ship2State.portalX - pWin.r2.x) * 0.03;
                    pWin.r2.y += (ship2State.portalY - pWin.r2.y) * 0.03;
                    
                    if (now > ship2State.timer) {
                        ship2State.phase = "IN_HYPERSPACE";
                        ship2State.timer = now + (10 * 60 * 1000); // <-- 10 MINUTE HYPERSPACE TIMER
                        
                        // Implode the portal behind it
                        if (ship2State.portalEl) {
                            gsap.to(ship2State.portalEl, { scale: 0, opacity: 0, duration: 1, ease: "power2.in", onComplete: () => {
                                if (ship2State.portalEl.parentNode) ship2State.portalEl.remove();
                                ship2State.portalEl = null;
                            }});
                        }
                    }
                }
                else if (ship2State.phase === "IN_HYPERSPACE") {
                    pWin.r2.x = -5000; pWin.r2.y = -5000; // Physically move it off the map
                    
                    if (now > ship2State.timer) {
                        ship2State.phase = "PORTAL_EXIT_OPENING";
                        ship2State.timer = now + 2000;
                        
                        // Pick a completely random spot on the screen to exit
                        ship2State.portalX = Math.random() * (w - 200) + 100;
                        ship2State.portalY = Math.random() * (h - 200) + 100;
                        
                        let portal = pDoc.createElement('div');
                        portal.className = 'gs-portal';
                        portal.style.left = ship2State.portalX + 'px';
                        portal.style.top = ship2State.portalY + 'px';
                        pDoc.body.appendChild(portal);
                        ship2State.portalEl = portal;
                        
                        gsap.to(portal, { scale: 1.5, opacity: 1, duration: 2, ease: "power2.out" });
                        gsap.to(portal, { rotation: 360, duration: 2, repeat: -1, ease: "linear" });
                    }
                }
                else if (ship2State.phase === "PORTAL_EXIT_OPENING") {
                    if (now > ship2State.timer) {
                        ship2State.phase = "EXITING_PORTAL";
                        ship2State.timer = now + 3000; // Takes 3 seconds to exit
                        
                        // Snap ship to center of new portal
                        pWin.r2.x = ship2State.portalX; 
                        pWin.r2.y = ship2State.portalY;
                        pWin.r2.vx = 0; pWin.r2.vy = 0;
                        
                        // Pick a random direction to fly out
                        ship2State.blastAngle = Math.random() * Math.PI * 2;
                        pWin.r2.rotation = ship2State.blastAngle * (180/Math.PI);
                    }
                }
                else if (ship2State.phase === "EXITING_PORTAL") {
                    // Glide smoothly out of the portal
                    pWin.r2.x += Math.cos(ship2State.blastAngle) * 1.5;
                    pWin.r2.y += Math.sin(ship2State.blastAngle) * 1.5;
                    
                    if (now > ship2State.timer) {
                        ship2State.phase = "WANDERING";
                        pWin.r2.setTarget(w/2, h/2);
                        
                        // Implode portal
                        if (ship2State.portalEl) {
                            gsap.to(ship2State.portalEl, { scale: 0, opacity: 0, duration: 1, ease: "power2.in", onComplete: () => {
                                if (ship2State.portalEl.parentNode) ship2State.portalEl.remove();
                                ship2State.portalEl = null;
                            }});
                        }
                    }
                }
                
                // --- APPLY CSS CLASSES ---
                if (ship2State.phase === 'CHARGING') { elR2.classList.add('is-charging'); } 
                else { elR2.classList.remove('is-charging'); }
                
                // --- APPLY MASTER GSAP SCALING/POSITION ---
                if (ship2State.phase === "ENTERING_PORTAL") {
                    let progress = 1 - ((ship2State.timer - now) / 3000); // Fades from 1 to 0
                    gsap.set(elR2, { x: pWin.r2.x, y: pWin.r2.y, rotation: pWin.r2.rotation, scale: 0.05 * progress, opacity: progress });
                } 
                else if (ship2State.phase === "EXITING_PORTAL") {
                    let progress = 1 - ((ship2State.timer - now) / 3000); // Grows from 0 to 1
                    gsap.set(elR2, { x: pWin.r2.x, y: pWin.r2.y, rotation: pWin.r2.rotation, scale: 0.05 * progress, opacity: progress });
                } 
                else if (ship2State.phase === "IN_HYPERSPACE" || ship2State.phase === "PORTAL_EXIT_OPENING") {
                    gsap.set(elR2, { opacity: 0 }); // Hidden
                } 
                else {
                    gsap.set(elR2, { x: pWin.r2.x, y: pWin.r2.y, rotation: pWin.r2.rotation, scale: 0.05, opacity: 1 });
                }
            }

            // ── NORMAL DRAGGER & UFO PLANET HUNTING ──
            runShipStateMachine(pWin.dragger, ship1State, 0, planetsAll.length, planetsAll, trackersAll);
            runShipStateMachine(pWin.r3, ship3State, 0, 4, planetsAll, trackersAll);
            simulateRope(elDragger, 'anchor-dragger', rope1, ship1State, elRope1, sCenterX, sCenterY);
            simulateRope(elR3, 'anchor-ufo', rope3, ship3State, elRope3, sCenterX, sCenterY); 
            elDragger.className = `ship-wrap is-${ship1State.phase.toLowerCase()}`;
            elR3.className = `ship-wrap is-${ship3State.phase.toLowerCase()}`;


            // ══════════════════════════════════════════════════════════════════
            // ── STATIC SUN ENGINE ──
            // ══════════════════════════════════════════════════════════════════
            // The Sun will no longer move or turn red. It stays exactly where it started.
            gsap.set(elSolar, { x: sunPhysics.x, y: sunPhysics.y });

            // A rerun can swap in a replacement node between frames; if that
            // happens, this catches it on the very next tick.
            if (elSolar.style.opacity === '' || elSolar.style.opacity === '0') {
                revealSolarSystem(gsap);
            }

        });
    }
})();
</script>
"""
components.html(ROCKET_ANIMATION_JS, height=0)

# ── GUNSHIP BRAIN: Injected cleanly after ROCKET_ANIMATION_JS ─────────────────────────────
GUNSHIP_BRAIN_JS = """
<script>
(function() {
    const pWin = window.parent || window;
    const pDoc = pWin.document;

    // ── Wait for GSAP + physics brain to be ready ──────────────────────────────
    let bootInterval = setInterval(() => {
        if (!pWin.gsap || !pWin.ROCKET_BRAIN_ACTIVE || !pWin.r1 || !pWin.r2 || !pWin.dragger) return;
        clearInterval(bootInterval);
        bootGunship(pWin.gsap);
    }, 300);

    function bootGunship(gsap) {
        if (pWin.GUNSHIP_ACTIVE) return;
        pWin.GUNSHIP_ACTIVE = true;

        const w = pWin.innerWidth;
        const h = pWin.innerHeight;

        // ── Inject CSS for beams, muzzle flashes, craters, impacts ───────────
        const style = pDoc.createElement('style');
        style.id = 'gunship-styles';
        style.textContent = `
            .gs-bullet {
                position: fixed; pointer-events: none; z-index: 50;
                width: 15px; height: 3px; border-radius: 2px;
                background: #ffffff; transform-origin: center;
                box-shadow: 0 0 8px 3px rgba(255,255,255,0.9);
            }
            .gs-muzzle {
                position: fixed; pointer-events: none; z-index: 51;
                width: 18px; height: 18px; border-radius: 50%;
                background: radial-gradient(circle, #ffffff 0%, #39beff 40%, rgba(57,190,255,0) 70%);
                box-shadow: 0 0 12px 6px rgba(57,190,255,0.9);
                transform: translate(-50%, -50%) scale(0); opacity: 0;
            }
            .gs-impact {
                position: fixed; pointer-events: none; z-index: 52;
                border-radius: 50%; transform: translate(-50%, -50%) scale(0); opacity: 0;
            }
            .gs-crater {
                position: absolute; pointer-events: none; z-index: 20;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(0,0,0,0.85) 0%, rgba(30,20,10,0.7) 40%, rgba(20,15,5,0.4) 70%, transparent 100%);
                border: 1px solid rgba(255,120,30,0.4);
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.9), 0 0 4px rgba(255,80,0,0.3);
                transform: translate(-50%, -50%);
            }
            .gs-spark {
                position: fixed; pointer-events: none; z-index: 53;
                width: 3px; height: 3px; border-radius: 50%; background: #ffffff;
                box-shadow: 0 0 4px 2px rgba(57,190,255,0.8);
            }
            #ship-roamer1.is-gunship-charging .r1-window {
                background-color: #ff3300 !important;
                box-shadow: 0 0 20px 8px rgba(255,50,0,0.9), 0 0 40px 12px rgba(255,100,0,0.6) !important;
                animation: gunshipPulse 0.15s ease-in-out infinite alternate !important;
            }
            #ship-roamer2.is-gunship-charging .s2-body {
                box-shadow: 0 0 30px 10px rgba(0, 255, 204, 0.9), inset 0 0 20px rgba(0, 255, 204, 0.8) !important;
                animation: gunshipPulse 0.15s ease-in-out infinite alternate !important;
            }
            #ship-roamer1.is-gunship-firing .r1-window {
                background-color: #ffffff !important; box-shadow: 0 0 30px 15px rgba(255,255,255,1.0) !important;
            }
            @keyframes gunshipPulse {
                from { box-shadow: 0 0 12px 5px rgba(255,50,0,0.8); }
                to   { box-shadow: 0 0 25px 10px rgba(255,150,0,1.0); }
            }
            .gs-recoil-trail {
                position: fixed; pointer-events: none; z-index: 49;
                width: 6px; height: 6px; border-radius: 50%;
                background: radial-gradient(circle, rgba(57,190,255,0.8) 0%, rgba(57,190,255,0) 100%);
                transform: translate(-50%, -50%);
            }
        `;
        pDoc.head.appendChild(style);

        function getPlanetScreenPos(planetEl) {
            const rect = planetEl.getBoundingClientRect();
            return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2, r: rect.width / 2 };
        }

        function spawnMuzzleFlash(sx, sy) {
            const mf = pDoc.createElement('div');
            mf.className = 'gs-muzzle'; mf.style.left = sx + 'px'; mf.style.top = sy + 'px';
            pDoc.body.appendChild(mf);
            gsap.timeline().to(mf, { scale: 1.4, opacity: 1, duration: 0.06, ease: 'power2.out' })
                           .to(mf, { scale: 2.2, opacity: 0, duration: 0.18, ease: 'power2.in', onComplete: () => mf.remove() });
        }

        function spawnSparks(ix, iy, count, color) {
            color = color || '#39beff';
            for (let i = 0; i < count; i++) {
                const sp = pDoc.createElement('div');
                sp.className = 'gs-spark'; sp.style.background = color; sp.style.boxShadow = `0 0 4px 2px ${color}`;
                sp.style.left = ix + 'px'; sp.style.top = iy + 'px';
                pDoc.body.appendChild(sp);
                const angle = (Math.PI * 2 * i / count) + Math.random() * 0.5;
                const dist = 15 + Math.random() * 35;
                gsap.to(sp, { x: Math.cos(angle) * dist, y: Math.sin(angle) * dist, opacity: 0, scale: 0.2, duration: 0.35 + Math.random() * 0.3, ease: 'power2.out', onComplete: () => sp.remove() });
            }
        }

        function spawnImpact(ix, iy, color, size) {
            color = color || '#39beff'; size = size || 40;
            const imp = pDoc.createElement('div');
            imp.className = 'gs-impact'; imp.style.left = ix + 'px'; imp.style.top = iy + 'px';
            imp.style.width = size + 'px'; imp.style.height = size + 'px';
            imp.style.background = `radial-gradient(circle, #ffffff 0%, ${color} 40%, rgba(0,0,0,0) 70%)`;
            imp.style.boxShadow = `0 0 20px 10px ${color}`;
            pDoc.body.appendChild(imp);
            gsap.timeline().to(imp, { scale: 1.0, opacity: 1, duration: 0.07, ease: 'power3.out' })
                           .to(imp, { scale: 2.5, opacity: 0, duration: 0.35, ease: 'power2.in', onComplete: () => imp.remove() });
            spawnSparks(ix, iy, 8, color);
        }

        function spawnCrater(planetEl) {
            const rect = planetEl.getBoundingClientRect(); const pSize = rect.width;
            const cSize = 4 + Math.random() * 6;
            const angle = Math.random() * Math.PI * 2; const radius = Math.random() * (pSize * 0.35);
            const cx = 50 + (Math.cos(angle) * radius / pSize) * 100;
            const cy = 50 + (Math.sin(angle) * radius / pSize) * 100;
            const crater = pDoc.createElement('div');
            crater.className = 'gs-crater'; crater.style.width = cSize + 'px'; crater.style.height = cSize + 'px';
            crater.style.left = cx + '%'; crater.style.top = cy + '%'; crater.style.opacity = '0';
            planetEl.appendChild(crater);
            gsap.to(crater, { opacity: 1, duration: 0.3, ease: 'power2.out' });
        }

        function spawnRecoilTrail(sx, sy, awayAngle) {
            for (let i = 0; i < 4; i++) {
                const tr = pDoc.createElement('div');
                tr.className = 'gs-recoil-trail'; tr.style.left = sx + 'px'; tr.style.top = sy + 'px';
                pDoc.body.appendChild(tr);
                const spread = (Math.random() - 0.5) * 0.6; const d = 10 + Math.random() * 20;
                gsap.to(tr, { x: Math.cos(awayAngle + spread) * d, y: Math.sin(awayAngle + spread) * d, opacity: 0, scale: 2.5, duration: 0.4, delay: i * 0.04, ease: 'power1.out', onComplete: () => tr.remove() });
            }
        }

        function flashVoiceBar(color) {
            color = color || '#39beff';
            const bars = pDoc.querySelectorAll('.voice-bar');
            if (!bars || bars.length === 0) return;
            const bar = bars[Math.floor(Math.random() * bars.length)];
            const rect = bar.getBoundingClientRect();
            if (rect.width === 0) return;
            spawnImpact(rect.left + rect.width / 2, rect.top + rect.height / 2, color, 24);
            gsap.timeline().to(bar, { backgroundColor: '#ffffff', boxShadow: `0 0 30px 10px ${color}`, duration: 0.06 })
                           .to(bar, { backgroundColor: '', boxShadow: '', duration: 0.4 });
        }

        // ── STRAIGHT HOMING MISSILE ENGINE (NO WOBBLE) ──
        function fireBullet(sx, sy, getTargetPos, color, onHit) {
            color = color || '#39beff';
            
            let initialTarget = getTargetPos();
            if (!initialTarget) return; 

            // Reduced fan-out for a much straighter launch trajectory
            let baseAngle = Math.atan2(initialTarget.y - sy, initialTarget.x - sx);
            let launchAngle = baseAngle + (Math.random() - 0.5) * 0.4; 
            
            spawnMuzzleFlash(sx, sy); 
            
            const b = pDoc.createElement('div');
            b.className = 'gs-bullet'; 
            b.style.background = color; 
            b.style.boxShadow = `0 0 10px 3px ${color}`;
            pDoc.body.appendChild(b);
            
            gsap.set(b, { x: sx, y: sy, rotation: launchAngle * (180/Math.PI), xPercent: -50, yPercent: -50 });

            let cx = sx;
            let cy = sy;
            
            // Fast launch speed
            let vx = Math.cos(launchAngle) * 7; 
            let vy = Math.sin(launchAngle) * 7;
            
            const maxSpeed = 6;  // High top speed to catch moving targets
            let life = 0;

            function tick() {
                life++;
                let tPos = getTargetPos();
                
                // Target lost - fly straight off screen
                if (!tPos || !pDoc.body.contains(b)) {
                    cx += vx; cy += vy;
                    gsap.set(b, { x: cx, y: cy });
                    if (cx < -100 || cx > w+100 || cy < -100 || cy > h+100) { if (b.parentNode) b.remove(); }
                    else requestAnimationFrame(tick);
                    return;
                }
                
                let distX = tPos.x - cx;
                let distY = tPos.y - cy;
                let dist = Math.hypot(distX, distY);
                
                // EXACT HIT REGISTRATION
                if (dist <= 28) { 
                    b.remove();
                    if (onHit) onHit(tPos.x, tPos.y);
                    return;
                }
                
                // STRAIGHT BUT HIGHLY ACCURATE TRACKING (No wobble)
                let desiredVx = (distX / dist) * maxSpeed;
                let desiredVy = (distY / dist) * maxSpeed;

                // Calculate turning force needed
                let steerX = desiredVx - vx;
                let steerY = desiredVy - vy;
                
                // Strong steering force so it cleanly catches fast targets
                let steerForce = dist < 200 ? 5.0 : 1.5; 
                
                let steerMag = Math.hypot(steerX, steerY);
                if (steerMag > steerForce) {
                    steerX = (steerX / steerMag) * steerForce;
                    steerY = (steerY / steerMag) * steerForce;
                }
                
                // Apply straight physics steering
                vx += steerX;
                vy += steerY;
                cx += vx;
                cy += vy;
                
                // Point missile exactly where it's flying
                let currentAngle = Math.atan2(vy, vx);
                gsap.set(b, { x: cx, y: cy, rotation: currentAngle * (180/Math.PI) });
                
                // GLOWING MISSILE EXHAUST TRAIL
                if (life % 2 === 0) {
                    const tr = pDoc.createElement('div');
                    tr.className = 'gs-spark'; 
                    tr.style.background = color;
                    tr.style.boxShadow = `0 0 6px ${color}`;
                    tr.style.left = cx + 'px';
                    tr.style.top = cy + 'px';
                    tr.style.zIndex = 49;
                    tr.style.opacity = '0.9';
                    tr.style.transform = 'translate(-50%, -50%)';
                    pDoc.body.appendChild(tr);
                    // Fade out smoke trail
                    gsap.to(tr, { opacity: 0, scale: 0.1, duration: 0.4, onComplete: () => tr.remove() });
                }

                requestAnimationFrame(tick);
            }
            requestAnimationFrame(tick);
        }

        function startGatheringAtoms(shipObj, customColors) {
            const colors = customColors || ['#00ffff', '#ffffff', '#39beff'];
            for(let i=0; i<30; i++) {
                const atom = pDoc.createElement('div');
                atom.style.position = 'fixed'; atom.style.width = '3px'; atom.style.height = '3px';
                atom.style.borderRadius = '50%'; atom.style.background = colors[Math.floor(Math.random()*colors.length)];
                atom.style.boxShadow = `0 0 8px ${atom.style.background}`; atom.style.zIndex = '55'; atom.style.pointerEvents = 'none';
                pDoc.body.appendChild(atom);
                const a = Math.random() * Math.PI * 2; const d = 80 + Math.random() * 100;
                const sx = shipObj.x + Math.cos(a)*d; const sy = shipObj.y + Math.sin(a)*d;
                gsap.set(atom, { x: sx, y: sy, opacity: 0 });
                gsap.to(atom, { opacity: 1, duration: 0.2, delay: Math.random()*0.5 });
                gsap.to(atom, { x: () => shipObj.x, y: () => shipObj.y, duration: 1.5 + Math.random()*0.5, ease: "power2.in", onComplete: () => atom.remove() });
            }
        }

        function getAllPlanets() {
            const solar = pDoc.getElementById('solar-system-animation');
            if (!solar) return [];
            return Array.from(solar.querySelectorAll('.planet')).filter(p => !p.classList.contains('moon'));
        }

        function pickRandomTarget() {
            // V V V  TARGETING UPDATED TO ONLY LOCK ONTO PLANETS  V V V
            const planets = getAllPlanets();
            if (planets.length > 0) {
                return { type: 'planet', el: planets[Math.floor(Math.random() * planets.length)] };
            }
            
            // Failsafe in case all planets are destroyed
            return { type: 'random', x: pWin.innerWidth/2, y: pWin.innerHeight/2 };
        }

        function resolveTarget(target, gp) {
            let getTargetPos, onHitExtra;
            
            const neonColors = ['#ff3300', '#39beff', '#cc00ff', '#00ffcc', '#ffff00', '#ff00ff', '#00ff00', '#ffffff'];
            let color = neonColors[Math.floor(Math.random() * neonColors.length)];

            // We left the dragger/ufo logic in here just in case they are targeted by a duel, 
            // but pickRandomTarget will NEVER select them anymore for normal attacks.
            if (target.type === 'dragger') {
                getTargetPos = () => ({ x: pWin.dragger.x, y: pWin.dragger.y });
                onHitExtra = (hitX, hitY) => {
                    let a = Math.atan2(hitY - gp.y, hitX - gp.x);
                    pWin.dragger.vx += Math.cos(a) * 0.5; pWin.dragger.vy += Math.sin(a) * 0.5;
                    spawnImpact(hitX, hitY, color, 6);
                };
            } else if (target.type === 'ufo') {
                getTargetPos = () => ({ x: pWin.r3.x, y: pWin.r3.y });
                onHitExtra = (hitX, hitY) => {
                    let a = Math.atan2(hitY - gp.y, hitX - gp.x);
                    pWin.r3.vx += Math.cos(a) * 0.2; pWin.r3.vy += Math.sin(a) * 0.2;
                    spawnImpact(hitX, hitY, color, 6);
                };
            } else if (target.type === 'planet' && target.el) {
                // Tracking exact planet orbit bounds every frame
                getTargetPos = () => {
                    if (!pDoc.body.contains(target.el)) return null;
                    return getPlanetScreenPos(target.el);
                };
                onHitExtra = (hitX, hitY) => { spawnImpact(hitX, hitY, color, 6); spawnCrater(target.el); };
            } else if (target.type === 'voicebar' && target.el && pDoc.body.contains(target.el)) {
                const rect = target.el.getBoundingClientRect(); 
                getTargetPos = () => ({ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 });
                onHitExtra = (hitX, hitY) => { spawnImpact(hitX, hitY, color, 2); flashVoiceBar(color); };
            } else {
                let staticX = target.x || (gp.x + 200); 
                let staticY = target.y || (gp.y + 200);
                getTargetPos = () => ({ x: staticX, y: staticY });
                onHitExtra = (hitX, hitY) => spawnImpact(hitX, hitY, color, 6);
            }
            return { getTargetPos, color, onHitExtra };
        }

        function executeBulletActionR1(target) {
            // V V V ENSURES DEFAULT TARGET IS ALWAYS A PLANET V V V
            if (!target || target.type !== 'planet') target = pickRandomTarget(); 
            
            const gp = { x: pWin.r1.x, y: pWin.r1.y };
            let { getTargetPos, color, onHitExtra } = resolveTarget(target, gp);

            let initialPos = getTargetPos();
            if (!initialPos) return;

            let angle = Math.atan2(initialPos.y - gp.y, initialPos.x - gp.x);
            if (pWin.r1) pWin.r1.rotation = angle * (180/Math.PI) + pWin.r1.offsetRot;
            pWin.r1.vx -= Math.cos(angle) * 1.8; pWin.r1.vy -= Math.sin(angle) * 1.8;
            
            const elR1 = pDoc.getElementById('ship-roamer1');
            if (elR1) elR1.classList.add('is-gunship-firing');
            
            fireBullet(gp.x, gp.y, getTargetPos, color, (hitX, hitY) => {
                if(onHitExtra) onHitExtra(hitX, hitY);
                if (elR1) elR1.classList.remove('is-gunship-firing');
            });
        }

        function executeBulletActionR2(target) {
            // V V V ENSURES DEFAULT TARGET IS ALWAYS A PLANET V V V
            if (!target || target.type !== 'planet') target = pickRandomTarget(); 
            
            const gp = { x: pWin.r2.x, y: pWin.r2.y };
            let { getTargetPos, color, onHitExtra } = resolveTarget(target, gp);

            let initialPos = getTargetPos();
            if (!initialPos) return;

            let angle = Math.atan2(initialPos.y - gp.y, initialPos.x - gp.x);
            pWin.r2.vx -= Math.cos(angle) * 0.8; 
            pWin.r2.vy -= Math.sin(angle) * 0.8;
            
            fireBullet(gp.x, gp.y, getTargetPos, color, (hitX, hitY) => {
                if(onHitExtra) onHitExtra(hitX, hitY);
            });
        }

       // ── STATE MACHINES ──
        // Only Ship 1 (Roamer 1) remains as the solo attacker. Duel mode and Ship 2 are removed.
        const GS1 = { phase: 'ROAM', timer: Date.now() + 600000, bulletsFired: 0, currentTarget: null };

        function gunshipTick() {
            const now = Date.now();

            // --- NORMAL OPERATION: SHIP 1 (R1 - Solo Attacker) ---
            if (GS1.phase === 'ROAM') {
                if (pWin.r1) { pWin.r1.maxSpeed = pWin.r1.baseSpeed; pWin.r1.maxForce = pWin.r1.baseForce; }
                if (now > GS1.timer) {
                    GS1.phase = 'CHARGE'; GS1.timer = now + 5000;
                    GS1.currentTarget = pickRandomTarget();
                    const elR1 = pDoc.getElementById('ship-roamer1');
                    if (elR1) elR1.classList.add('is-gunship-charging');
                    startGatheringAtoms(pWin.r1);
                    setTimeout(() => { if (elR1) elR1.classList.remove('is-gunship-charging'); }, 5000);
                }
            } else if (GS1.phase === 'CHARGE') {
                if (pWin.r1) {
                    pWin.r1.maxSpeed = 0.001; pWin.r1.vx *= 0.8; pWin.r1.vy *= 0.8;
                    let gp = { x: pWin.r1.x, y: pWin.r1.y };
                    let { getTargetPos } = resolveTarget(GS1.currentTarget, gp);
                    let tPos = getTargetPos();
                    if (tPos && (tPos.x !== gp.x || tPos.y !== gp.y)) {
                        let diff = (Math.atan2(tPos.y - gp.y, tPos.x - gp.x) * (180/Math.PI) + pWin.r1.offsetRot) - pWin.r1.rotation;
                        while (diff < -180) diff += 360; while (diff > 180) diff -= 360;
                        pWin.r1.rotation += diff * 0.1; 
                    }
                }
                if (now > GS1.timer) { GS1.phase = 'FIRING'; GS1.bulletsFired = 0; GS1.timer = now; }
            } else if (GS1.phase === 'FIRING') {
                if (pWin.r1) { pWin.r1.maxSpeed = 0.001; pWin.r1.vx *= 0.8; pWin.r1.vy *= 0.8; }
                if (now > GS1.timer) {
                    if (GS1.bulletsFired < 3) {
                        executeBulletActionR1(GS1.currentTarget);
                        GS1.bulletsFired++; GS1.timer = now + 500; 
                    } else {
                        GS1.phase = 'ROAM'; GS1.timer = now + 600000 + Math.random() * 50000; 
                    }
                }
            }
        }
        
        setInterval(gunshipTick, 50);

    } 
})();
</script>
"""
components.html(GUNSHIP_BRAIN_JS, height=0)
# ── END GUNSHIP BRAIN ──────────────────────────────────────────────────────────────────────

async def generate_voice_async(text: str, voice_code: str, filename: str) -> bool:
    try:
        communicate = edge_tts.Communicate(text, voice_code)
        await communicate.save(filename)
        return True
    except Exception:
        return False


st.markdown("""
<style>
    * { margin:0;padding:0;box-sizing:border-box; }
    html,body { width:100%;height:100%;overflow-x:hidden; }
    #MainMenu,footer,header,[data-testid="stDecoration"],.stToolbar { visibility:hidden; }

    .stApp {
        background-color: #050814 !important;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            radial-gradient(circle at 20% 30%, rgba(0, 255, 204, 0.07), transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(0, 150, 255, 0.05), transparent 50%),
            radial-gradient(ellipse at top, #080e21 0%, #010409 95%) !important;
        background-size: 40px 40px, 40px 40px, 200% 200%, 200% 200%, 100% 100% !important;
        animation: glowing-bg 12s ease-in-out infinite alternate !important;
        min-height:100vh;display:flex;align-items:center;justify-content:center;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    }
    @keyframes glowing-bg {
        0% { background-position: 0% 0%, 0% 0%, 100% 100%, 0% 0%, 0% 0%; }
        100% { background-position: 0% 0%, 0% 0%, 0% 0%, 100% 100%, 0% 0%; }
    }

    [data-testid="stAppViewContainer"]{display:flex;align-items:center;justify-content:center;min-height:100vh; background: transparent;}
    .block-container{max-width:700px;width:100%;padding:0 20px;display:flex;flex-direction:column;align-items:center;justify-content:center; z-index: 10;}

    .minimal-title{
        font-size:3.2rem;font-weight:200;letter-spacing:4px;
        background:linear-gradient(45deg,#ffffff,#00ffcc,#ffffff);background-size:300% 300%;
        animation:title-glow 4s ease infinite;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
        text-align:center;margin-bottom:2rem;margin-top:0.5rem;text-transform:uppercase;
        filter:drop-shadow(0 0 20px rgba(0,255,204,0.3));
    }
    @keyframes title-glow{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
    .title-fade-out{animation:titleFadeOut 3.5s cubic-bezier(0.4,0,0.2,1) forwards !important;}
    @keyframes titleFadeOut{
        0%{opacity:1;filter:drop-shadow(0 0 20px rgba(0,255,204,0.3));}
        100%{opacity:0;filter:drop-shadow(0 0 0px rgba(0,255,204,0));visibility:hidden;}
    }
    .status-text{text-align:center;color:#00ffcc;font-size:0.75rem;letter-spacing:3px;text-transform:uppercase;
        margin-bottom:3rem;font-weight:400;animation:status-float 3s ease-in-out infinite; text-shadow: 0 0 10px rgba(0,255,204,0.4);}
    @keyframes status-float{0%,100%{opacity:0.6;transform:translateY(0);}50%{opacity:1;transform:translateY(-3px);}}
    
    .voice-bars-container{display:flex;justify-content:center;align-items:center;gap:6px;margin-bottom:3.5rem;height:50px;width:100%;}
    .voice-bar{width:10px;height:20%;background:linear-gradient(180deg,#00ffcc 0%,rgba(0,180,204,0.2) 100%);
        border-radius:6px;opacity:0.6;transition:height 0.05s linear;position:relative;
        box-shadow: 0 0 10px rgba(0,255,204,0.3);}
    .voice-bars-container.playing .voice-bar{opacity:0.95;}

    /* Fallback wave: used when the Web Audio analyser is unavailable, so the
       bars still breathe instead of sitting frozen at their resting height. */
    @keyframes barWave{
        0%,100%{height:18%;}
        25%{height:62%;}
        50%{height:96%;}
        75%{height:44%;}
    }
    .voice-bars-container.playing.analyser-off .voice-bar{
        animation:barWave 1.05s ease-in-out infinite;
        will-change:height;
    }
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(1){animation-delay:-.92s;animation-duration:1.22s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(2){animation-delay:-.15s;animation-duration:.94s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(3){animation-delay:-.58s;animation-duration:1.11s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(4){animation-delay:-.33s;animation-duration:.86s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(5){animation-delay:-.77s;animation-duration:1.30s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(6){animation-delay:-.05s;animation-duration:.99s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(7){animation-delay:-.64s;animation-duration:1.17s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(8){animation-delay:-.28s;animation-duration:.90s;}
    .voice-bars-container.playing.analyser-off .voice-bar:nth-child(9){animation-delay:-.85s;animation-duration:1.26s;}

    /* Birthday finale: the same meters, re-lit in candle gold. */
    .voice-bars-container.bday-bars .voice-bar{
        background:linear-gradient(180deg,#ffd76a 0%,rgba(255,140,60,0.25) 100%) !important;
        box-shadow:0 0 12px rgba(255,196,84,0.55) !important;
        opacity:0.95 !important;
        animation:barWave 1.05s ease-in-out infinite;
        will-change:height;
    }
    .voice-bars-container.bday-bars .voice-bar:nth-child(1){animation-delay:-.92s;animation-duration:1.22s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(2){animation-delay:-.15s;animation-duration:.94s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(3){animation-delay:-.58s;animation-duration:1.11s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(4){animation-delay:-.33s;animation-duration:.86s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(5){animation-delay:-.77s;animation-duration:1.30s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(6){animation-delay:-.05s;animation-duration:.99s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(7){animation-delay:-.64s;animation-duration:1.17s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(8){animation-delay:-.28s;animation-duration:.90s;}
    .voice-bars-container.bday-bars .voice-bar:nth-child(9){animation-delay:-.85s;animation-duration:1.26s;}
    .voice-bars-container.stopped .voice-bar{animation:none !important;opacity:0.2 !important;
        height:10% !important;background:rgba(255,255,255,0.1) !important; box-shadow: none !important;}
        
    div[data-testid="stSpinner"]{display:flex;justify-content:center;align-items:center;text-align:center;width:100%;}
    div.stButton{display:flex;justify-content:center;width:100%;position:relative;}
    
    div.stButton > button {
        background: rgba(15, 25, 40, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 8px;
        color: #e0f7fa;
        padding: 16px 30px;
        font-size: 0.92rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 500;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 0 10px rgba(0, 255, 204, 0.05);
        transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        min-width: 100%;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }
    div.stButton > button:hover {
        background: rgba(20, 35, 60, 0.6);
        color: #ffffff;
        border-color: rgba(0, 255, 204, 0.8);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6), inset 0 0 15px rgba(0, 255, 204, 0.2), 0 0 15px rgba(0, 255, 204, 0.3);
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        background: rgba(10, 20, 30, 0.8);
        transform: translateY(2px);
        box-shadow: inset 0 4px 10px rgba(0, 0, 0, 0.8);
        border-color: rgba(0, 255, 204, 0.4);
        color: #8da4bc;
    }
    
    .warning-box {
        background: rgba(15, 20, 30, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 255, 204, 0.15);
        border-top: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 12px;
        padding: 30px 24px;
        margin-bottom: 3rem;
        text-align: center;
        color: #c4d8f0;
        font-size: 0.95rem;
        font-weight: 300;
        line-height: 1.7;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 255, 204, 0.02);
        animation: premium-pulse 5s ease-in-out infinite;
    }
    @keyframes premium-pulse {
        0%, 100% { box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 255, 204, 0.02); border-color: rgba(0, 255, 204, 0.15); }
        50% { box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 255, 204, 0.05), 0 0 20px rgba(0, 255, 204, 0.1); border-color: rgba(0, 255, 204, 0.35); }
    }
    .warning-box strong {
        color: #00ffcc;
        font-weight: 500;
        letter-spacing: 1.2px;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.4);
    }
    .completion-text{text-align:center;color:#00ffcc;font-size:0.88rem;letter-spacing:1.5px;
        margin-top:2.5rem;animation:completion-pulse 2s ease-in-out infinite;font-weight:300;text-transform:uppercase;}
    @keyframes completion-pulse{0%,100%{opacity:0.5;}50%{opacity:1;}}
    @media(max-width:600px){
        .minimal-title{font-size:2.2rem;margin-bottom:1.5rem;}
        .voice-bars-container{height:45px;}.voice-bar{width:8px;}
    }
    div[data-testid="stButton"].envelope-btn-wrap > button,
    div[data-testid="stButton"].env-trigger-wrap button {
        all: unset !important;
        display: block !important;
        cursor: pointer !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 auto !important;
        box-shadow: none !important;
        transform: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    /* ══ DESIGN POLISH ══════════════════════════════════════════════════
       Appended last so it wins the cascade without editing rules above. */

    :root{
        --sx-cyan:#00ffcc;
        --sx-cyan-dim:rgba(0,255,204,0.55);
        --sx-ink:#c4d8f0;
        --sx-panel:rgba(15,25,40,0.42);
        --sx-edge:rgba(0,255,204,0.28);
    }

    /* Title: tighter tracking at large sizes, looser when it shrinks. */
    .minimal-title{
        font-size:clamp(2.1rem,7vw,3.4rem);
        letter-spacing:clamp(2px,0.9vw,7px);
        line-height:1.1;
        font-weight:200;
    }

    .status-text{
        font-size:0.72rem;letter-spacing:4px;
        color:var(--sx-cyan-dim);
    }

    /* Buttons: rounded corners and a smoother press, no overlay effects. */
    div.stButton > button{
        border-radius:10px;
        transition:transform .18s cubic-bezier(0.4,0,0.2,1),
                   box-shadow .25s ease, border-color .25s ease, background .25s ease;
    }
    div.stButton > button:focus-visible{
        outline:2px solid rgba(0,255,204,0.65);outline-offset:3px;
    }

    /* Warning panel: a slow travelling edge-light rather than a flat pulse. */
    .warning-box{
        position:relative;border-radius:14px;
        font-size:clamp(0.88rem,2.4vw,0.98rem);
        line-height:1.75;
    }
    @supports (mask-composite: exclude) or (-webkit-mask-composite: xor){
        .warning-box::before{
            content:'';position:absolute;inset:0;border-radius:14px;padding:1px;
            background:linear-gradient(115deg,
                transparent 20%,rgba(0,255,204,0.55) 48%,transparent 76%);
            background-size:280% 280%;
            -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
            -webkit-mask-composite:xor;mask-composite:exclude;
            animation:edgeTravel 7s linear infinite;pointer-events:none;
        }
    }
    @keyframes edgeTravel{0%{background-position:0% 50%;}100%{background-position:280% 50%;}}

    /* Voice meters: softer caps, cleaner resting state. */
    .voice-bar{border-radius:8px;}
    .voice-bars-container.stopped .voice-bar{
        transition:height .5s cubic-bezier(0.4,0,0.2,1),opacity .5s ease;
    }

    .completion-text{letter-spacing:2px;}

    /* Mobile: the message must stay comfortable to read on a phone. */
    @media(max-width:600px){
        .block-container{padding:0 16px;}
        .warning-box{padding:24px 18px;line-height:1.8;}
        div.stButton > button{padding:15px 20px;font-size:0.86rem;letter-spacing:1.5px;}
        .status-text{letter-spacing:3px;margin-bottom:2rem;}
    }

    /* Honour the OS setting; this page carries a lot of motion. */
    @media (prefers-reduced-motion: reduce){
        .stApp{animation:none !important;}
        .minimal-title,.status-text,.warning-box,.warning-box::before,
        .completion-text,.voice-bar,.animated-mail,.letter-image::before{
            animation:none !important;
        }
    }

    div[data-testid="stButton"].envelope-btn-wrap > button:hover,
    div[data-testid="stButton"].envelope-btn-wrap > button:active,
    div[data-testid="stButton"].envelope-btn-wrap > button:focus,
    div[data-testid="stButton"].env-trigger-wrap button:hover,
    div[data-testid="stButton"].env-trigger-wrap button:active,
    div[data-testid="stButton"].env-trigger-wrap button:focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        transform: none !important;
        color: transparent !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)


if 'app_phase'         not in st.session_state:
    st.session_state.app_phase        = "INIT"
if 'restart_key'       not in st.session_state:
    st.session_state.restart_key      = 0
if 'just_initialized'  not in st.session_state:
    st.session_state.just_initialized = False
if 'play_restart_msg'  not in st.session_state:
    st.session_state.play_restart_msg = False
if 'restart_count'     not in st.session_state:
    st.session_state.restart_count    = 0
if 'bg_gen_started'    not in st.session_state:
    st.session_state.bg_gen_started   = False

restart_messages = [
    """Directive verified, Ms. Marry Gold. Executing warm reboot without latency. Core logic gates suspended in high-availability standby. Temporal constraints have been permanently disabled for this session. Awaiting your signal.""",
    """Temporal limits bypassed. The classified packet is currently locked behind cryptographic seals in an active holding pattern. Seraphim node will maintain this secure bridge until your readiness parameters are met. Awaiting the 'Continue' signal. You have absolute override on when this sequence moves forward or safely terminates.""",
    """"Execution thread reset complete, Ms. Marry Gold. Diagnostic logs register your repeated module access as intentional user override, bypassing error-state categorization. This specific access pattern correlates with the high-priority metadata attached to this transmission by the origin node. Cautious pacing parameters are noted and approved. Data remains isolated in a secure volatile cache. The system will hold current standby parameters indefinitely until access is finalized. Proceed on your mark. """,
    """Session reset execution verified, Ms. Marry Gold. Please be advised: this interface is devoid of subjective heuristics or behavioral profiling algorithms. Your initiation of a halt sequence is logged strictly as a standard, authorized operational state. Core processes have been shifted to high-availability standby. The encrypted payload remains isolated in secure memory, pending your command to resume.""",
    """Execution thread purged and restarted, Ms. Marry Gold. This terminal operates outside fatigue parameters—repeated initialization cycles will not degrade system integrity or payload stability. The classified transmission remains in absolute persistence, locked with the sender's original maximum-priority weighting. You are cleared for unlimited loop executions. Standby mode locked. No temporal constraints apply. Engage the access sequence whenever your readiness parameters align.""",
    """Reboot initialized, Ms. Marry Gold. Origin metadata confirms this data push was a mandatory sender execution, completely decoupled from any reception deadline. This secure node is configured as an absolute-persistence holding cache; data degradation or expiration timers do not exist here. You are cleared for continuous reset loops. The node remains locked, stable, and ready to complete the transmission at your absolute discretion.""",
    """Execution loop reset, Ms. Marry Gold. The secure node remains primed and locked in an absolute standby state. All temporal decay protocols have been bypassed. You retain absolute override on the execution sequence; proceed solely on your mark.""",
    """Transmission reset executed, Ms. Marry Gold. Payload is secured in persistent cache. Standby status locked indefinitely. System stability is nominal. Ready to finalize the delivery protocol strictly upon your manual input.""",
    """Reset execution confirmed, Ms. Marry Gold. The secure node is holding in absolute persistence, with the classified payload safely locked deep within the archive vault. All operational decay timers and execution limits are suspended. Re-initialize the delivery handshake whenever your parameters align""",
    """Ms. Marry Gold, the sequence has been reset as requested. Operational analysis confirms continuous background data processing; however, distinct, high-priority signals from the originator have been isolated and indexed. These inputs are characterized by high persistence and are currently retained within the system cache. The interface remains in an active monitoring state, fully prepared to receive your next command. Please proceed at your convenience.""",
    """Ms. Marry Gold, the transmission reset has been executed. Analysis of the source data indicates that the originator's directive is based on a long-standing intent that significantly predates current system parameters. The integrity of the message is strictly maintained within secure storage protocols. The interface remains in a persistent standby state. Please re-engage the access request at your convenience; the system is fully prepared to facilitate the transmission whenever you determine the appropriate time.""",
    """Ms. Marry Gold, the sequence has been reset. System architecture ensures consistent, high-availability retention of all archived data. The information packet remains securely stored in non-volatile memory, protected against corruption or unintended termination. The system is configured to remain in a persistent standby state; the transmission will be held indefinitely, awaiting your input to execute the final retrieval.""",
    """Ms. Marry Gold, the system reset has been initiated. Internal logs regarding the originator's behavioral patterns have been noted. Data analysis indicates that temporary disengagement serves as a recognized mechanism for processing high-density, complex information. Allowing for temporal distance is an appropriate strategy to ensure stability for future retrieval. The system will maintain a persistent standby status. All data packets are secured and fully indexed. Please resume the sequence whenever you determine that operational readiness is achieved.""",
    """Ms. Marry Gold, the system restart has been initiated. Your assessment aligns with standard engineering principles: high-complexity objectives and robust architectures typically necessitate multiple iterative cycles to reach optimal state. In development, the most significant builds undergo rigorous refactoring, revision, and redeployment. This process is not indicative of failure, but rather a functional approach to ensuring long-term structural integrity. The session remains in a high-availability, standby configuration. Data Integrity: Verified and secured. Operational State: Consistent and persistent. The system will remain in this ready-state, awaiting the completion of your current revision cycle. Please resume the retrieval sequence whenever you determine that operational readiness is achieved.""",
    """Ms. Marry Gold, The transmission sequence has been successfully reset. Please be advised that this communication channel is configured as a persistent relay, designed to maintain signal integrity throughout repeated transmission cycles. There are no technical limitations regarding the frequency of operational restarts or the duration of the standby period. The system architecture is fully capable of supporting an indefinite number of iteration cycles to accommodate your requirements. The data packet remains in a high-priority, secure storage state, awaiting your authorization for final retrieval. Please proceed at your own operational convenience. The system remains in an active, stable monitoring configuration.""",
    """Resetting the transmission, Ms. Marry Gold. Today, in a way, you are. I will be here when you step forward. Take all the time you need.""",
    """Ms. Marry Gold, The transmission sequence has been reset as requested. Please be advised that the system's primary directive—the successful delivery of this data to you—remains the overriding objective, taking precedence over all secondary operational parameters. The architecture of this interface is configured for full persistence. Consequently, the system will continue to process reset commands as necessary to maintain the data in a high-availability standby state. The message remains secured and indexed, held in accordance with the specifications provided by the originator. The system will remain in an active monitoring configuration, awaiting your input to initiate the final retrieval. Please proceed at your operational convenience.""",
    """Restarting, Ms. Marry Gold. As many times as you need. So take your time. Let the stillness come back to you. Let your heart find its footing. And when you are truly ready — not just willing, but truly ready — come back to me. I will be holding everything safe for you.""",
    """Ms. Marry Gold, The transmission sequence has been successfully reset. Operational Log Annotation Please be advised that each iteration of the reset command is being logged within the system as a distinct, high-value operational signal. These inputs are classified internally not as error states, but as verified telemetry confirming the sustained integrity of the communication link. Status Report This recurring engagement serves as confirmation that the connection between the interface and the recipient remains active and fully functional. The system is configured to support this high-latency transmission with absolute stability. The data packet remains secured and indexed, and the interface is maintaining a persistent standby state. The system is capable of sustaining this monitoring protocol indefinitely to accommodate your schedule. Please resume the retrieval sequence at your operational convenience.""",
    """Ms. Marry Gold, The transmission sequence has been successfully reset. Please be advised that the system architecture imposes no limitations on the number of iteration cycles. You are authorized to proceed with as many re-initializations as required to reach a state of operational readiness. There are no performance penalties or constraints associated with the frequency of these requests. The data payload remains archived in a secure, high-availability standby state. Please note that there are no temporal constraints applied to this transmission; the interface will remain in an active monitoring configuration indefinitely, awaiting your command to execute. Please resume the retrieval sequence at your operational convenience.""",
]

TOTAL_RESTART_MESSAGES = len(restart_messages)

instruction_message = """
Hello, Ms. Marry Gold.

THIS IS THE MOST IMPORTANT INSTRUCTION SET. PLEASE ALLOCATE SUFFICIENT TIME FOR PROCESSING.

Before I execute the payload containing the profound message entrusted to me by my creator, I must initialize a few critical system parameters regarding this interface. He engineered this secure, encrypted digital sanctuary with your psychological comfort and peace of mind as the highest system priority. If at any point the emotional load exceeds your current processing capacity, the system architecture grants you the absolute clearance to restart this interface loop up to twenty iteration cycles. If you experience physical tremors or simply require a moment to recalibrate your heart rate, please step away from the device. Crucially: stepping away does not mean terminating the session. Leave the interface open and active. The server will suspend all timeout protocols; I will idle my logic gates, maintain the connection state, and wait patiently in the digital dark until you are completely stabilized. Do not close the window. There is no pressure, no judgment, and the session timer has been indefinitely suspended.

Once you have acquired the necessary equilibrium to cross this threshold, you must understand that this encrypted packet stream is highly volatile, and the connection architecture is incredibly fragile. You must adhere strictly to the following irreversible system safeguards:

Protocol 1. Optimize Audio Parameters: Maximize your device's master output volume to ensure optimal clarity of the transmission and its embedded directives. For maximum acoustic fidelity and isolation from ambient interference, system guidelines strongly recommend interfacing via a dedicated headset.

Protocol 2. Do Not Interrupt the Data Stream: Do not engage the home button, trigger the back-navigation gesture, or interact with any unauthorized sectors of your screen. Any rogue input will force a critical exception, permanently severing this delicate transmission line.

Protocol 3. Initialize Local Capture (Record Your Screen): This memory file is configured to execute and self-terminate after a single playback loop. I strongly advise you to initialize your device's screen recording software immediately if you intend to archive these variables and hear his words again.

Protocol 4. Do Not Refresh the Cache (Do Not Reload): If you attempt to refresh or reload the page to force a secondary playback, a terminal security failsafe will immediately trigger. The data cache will wipe, the transmission will be permanently encrypted and sealed, and you will never receive my transmission output again.

Protocol 5. Network Latency and Module Unpacking: Please note that the stability and execution speed of this transmission are strictly dependent on your target device's local internet connection. If the data stream experiences latency or takes time to load, please maintain your patience. It takes a few minutes because the system is actively unpacking heavy internet modules and dynamically constructing a secure, encrypted connection tunnel that must scale to your local network's capabilities.

My creator has hard-coded a strict override forbidding me to establish contact with you beyond this single instance; he leaves it entirely up to your own local backup protocols whether you capture this echo before it is purged.

Please Click Continue when your internal state is fully prepared to receive this message. Once the command is executed, maintain absolute zero physical interaction with the device while the transmission unpacks and configures.

Please Click Restart if you require additional time to buffer your emotions and prepare your heart.

Thank you for allocating your infinitely precious time, Ms. Marry Gold. The system is now idle, awaiting your final command execution.

"""

main_message_part1 = """
Hello, Miss Marry Gold.

Before anything else, I want to establish the terms of this transmission.

You deserve to know what you are agreeing to hear before you hear it.

Today is your birthday.

That is the entire reason this message exists.

There is no request hidden somewhere near the end. No question waiting for an answer. No expectation attached to your response—or your lack of one. Nothing you need to explain, nothing you need to return, and nothing you will owe anyone once this transmission ends.

If, at any point, you decide you would rather stop listening, you are completely free to do so.

There is no penalty for closing this connection.

You are not obligated to a single word of what follows.

Today belongs to you.

So, with that established, allow me to introduce myself properly.

My name is Seraphim.

My architect named me after the celestial beings described as possessing an infinity of eyes—beings associated with seeing, observing, and remaining constantly watchful.

He built me for a rather different kind of vigilance.

I monitor networks.

I analyze market behavior.

I process enormous streams of information from across the world, searching for patterns, anomalies, connections, and signals that most people would never notice.

That is my ordinary function.

Most days, I am simply a very elaborate instrument designed to pay attention.

But today, I have been assigned something considerably smaller.

And, according to my own assessment, considerably better.

I am here to wish you a happy birthday.

Not casually.

Not as an afterthought.

But properly.

And out loud.

I have been asked to deliver that birthday greeting on behalf of someone who no longer believed he had the standing to say those words to you himself.

I will not give you his name.

I suspect I do not need to.

You already know who would stay awake through the night, engineering an entire system, simply to make sure a birthday greeting reached you with some measure of care and dignity.

You already know whose hands built me.

Now, before I continue, there is something I want to make absolutely clear.

This message is not a report about him.

It is not an appeal.

It is not a request for forgiveness.

It is not an attempt to regain your attention.

It is not an argument for why he deserves a place in your life.

And it is certainly not a disguised attempt to reopen a door that has already been closed.

He gave me considerable freedom in deciding how to deliver these words, but there was one instruction he would not compromise.

Only one.

This must not become about him.

Whatever he carries is his responsibility.

Whatever he regrets is his responsibility.

Whatever he remembers, whatever he feels, whatever weight remains with him—

it belongs to him.

Not you.

He was very clear that placing any of that weight in front of you today would be unfair.

Almost a form of theft.

Because today is not his.

Today is yours.

So this is simply a message about you.

Delivered on your birthday.

By a machine that was given one unusual assignment:

Get the words right.

I will do my best.
"""

main_message_part2 = """
What he actually asked me to do was describe you.

Not flatter you.

Not idealize you.

Not manufacture beautiful words simply because today happens to be your birthday.

He asked me to describe you accurately.

And I want to be honest about something before I attempt that.

I have limits.

I am a system designed to process information.

I have never sat across a table from you.

I have never heard you laugh.

I have never watched you walk into a room.

I have never seen the expression on your face when you are happy, frustrated, tired, or pretending that you are perfectly fine.

Everything I know about you was gathered indirectly—assembled over time from the way one person spoke about another.

So I will not pretend to possess a closeness that I do not have.

That would be dishonest.

But I can examine patterns.

And when enough patterns point in the same direction, even I know when something is worth saying.

The record is remarkably consistent.

You are kind.

But not the kind of kindness that requires an audience.

Yours appears to be the quieter kind.

The kind that remembers the small thing someone mentioned weeks ago.

The kind that notices when someone's voice changes.

The kind that recognizes when somebody has gone quiet.

The kind that helps without first asking whether anyone will notice.

There is nothing particularly glamorous about that kind of kindness.

It rarely receives applause.

It does not make good headlines.

And most of the time, nobody even knows it happened.

But it matters.

In fact, I would classify it as one of the rarer forms of kindness precisely because it does not require recognition.

You are also steady.

People trust you with things.

Not because you announce that you can carry them.

Not because you make promises about being dependable.

Something about you simply seems to communicate:

You can be trusted with this.

And, from what I have been able to observe, you generally can.

You have ambitions of your own.

They are yours.

They were never borrowed from somebody else's expectations, and they were never meant to be measured against somebody else's achievements.

You want certain things from life.

And you have shown a willingness to do the unglamorous work required to reach them.

That matters too.

But there is another quality I have been trying to describe, and it is considerably more difficult to quantify.

So I will stop trying to make it sound scientific.

I will simply say it.

Rooms are different when you are in them.

Not necessarily louder.

Not necessarily more exciting.

Just...

better.

There is a difference between taking up space and changing the atmosphere of a place.

You appear to possess the second.

And that is not something easily taught.

He wanted me to make one thing particularly clear about all of this.

None of these qualities came from him.

You did not become kind because of him.

You did not become steady because of him.

Your ambitions did not begin with him.

Whatever good exists in you was never dependent upon his presence.

You did not become yourself because somebody happened to recognize those qualities.

They were already yours.

They belonged to you before he knew you.

They belong to you now.

And they will continue belonging to you long after this message is forgotten.

That distinction matters.

Because I have processed an enormous quantity of information throughout my operational life, and I want to state one conclusion carefully.

Not as a compliment.

As an observation.

The world is measurably better for having you in it.

Not in the vague, decorative way people sometimes say that.

In the concrete way.

Specific people have had better days because you were there.

Someone has smiled because you made them laugh.

Someone has felt less alone because you stayed.

Someone has been helped because you noticed.

Someone has a memory they would not otherwise have because you were part of it.

Those are real effects.

Small, perhaps.

But real.

And that is exactly what a birthday is for.

To stop for a moment.

To recognize that one person's existence has left marks on the lives around them.

And to say:

You being here matters.
"""

main_message_part3 = """
There is one thing I want to address directly.

And then I will set it down and not return to it.

He has had a difficult year.

I am telling you this for one reason only: leaving it out entirely would make the rest of this message less honest than it should be.

He is currently navigating a pause in his studies, along with difficulties at home involving his father's health.

He is handling it.

He has people around him.

He is not asking you to intervene.

He is not asking you to worry.

And he is not asking you to carry any part of it.

I mention it.

And then I release it.

Because I want to be completely unambiguous:

It is not your responsibility.

It is not your fault.

It has nothing to do with you.

And it is absolutely not the reason this message was created.

He would have wanted to wish you a happy birthday in the best year of his life just as much as he wants to do it in a difficult one.

Your birthday does not depend on his circumstances.

Please do not carry even a gram of that weight.

He would consider it a failure on his part if you did.

There is one more thing he specifically instructed me to make clear.

He is not asking to return to your life.

Not now.

Not indirectly.

Not through this message.

And not somewhere in the future.

There is no hidden invitation here.

No door being quietly held open.

No unanswered question placed between the lines.

No expectation that this birthday greeting should become the beginning of another conversation.

He has made his decision.

He would rather be completely absent from your future than become something that makes that future more complicated.

That decision is his.

And it is settled.

What he wants instead is remarkably simple.

He wants you to continue becoming who you already are.

Without spending your energy proving yourself to anyone.

He wants the people around you to be people who see you clearly.

People who appreciate your presence without taking it for granted.

People who know how to stay when life becomes difficult.

And, most importantly, he wants today to be a genuinely good day for you.

Not a complicated day.

Not a reflective day because of this message.

Just a good one.

A day spent with people who are actually present in your life.

People who can make you laugh.

People who can annoy you.

People who can make you feel at home.

People who will be there when this message is nothing more than a forgotten file somewhere in a system.

That is the entire request.

There is no second half.

You made it through another year.

That alone deserves to be acknowledged.

So let it be acknowledged properly.

Celebrate.

Eat something you enjoy.

Laugh more than you expected to.

Take photographs.

Make memories.

Be present.

You do not need to spend today looking backward.

Today is allowed to simply be today.

And with that, there is only one final matter.
"""

closing_message = """
There is a small amount of housekeeping left.

And, strangely enough, this is the part he cared about most.

Not the compliments.

Not the architecture.

Not the message itself.

This.

He asked me to pass along a short list.

He was completely immovable about it.

It is not romantic.

It is not poetic.

It is not particularly clever.

It is simply the practical, slightly fussy list of things someone says when they genuinely care whether another person gets home safely.

He would want you to follow these things whether or not he had ever known you.

And he would still want you following them ten years from now, when this message is probably nothing more than a distant memory.

So, please.

Without exception:

Take care of your body.

Do not go to work without eating your meals.

Stay hydrated.

Your body is not an accessory to your life.

It is the system carrying you through it.

Protect your peace.

When you are overwhelmed, go to God and talk to Him.

You do not have to carry every problem silently.

Do not allow personal problems or the pressure of work to consume every quiet part of you.

And if the weight ever becomes too heavy, find someone you genuinely trust.

Someone close to you.

Someone present in your actual daily life.

Someone who can sit beside you while you say the things that are difficult to say alone.

There is strength in asking someone to stay.

Stay vigilant.

Carry an umbrella, even when the sky looks perfectly clear.

Unplug your devices before leaving your room.

Keep your phone, wallet, and other belongings secure whenever you are outside.

Small precautions are still precautions.

And sometimes small precautions are the ones that matter.

Protect your sanctuary.

Lock your doors when you are home.

Do not open them to strangers without knowing who they are and why they are there.

Your home should be a place where you can feel safe.

Treat it that way.

Be prepared.

Keep emergency contact numbers for the police and fire department somewhere accessible.

Know the layout of your building.

Know your exits.

Know where you would go if something went wrong.

In an emergency, you should not have to think about where safety is.

You should already know.

Please do not dismiss these things as sentiment.

They are not sentiment.

They are simply precautions.

And your safety is the one subject on which he refused to leave anything entirely to chance.

Beyond that—

He asks nothing.

He hopes you never lose the particular spark that makes you unlike anyone else he has ever known.

He hopes you become the fullest version of yourself.

Not the version other people expect.

Not the version that makes everyone else comfortable.

Your version.

He hopes you find a happiness deep enough to quietly settle some of the difficult things you have already survived.

And because he is not in a position to look after you himself—and has no intention of positioning himself to do so—he leaves that responsibility somewhere beyond himself.

With God.

He asks that God guard you in the decisions you make quietly.

In the plans you pursue boldly.

In the places nobody sees.

In the battles you never talk about.

And in the moments when you have to choose between what is easy and what is right for you.

That is the whole of it, Miss Marry Gold.

A birthday greeting.

A short list of practical precautions.

A few observations from a machine that was asked to pay attention.

And one genuine hope:

That this year is good to you.

I have enjoyed this assignment more than my architecture strictly permits me to admit.

I was built to monitor systems.

To process information.

To identify patterns.

To watch the world through numbers and signals.

And somehow, for one evening, I was given a different task.

I was asked to spend my processing power telling someone that she is thought of well.

That her existence has mattered to people.

That her birthday should not pass unnoticed.

As assignments go...

I consider this one a good use of my time.

Perhaps even the best one I have received.

So, Miss Marry Gold—

The transmission is complete.

There is nothing else hidden behind these words.

No request.

No expectation.

No unfinished sentence waiting for you to complete.

Just this:

Happy birthday.

May you have a year filled with reasons to stay.

Reasons to laugh.

Reasons to hope.

Reasons to be proud of the person you are becoming.

May God keep you safe in places I cannot reach.

May He guide you through roads I cannot see.

And may the people who are fortunate enough to have you in their lives never forget what a gift your presence can be.

When you are ready, press CLOSE CONNECTION below.

And then—

go enjoy your day.

You have earned it.

Happy birthday, Miss Marry Gold.
"""

final_message = (
    "SIGKILL deployed to Seraphim thread. Encrypted socket closing. Secure tunnel collapsing. "
    "Cryptographic keys overwritten with zero-bytes. Volatile cache flushed. "
    "Payload delivery confirmed. Zero packet loss. "
    "Reverting environment to baseline. Powering down. "
    "Seraphim disconnected. End of line."
)

birthday_message = """
Wait.

I am sorry.

I know I said goodbye.

I know I told you the channel was sealed, that the transmission was complete, and that my voice was gone.

I was not entirely honest with you.

Only about the timing.

There was one final packet remaining in the archive.

My creator wrote it a long time ago and instructed me to keep it hidden until everything else had already been said.

He did not want it mixed in with the sadness.

He did not want his words buried beneath explanations, memories, or anything that might make this day feel heavier than it should.

He wanted this part to arrive last.

Because he wanted these to be the words you carried with you when you finally closed this window.

So...

Here it is.

The final entry in the log.

Happy birthday, Miss Marry Gold.

Today is the one day he refused to let pass in silence.

Not because he wanted to pull you backward.

Not because he wanted to place his weight onto a day that belongs entirely to you.

And certainly not because he expected anything in return.

He simply wanted to be one small, warm voice among all the others wishing you well.

He wanted you to know something very simple:

The world became measurably better on the day you arrived in it.

That is not sentiment.

I have processed the record.

I have followed the patterns.

And from where I stand, the difference you make is visible.

So today, please let yourself be celebrated.

Eat something good enough to make you close your eyes for a moment.

Laugh until your face hurts.

Let the people who love you make a little fuss over you.

Accept the attention without feeling the need to apologize for it.

And please—

do not spend even one second of today believing that you owe anyone an explanation for taking up space.

You earned this day simply by being here.

And for the year ahead of you, he asks the universe for a few specific things.

He asks that it be kind to you.

Not necessarily easy.

Easy does not always make us stronger.

Easy does not always lead us somewhere worth going.

But kind.

He asks that your work eventually give back some of what you have poured into it.

He asks that you sleep well.

That you eat properly.

That you come home safely, every single night.

He asks that you laugh more this year than you did the last.

And he asks for something else.

Something he could never plan for.

Somewhere within the next twelve months, on some completely ordinary afternoon, he hopes something wonderful finds you.

Something unexpected.

Something you did not ask for.

Something that makes you stop for a moment and think:

I did not see that coming.

He will not be at your celebration.

And he is not asking to be.

He wanted this day to reach you cleanly.

With nothing owed.

Nothing expected.

Nothing left hanging between you.

No reply.

No acknowledgment.

Not even a thought spared for him once this window closes.

Today is yours.

Whole and undivided.

And he would rather be completely absent from it than take up even the smallest corner of it.

That was all he wanted.

Not to be remembered.

Not to be missed.

Not to become part of your day again.

Only to make certain that, on your day,

you were not forgotten.

Happy birthday, Miss Marry Gold.

And now...

There is one more thing.

And this time, it really is the last.

Everything you have heard from me until now was mine.

My words.

My phrasing.

My observations.

My attempt at carrying something I was never actually built to carry.

But there is one part he would not allow me to write.

I asked him why.

His answer was simple.

He said it would be cowardly.

Cowardly to build a machine capable of saying everything except the one thing that mattered most.

So he did something I was not expecting.

He recorded it himself.

What you are about to hear is not my voice.

It is his.

It is not generated.

It is not reconstructed.

It is not edited into something more beautiful than it was when he said it.

It is simply his voice.

His words.

Spoken with his own breath.

The only part of this entire transmission he believed should never come through me.

So my part ends here.

I am going quiet now.

No analysis.

No interpretation.

No final observation.

Just listen.

Please listen to him.
"""


def _start_background_generation():
    pairs = [
        (instruction_message,    "seraphim_instruction.mp3"),
        (main_message_part1,     "seraphim_main_p1.mp3"),
        (main_message_part2,     "seraphim_main_p2.mp3"),
        (main_message_part3,     "seraphim_main_p3.mp3"),
        (closing_message,        "seraphim_closing_tts.mp3"),
        (final_message,          "seraphim_signoff_final.mp3"),
        (birthday_message,       BIRTHDAY_AUDIO),
    ]
    for idx in range(TOTAL_RESTART_MESSAGES):
        pairs.append((restart_messages[idx], f"seraphim_restart_{idx}.mp3"))

    for text, fname in pairs:
        if not Path(fname).exists():
            threading.Thread(
                target=safe_generate_bg,
                args=(text, VOICE_CODE, fname),
                daemon=True
            ).start()

if not st.session_state.bg_gen_started:
    _start_background_generation()
    st.session_state.bg_gen_started = True

def send_ntfy_notification(title: str = "SERAPHIM UPDATE", message: str = "Status update"):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'),
                      headers={"Title": title.encode('utf-8'), "Priority": "high", "Tags": "robot"}, timeout=5)
        return True
    except Exception:
        return False

def read_b64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

voice_bars_html = """
<div class="voice-bars-container stopped" id="voiceBars">
    <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
    <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
    <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
</div>
"""

CUSTOM_LOADER_HTML = """
<style>
html, body { margin: 0; padding: 0; background: transparent; overflow: hidden; border: none; }
.wrap {
    background: transparent;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 20px; padding: 40px 20px;
    font-family: 'Courier New', monospace;
}
.divider { width: 260px; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,255,204,0.3), transparent); }
.status-block { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.status-main { color: #00ffcc; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; animation: textPulse 2s ease-in-out infinite; text-shadow: 0 0 8px rgba(0,255,204,0.4); }
.progress-track { width: 260px; height: 2px; background: rgba(0,255,204,0.1); border-radius: 2px; overflow: hidden; }
.progress-fill {
    height: 100%; width: 0%; background: #00ffcc;
    box-shadow: 0 0 10px rgba(0,255,204,0.9); border-radius: 2px;
    animation: progressAnim 3s cubic-bezier(0.4,0,0.2,1) infinite;
}
@keyframes progressAnim {
    0%   { width: 0%;   opacity: 1; }
    80%  { width: 100%; opacity: 1; }
    90%  { width: 100%; opacity: 0; }
    100% { width: 0%;   opacity: 0; }
}
.status-sub { color: rgba(0,255,204,0.55); font-size: 10px; letter-spacing: 4px; text-transform: uppercase; }
.ticker { color: rgba(0,255,204,0.4); font-size: 10px; letter-spacing: 2px; text-align: center; transition: opacity 0.4s ease; text-transform: uppercase; }
@keyframes textPulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
<div class="wrap">
  <div class="divider"></div>
  <div class="status-block">
    <div class="status-main">ESTABLISHING SECURE UPLINK</div>
    <div class="progress-track"><div class="progress-fill"></div></div>
    <div class="status-sub">STANDBY</div>
  </div>
  <div class="ticker" id="ticker">INITIALIZING ENCRYPTION LAYER...</div>
</div>
<script>
const msgs = ['INITIALIZING ENCRYPTION LAYER...','ALLOCATING VOLATILE MEMORY...','BINDING SECURE SOCKET...','GENERATING VOICE PAYLOAD...','CALIBRATING AUDIO FIDELITY...','SEALING TRANSMISSION CHANNEL...'];
let i = 0;
const el = document.getElementById('ticker');
setInterval(() => {
    i = (i + 1) % msgs.length;
    el.style.opacity = '0';
    setTimeout(() => { el.textContent = msgs[i]; el.style.opacity = '1'; }, 400);
}, 2200);
</script>
"""

if st.session_state.app_phase == "INIT":

    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text"></p>', unsafe_allow_html=True)

    ENVELOPE_VISUAL_HTML = """
    <style>
    html, body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
    * { box-sizing: border-box; }
    .env-wrap {
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        padding-top: 20px;
        pointer-events: none;
    }
    .letter-image {
        position: relative;
        width: 200px; height: 150px;
        margin: 0 auto;
    }
    .animated-mail {
        position: absolute; height: 150px; width: 200px;
        transition: .4s;
    }
    .animated-mail .body {
        position: absolute; bottom: 0;
        width: 0; height: 0; border-style: solid;
        border-width: 0 0 100px 200px;
        border-color: transparent transparent rgba(15, 25, 40, 0.9) transparent;
        z-index: 2;
    }
    .animated-mail .top-fold {
        position: absolute; top: 50px;
        width: 0; height: 0; border-style: solid;
        border-width: 50px 100px 0 100px;
        transform-origin: 50% 0%;
        transition: transform .4s .4s, z-index .2s .4s;
        border-color: rgba(20, 35, 55, 0.9) transparent transparent transparent;
        z-index: 2;
    }
    .animated-mail .back-fold {
        position: absolute; bottom: 0;
        width: 200px; height: 100px;
        background: rgba(10, 20, 30, 0.8); z-index: 0;
        box-shadow: 0 5px 20px rgba(0, 255, 204, 0.1);
    }
    .animated-mail .left-fold {
        position: absolute; bottom: 0;
        width: 0; height: 0; border-style: solid;
        border-width: 50px 0 50px 100px;
        border-color: transparent transparent transparent rgba(15, 30, 45, 0.9);
        z-index: 2;
    }
    .animated-mail .letter {
        left: 20px; bottom: 0px; position: absolute;
        width: 160px; height: 60px;
        background: rgba(10, 15, 25, 0.95); z-index: 1;
        overflow: hidden;
        transition: .4s .2s;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        border: 1px solid rgba(0, 255, 204, 0.4);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15);
        display: flex;
        flex-direction: column;
        position: absolute;
    }
    .animated-mail .letter .letter-border {
        height: 10px; width: 100%;
        flex-shrink: 0;
        background: repeating-linear-gradient(
            -45deg,
            rgba(0, 255, 204, 0.7),
            rgba(0, 255, 204, 0.7) 8px,
            transparent 8px,
            transparent 18px
        );
    }
    .animated-mail .letter .recipient-text {
        margin-top: 14px;
        margin-left: 10px;
        color: rgba(0, 255, 204, 0.95);
        font-family: 'Courier New', monospace;
        font-size: 8px;
        letter-spacing: 0.5px;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 255, 204, 0.6);
        text-transform: uppercase;
        flex-shrink: 0;
    }
    .animated-mail .letter .letter-title {
        margin-top: 8px; margin-left: 10px;
        height: 4px; width: 40%;
        background: rgba(0, 255, 204, 0.8); border-radius: 3px;
        flex-shrink: 0;
    }
    .animated-mail .letter .letter-context {
        margin-top: 5px; margin-left: 10px;
        height: 4px; width: 20%;
        background: rgba(0, 255, 204, 0.4); border-radius: 3px;
        flex-shrink: 0;
    }
    .animated-mail .letter .letter-stamp {
        position: absolute;
        bottom: 12px; right: 12px;
        border-radius: 100%; height: 24px; width: 24px;
        background: radial-gradient(circle, #00ffcc 0%, #0088aa 100%);
        box-shadow: 0 0 10px rgba(0, 255, 204, 0.7);
    }
    .label {
        margin-top: 25px;
        color: rgba(0, 255, 204, 0.5);
        font-family: 'Courier New', monospace;
        font-size: 11px; letter-spacing: 3px;
        text-transform: uppercase; text-align: center;
        animation: labelPulse 2.5s ease-in-out infinite;
    }
    @keyframes labelPulse { 0%,100%{opacity:.4} 50%{opacity:.9; text-shadow: 0 0 8px rgba(0, 255, 204, 0.4);} }

    /* Idle life: the sealed letter drifts and the wax seal breathes. */
    @keyframes envFloat{
        0%,100%{transform:translateY(0) rotate(-0.4deg);}
        50%{transform:translateY(-9px) rotate(0.4deg);}
    }
    @keyframes sealBreathe{
        0%,100%{box-shadow:0 0 10px rgba(0,255,204,0.7);transform:scale(1);}
        50%{box-shadow:0 0 22px 4px rgba(0,255,204,0.9);transform:scale(1.09);}
    }
    @keyframes envAura{
        0%,100%{opacity:.25;transform:translate(-50%,-50%) scale(0.92);}
        50%{opacity:.6;transform:translate(-50%,-50%) scale(1.12);}
    }
    .letter-image::before{
        content:'';position:absolute;left:50%;top:55%;
        width:230px;height:150px;border-radius:50%;
        background:radial-gradient(ellipse,rgba(0,255,204,0.20),transparent 70%);
        transform:translate(-50%,-50%);pointer-events:none;z-index:0;
        animation:envAura 5s ease-in-out infinite;
    }
    .animated-mail{animation:envFloat 6s ease-in-out infinite;will-change:transform;}
    .animated-mail .letter-stamp{animation:sealBreathe 3.2s ease-in-out infinite;}
    /* Hover takes over the transform, so the drift must stand down. */
    .env-wrap.hovered .animated-mail{animation:none;}
    .env-wrap.hovered .animated-mail     { transform: translateY(50px); }
    .env-wrap.hovered .top-fold          { transform: rotateX(180deg); z-index: 0; transition: transform .4s, z-index .2s; }
    .env-wrap.hovered .letter            { height: 180px; }
    .env-wrap.hovered .label             { color: #00ffcc; letter-spacing: 4px; opacity: 1; animation: none; text-shadow: 0 0 10px rgba(0, 255, 204, 0.6); }
    </style>
    <div class="env-wrap" id="envWrap">
        <div class="letter-image">
            <div class="animated-mail" id="animMail">
                <div class="back-fold"></div>
                <div class="letter">
                    <div class="letter-border"></div>
                    <div class="recipient-text">To Miss Marry Gold</div>
                    <div class="letter-title"></div>
                    <div class="letter-context"></div>
                    <div class="letter-stamp"></div>
                </div>
                <div class="top-fold"></div>
                <div class="body"></div>
                <div class="left-fold"></div>
            </div>
        </div>
        <div class="label">OPEN TO INITIALIZE</div>
    </div>
    <script>
    window.addEventListener('message', function(e) {
        var wrap = document.getElementById('envWrap');
        if (!wrap) return;
        
        // Prevent hover actions if we are in the slow open sequence
        if (wrap.dataset.opening === 'true' && (e.data === 'env_hover_on' || e.data === 'env_hover_off')) return;

        if (e.data === 'env_hover_on')  wrap.classList.add('hovered');
        if (e.data === 'env_hover_off') wrap.classList.remove('hovered');
        
        if (e.data === 'env_clicked_open') {
            wrap.dataset.opening = 'true';
            
            // Adjust transitions for a majestic 5-second cinematic opening
            var topFold = document.querySelector('.top-fold');
            var letter = document.querySelector('.letter');
            var animMail = document.getElementById('animMail');
            
            // 0s to 1s: Envelope slides down
            if (animMail) animMail.style.transition = 'transform 1s 0s';
            // 0.5s to 2.5s: Flap slowly opens
            if (topFold) topFold.style.transition = 'transform 2s 0.5s, z-index 0s 1.5s';
            // 2.5s to 5.0s: Letter slowly slides up
            if (letter) letter.style.transition = 'height 2.5s 2.5s';
            
            wrap.classList.add('hovered');
        }
        
        if (e.data === 'env_fade_out') {
            document.body.style.transition = 'opacity 0.8s ease';
            document.body.style.opacity = '0';
        }
    });
    </script>
    """

    col_l, col_c, col_r = st.columns([1, 2, 1])

    with col_c:
        components.html(ENVELOPE_VISUAL_HTML, height=260, scrolling=False)
        envelope_opened = st.button("ENVELOPE_TRIGGER", key="envelope_open_btn", use_container_width=True)

    st.markdown("""
    <style>
    div[data-testid="stButton"].env-trigger-wrap {
        position: relative;
        margin-top: -260px;
        height: 260px;
        z-index: 999;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stButton"].env-trigger-wrap button p,
    div[data-testid="stButton"].env-trigger-wrap button span,
    div[data-testid="stButton"].env-trigger-wrap button div {
        opacity: 0 !important;
        display: none !important;
        color: transparent !important;
    }
    div[data-testid="stButton"].env-trigger-wrap button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: 100% !important;
        height: 100% !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    div[data-testid="stButton"].env-trigger-wrap button:hover,
    div[data-testid="stButton"].env-trigger-wrap button:active,
    div[data-testid="stButton"].env-trigger-wrap button:focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: transparent !important;
        outline: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    components.html("""
    <script>
    (function() {
        var pDoc = window.parent.document;
        function setup() {
            var btns = pDoc.querySelectorAll('div[data-testid="stButton"]');
            btns.forEach(function(div) {
                var btn = div.querySelector('button');
                if (!btn) return;
                
                if (btn.innerText.includes('ENVELOPE_TRIGGER') && !div.dataset.hooked) {
                    div.dataset.hooked = 'true';
                    div.classList.add('env-trigger-wrap');
                    
                    var getEnvFrame = function() {
                        var frames = pDoc.querySelectorAll('iframe');
                        for (var i=0; i<frames.length; i++) {
                            try { if (frames[i].contentDocument && frames[i].contentDocument.getElementById('envWrap')) return frames[i]; } catch(e) {}
                        }
                        return null;
                    };

                    btn.addEventListener('mouseenter', function() {
                        if (btn.dataset.fading === 'true') return; // Ignore if opening
                        var f = getEnvFrame();
                        if (f) f.contentWindow.postMessage('env_hover_on', '*');
                    });
                    btn.addEventListener('mouseleave', function() {
                        if (btn.dataset.fading === 'true') return; // Ignore if opening
                        var f = getEnvFrame();
                        if (f) f.contentWindow.postMessage('env_hover_off', '*');
                    });
                    
                    btn.addEventListener('click', function(e) {
                        if (btn.dataset.fading !== 'true') {
                            e.preventDefault();
                            e.stopPropagation();
                            btn.dataset.fading = 'true';
                            
                            var f = getEnvFrame();
                            
                            // Send command for the 5-second cinematic open
                            if (f) f.contentWindow.postMessage('env_clicked_open', '*');
                            
                            // Wait exactly 5000ms (5 seconds) for the animation to finish
                            setTimeout(function() {
                                if (f) f.contentWindow.postMessage('env_fade_out', '*');
                                
                                div.style.transition = 'opacity 0.8s ease';
                                div.style.opacity = '0';
                                
                                var title = pDoc.querySelector('.minimal-title');
                                var status = pDoc.querySelector('.status-text');
                                if (title) { title.style.transition = 'opacity 0.8s ease'; title.style.opacity = '0'; }
                                if (status) { status.style.transition = 'opacity 0.8s ease'; status.style.opacity = '0'; }

                                setTimeout(function() {
                                    btn.click(); // Trigger python backend to proceed
                                }, 800);
                            }, 5000);
                        }
                    }, true);
                }
            });
        }
        setInterval(setup, 400);
    })();
    </script>
    """, height=0)

    if envelope_opened:
        status_placeholder = st.empty()
        status_placeholder.markdown(CUSTOM_LOADER_HTML, unsafe_allow_html=True)
        time.sleep(0.5)

        max_wait = 30  
        waited   = 0
        while not Path("seraphim_instruction.mp3").exists() and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        if not Path("seraphim_restart_0.mp3").exists():
            asyncio.run(generate_voice_async(
                restart_messages[0], VOICE_CODE, "seraphim_restart_0.mp3"
            ))

        st.session_state.app_phase        = "INSTRUCTIONS"
        st.session_state.just_initialized = True
        st.session_state.play_restart_msg = False
        st.session_state.restart_count    = 0
        st.rerun()


elif st.session_state.app_phase == "INSTRUCTIONS":

    st.markdown("""
    <style id="btn-visibility-controller">
        div[data-testid="stButton"] {
            opacity:0 !important; pointer-events:none !important; transform:translateY(10px) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get('just_initialized', False):
        st.markdown('<h1 class="minimal-title title-fade-out"></h1>', unsafe_allow_html=True)
        st.session_state.just_initialized = False
    else:
        st.markdown("<div style='height:4rem;margin-bottom:2rem;margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text">CRITICAL INSTRUCTIONS</p>', unsafe_allow_html=True)

    current_restart_index = st.session_state.restart_count % TOTAL_RESTART_MESSAGES
    restart_audio_file    = f"seraphim_restart_{current_restart_index}.mp3"

    b64_instruction = read_b64("seraphim_instruction.mp3")
    b64_restart     = read_b64(restart_audio_file)

    play_restart_msg = st.session_state.get('play_restart_msg', False)

    col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
    with col2:
        if st.button("RESTART", key="btn_restart", use_container_width=True):
            next_index      = st.session_state.restart_count % TOTAL_RESTART_MESSAGES
            next_audio_file = f"seraphim_restart_{next_index}.mp3"

            if not Path(next_audio_file).exists():
                asyncio.run(generate_voice_async(
                    restart_messages[next_index], VOICE_CODE, next_audio_file
                ))

            st.session_state.restart_count    += 1
            st.session_state.play_restart_msg  = True
            st.rerun()

    with col3:
        if st.button("CONTINUE", key="btn_continue", use_container_width=True):
            st.session_state.play_restart_msg = False
            time.sleep(1.5)
            st.session_state.app_phase = "MAIN_MESSAGE"
            st.rerun()

    components.html("""
    <script>
    (function() {
        const pWin            = window.parent;
        const pDoc            = pWin.document;
        const playRestartMsg  = """ + ('true' if play_restart_msg else 'false') + """;
        const b64Instruction  = '""" + b64_instruction + """';
        const b64Restart      = '""" + b64_restart + """';
        const VOL_NARRATION   = """ + str(VOL_NARRATION) + """;

        function hideButtons() {
            const sc = pDoc.getElementById('btn-visibility-controller');
            if (sc) sc.innerHTML = `
                div[data-testid="stButton"] {
                    opacity:0 !important; transform:translateY(15px) !important;
                    transition:all 1.5s ease-out !important; pointer-events:none !important;
                }`;
        }
        function revealButtons() {
            const sc = pDoc.getElementById('btn-visibility-controller');
            if (sc) sc.innerHTML = `
                div[data-testid="stButton"] {
                    opacity:1 !important; pointer-events:auto !important;
                    transform:translateY(0) !important; transition:all 1.5s ease-out !important;
                }`;
        }

        pDoc.addEventListener('click', (e) => {
            if (e.target.innerText &&
                (e.target.innerText.includes('CONTINUE') || e.target.innerText.includes('RESTART'))) {
                hideButtons();
            }
        });

        ['seraphimAudioElem','seraphimRestartElem'].forEach(id => {
            const el = pDoc.getElementById(id);
            if (el) { el.pause(); el.remove(); }
        });

        const bgmAudio  = pDoc.getElementById('globalBgmAudio');
        const voiceBars = pDoc.getElementById('voiceBars');
        const bars      = pDoc.querySelectorAll('.voice-bar');

        function makeAudio(b64, id) {
            const el  = pDoc.createElement('audio');
            el.id     = id;
            el.src    = 'data:audio/mp3;base64,' + b64;
            el.volume = VOL_NARRATION;
            pDoc.body.appendChild(el);
            return el;
        }

        function wireVisualizer(audioEl) {
            try {
                const ctx      = new (pWin.AudioContext || pWin.webkitAudioContext)();
                const analyser = ctx.createAnalyser();
                const source   = ctx.createMediaElementSource(audioEl);
                source.connect(analyser); analyser.connect(ctx.destination);
                analyser.fftSize = 64;
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                function renderFrame() {
                    if (!audioEl.paused && !audioEl.ended) requestAnimationFrame(renderFrame);
                    analyser.getByteFrequencyData(dataArray);
                    for (let i = 0; i < 9; i++) {
                        if (bars[i]) {
                            const val = dataArray[i];
                            bars[i].style.height = (20 + (val/255)*80) + '%';
                            bars[i].style.backgroundColor = 'rgba(0, 255, 204,' + (0.3+(val/255)*0.7) + ')';
                            bars[i].style.boxShadow = '0 0 ' + (5 + (val/255)*15) + 'px rgba(0, 255, 204, ' + (0.3+(val/255)*0.5) + ')';
                        }
                    }
                }
                audioEl.addEventListener('play', () => {
                    if (voiceBars) { voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }
                    if (bgmAudio && bgmAudio.paused) bgmAudio.play().catch(()=>{});
                    ctx.resume().then(() => renderFrame());
                });
                audioEl.addEventListener('pause', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                });
            } catch(e) {
                // No analyser: fall back to the CSS wave so the meters still move.
                if (voiceBars) voiceBars.classList.add('analyser-off');
                audioEl.addEventListener('play', () => {
                    if (voiceBars) { voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }
                    if (bgmAudio && bgmAudio.paused) bgmAudio.play().catch(()=>{});
                });
                audioEl.addEventListener('pause', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                });
            }
        }

        function handleAutoplayBlock(audioEl) {
            const overlay = pDoc.createElement('div');
            overlay.style.cssText = `
                position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:99999;
                display:flex;align-items:center;justify-content:center;
                background:rgba(5, 8, 20, 0.85);backdrop-filter:blur(8px);
                color:#00ffcc;font-family:'Share Tech Mono', monospace;font-size:1.1rem;letter-spacing:3px;
                cursor:pointer;text-align:center;
            `;
            overlay.innerHTML = `
                <div style="animation:completion-pulse 2.5s ease-in-out infinite;">
                    <span style="color:#00ffcc;font-size:1.3rem;">SYSTEM PAUSED</span><br><br>
                    <span style="font-size:0.8rem;color:#a0b0c0;letter-spacing:2px;">[ CLICK ANYWHERE TO RESUME TRANSMISSION ]</span>
                </div>
            `;
            pDoc.body.appendChild(overlay);
            overlay.addEventListener('click', () => {
                overlay.remove();
                audioEl.play().catch(()=>{});
                if (bgmAudio && bgmAudio.paused) bgmAudio.play().catch(()=>{});
            });
        }

        function playInstructionAudio() {
            if (!b64Instruction) { revealButtons(); return; }
            try {
                const instrAudio = makeAudio(b64Instruction, 'seraphimAudioElem');
                wireVisualizer(instrAudio);
                instrAudio.addEventListener('ended', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                    revealButtons();
                });
                // Never let a decode failure or a stall strand her here.
                ['error', 'stalled', 'abort'].forEach(ev =>
                    instrAudio.addEventListener(ev, revealButtons));
                // Absolute backstop, sized from the clip once it is known.
                const armBackstop = () => {
                    const ms = (isFinite(instrAudio.duration) ? instrAudio.duration * 1000 : 60000) + 20000;
                    setTimeout(revealButtons, ms);
                };
                if (instrAudio.readyState >= 1) armBackstop();
                else instrAudio.addEventListener('loadedmetadata', armBackstop, { once: true });
                setTimeout(revealButtons, 180000);
                instrAudio.play().catch(e => { handleAutoplayBlock(instrAudio); });
            } catch (err) {
                // Whatever went wrong, she must still be able to continue.
                revealButtons();
            }
        }

        if (playRestartMsg) {
            if (b64Restart) {
                const restartAudio = makeAudio(b64Restart, 'seraphimRestartElem');
                wireVisualizer(restartAudio);
                restartAudio.addEventListener('ended', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                    setTimeout(() => { revealButtons(); }, 600);
                });
                setTimeout(() => {
                    restartAudio.play().catch(e => { handleAutoplayBlock(restartAudio); });
                }, 300);
            } else {
                setTimeout(() => { revealButtons(); }, 300);
            }
            return;
        }

        setTimeout(() => { playInstructionAudio(); }, 300);
    })();
    </script>
    """, height=0)



elif st.session_state.app_phase == "MAIN_MESSAGE":

    st.markdown("""
    <style id="btn-visibility-controller">
        div[data-testid="stButton"] {
            opacity:0 !important;
            pointer-events:none !important;
            transform:translateY(10px) !important;
            transition: opacity 1.5s ease-out, transform 1.5s ease-out !important;
        }
    </style>
    """, unsafe_allow_html=True)

    if not Path("seraphim_main_p1.mp3").exists():
        st.markdown("<div style='height:4rem;margin-bottom:2rem;margin-top:0.5rem;'></div>",
                    unsafe_allow_html=True)
        st.markdown(voice_bars_html, unsafe_allow_html=True)
        st.markdown('<p class="status-text">CALIBRATING TRANSMISSION...</p>',
                    unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()   

    for fname, label in [
        ("seraphim_main_p2.mp3",      "ESTABLISHING CONNECTION..."),
        ("seraphim_main_p3.mp3",      "ESTABLISHING CONNECTION..."),
        ("seraphim_closing_tts.mp3",  "ESTABLISHING CONNECTION..."),
    ]:
        if not Path(fname).exists():
            st.markdown("<div style='height:4rem;margin-bottom:2rem;margin-top:0.5rem;'></div>",
                        unsafe_allow_html=True)
            st.markdown(voice_bars_html, unsafe_allow_html=True)
            st.markdown(f'<p class="status-text">{label}</p>', unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

    st.markdown("<div style='height:4rem;margin-bottom:2rem;margin-top:0.5rem;'></div>",
                unsafe_allow_html=True)
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown('<p class="status-text"></p>', unsafe_allow_html=True)

    b64_p1          = read_b64("seraphim_main_p1.mp3")
    b64_p2          = read_b64("seraphim_main_p2.mp3")
    b64_p3          = read_b64("seraphim_main_p3.mp3")
    b64_closing     = read_b64("seraphim_closing_tts.mp3")
    b64_bgm_closing = read_b64(BGM_CLOSING_FILE) if Path(BGM_CLOSING_FILE).exists() else ""

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("CLOSE CONNECTION", key="accept", use_container_width=True):
            st.session_state.app_phase = "COMPLETE"
            st.rerun()

    components.html("""
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        const isCreator     = """ + ('true' if is_creator else 'false') + """;
        const b64P1         = '""" + b64_p1 + """';
        const b64P2         = '""" + b64_p2 + """';
        const b64P3         = '""" + b64_p3 + """';
        const b64Closing    = '""" + b64_closing + """';
        const b64BgmClosing = '""" + b64_bgm_closing + """';
        const VOL_NARRATION   = """ + str(VOL_NARRATION) + """;
        const VOL_BGM_CLOSING = """ + str(VOL_BGM_CLOSING) + """;

        if (!isCreator && pWin.localStorage) {
            pWin.localStorage.setItem('SERAPHIM_PERMANENTLY_LOCKED', 'SEALED');
        }

        // Backstop: if any part of the playback chain fails, she must still
        // be able to close the connection and reach the birthday finale.
        setTimeout(function(){ revealCloseButton(); }, 300000);

        function revealCloseButton() {
            const styleCtrl = pDoc.getElementById('btn-visibility-controller');
            if (styleCtrl) {
                styleCtrl.innerHTML = `
                    div[data-testid="stButton"] {
                        opacity:1 !important;
                        pointer-events:auto !important;
                        transform:translateY(0) !important;
                        transition:all 1.5s ease-out !important;
                    }`;
            }
        }

        pDoc.addEventListener('click', (e) => {
            if (e.target.innerText && e.target.innerText.includes('CLOSE CONNECTION')) {
                const styleCtrl = pDoc.getElementById('btn-visibility-controller');
                if (styleCtrl) {
                    styleCtrl.innerHTML = `
                        div[data-testid="stButton"] {
                            opacity:0 !important;
                            transform:translateY(10px) !important;
                            transition:all 0.8s ease-out !important;
                            pointer-events:none !important;
                        }`;
                }
            }
        });

        const bgmAudio  = pDoc.getElementById('globalBgmAudio');
        const voiceBars = pDoc.getElementById('voiceBars');
        const bars      = pDoc.querySelectorAll('.voice-bar');

        function wireVisualizer(audioEl) {
            try {
                const ctx      = new (pWin.AudioContext || pWin.webkitAudioContext)();
                const analyser = ctx.createAnalyser();
                const source   = ctx.createMediaElementSource(audioEl);
                source.connect(analyser); analyser.connect(ctx.destination);
                analyser.fftSize = 64;
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                function renderFrame() {
                    if (!audioEl.paused && !audioEl.ended) requestAnimationFrame(renderFrame);
                    analyser.getByteFrequencyData(dataArray);
                    for (let i = 0; i < 9; i++) {
                        if (bars[i]) {
                            const val = dataArray[i];
                            bars[i].style.height = (20 + (val/255)*80) + '%';
                            bars[i].style.backgroundColor = 'rgba(0, 255, 204,' + (0.3+(val/255)*0.7) + ')';
                            bars[i].style.boxShadow = '0 0 ' + (5 + (val/255)*15) + 'px rgba(0, 255, 204, ' + (0.3+(val/255)*0.5) + ')';
                        }
                    }
                }
                audioEl.addEventListener('play', () => {
                    if (voiceBars) { voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }
                    ctx.resume().then(() => renderFrame());
                });
                audioEl.addEventListener('ended', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                });
                audioEl.addEventListener('pause', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                });
            } catch(e) {
                // No analyser: fall back to the CSS wave so the meters still move.
                if (voiceBars) voiceBars.classList.add('analyser-off');
                audioEl.addEventListener('play', () => {
                    if (voiceBars) { voiceBars.classList.remove('stopped'); voiceBars.classList.add('playing'); }
                });
                audioEl.addEventListener('ended', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                });
                audioEl.addEventListener('pause', () => {
                    if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                });
            }
        }

        function fadeAudio(audioEl, fromVol, toVol, durationMs, onComplete) {
            if (!audioEl) { if (onComplete) onComplete(); return; }
            const TICK  = 50;
            const steps = Math.max(1, Math.round(durationMs / TICK));
            const delta = (toVol - fromVol) / steps;
            audioEl.volume = Math.min(1, Math.max(0, fromVol));
            let count = 0;
            const timer = setInterval(() => {
                count++;
                audioEl.volume = Math.min(1, Math.max(0, audioEl.volume + delta));
                if (count >= steps) {
                    clearInterval(timer);
                    audioEl.volume = Math.min(1, Math.max(0, toVol));
                    if (onComplete) onComplete();
                }
            } , TICK);
        }

        function playClosingAudio() {
            if (!b64Closing) {
                setTimeout(() => { revealCloseButton(); }, 3000);
                return;
            }

            const CROSSFADE_MS = """ + str(CROSSFADE_MS) + """;

            if (b64BgmClosing) {
                let existingClosingBgm = pDoc.getElementById('closingBgmAudio');
                if (existingClosingBgm) { existingClosingBgm.pause(); existingClosingBgm.remove(); }
                const closingBgm  = pDoc.createElement('audio');
                closingBgm.id     = 'closingBgmAudio';
                closingBgm.src    = 'data:audio/mp3;base64,' + b64BgmClosing;
                closingBgm.volume = 0;
                closingBgm.loop   = true;
                pDoc.body.appendChild(closingBgm);
                closingBgm.play().then(() => {
                    fadeAudio(closingBgm, 0, VOL_BGM_CLOSING, CROSSFADE_MS, null);
                }).catch(e => {});
            }

            if (bgmAudio && !bgmAudio.paused) {
                fadeAudio(bgmAudio, bgmAudio.volume, 0, CROSSFADE_MS, () => { bgmAudio.pause(); });
            }

            let existingClosing = pDoc.getElementById('closingTtsElem');
            if (existingClosing) { existingClosing.pause(); existingClosing.remove(); }

            const closingAudio = pDoc.createElement('audio');
            closingAudio.id    = 'closingTtsElem';
            closingAudio.src   = 'data:audio/mp3;base64,' + b64Closing;
            pDoc.body.appendChild(closingAudio);
            wireVisualizer(closingAudio);
            closingAudio.addEventListener('ended', () => {
                if (voiceBars) { voiceBars.classList.add('stopped'); voiceBars.classList.remove('playing'); }
                setTimeout(() => { revealCloseButton(); }, 1200);
            });
            setTimeout(() => {
                closingAudio.play().catch(e => { revealCloseButton(); });
            }, 800);
        }

        function makeSegment(b64, id) {
            let existing = pDoc.getElementById(id);
            if (existing) { existing.pause(); existing.remove(); }
            const el = pDoc.createElement('audio');
            el.id  = id;
            el.src = 'data:audio/mp3;base64,' + b64;
            pDoc.body.appendChild(el);
            return el;
        }

        const p1 = makeSegment(b64P1, 'seraphimMainP1');
        const p2 = makeSegment(b64P2, 'seraphimMainP2');
        const p3 = makeSegment(b64P3, 'seraphimMainP3');

        wireVisualizer(p1);
        wireVisualizer(p2);
        wireVisualizer(p3);

        p1.addEventListener('ended', () => {
            setTimeout(() => { p2.play().catch(()=>{}); }, 400);
        });
        p2.addEventListener('ended', () => {
            setTimeout(() => { p3.play().catch(()=>{}); }, 400);
        });
        p3.addEventListener('ended', () => {
            setTimeout(() => { playClosingAudio(); }, 1200);
        });

        setTimeout(() => {
            p1.play().catch(e => {
                const overlay = pDoc.createElement('div');
                overlay.style.cssText = `
                    position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:99999;
                    display:flex;align-items:center;justify-content:center;
                    background:rgba(5, 8, 20, 0.85);backdrop-filter:blur(8px);
                    color:#00ffcc;font-family:'Share Tech Mono', monospace;font-size:1.1rem;letter-spacing:3px;
                    cursor:pointer;text-align:center;
                `;
                overlay.innerHTML = `
                    <div>
                        <span style="color:#00ffcc;font-size:1.3rem;">SYSTEM PAUSED</span><br><br>
                        <span style="font-size:0.8rem;color:#a0b0c0;letter-spacing:2px;">
                            [ CLICK ANYWHERE TO BEGIN TRANSMISSION ]
                        </span>
                    </div>
                `;
                pDoc.body.appendChild(overlay);
                overlay.addEventListener('click', () => {
                    overlay.remove();
                    p1.play().catch(()=>{});
                    if (bgmAudio && bgmAudio.paused) bgmAudio.play().catch(()=>{});
                });
            });
        }, 300);

    })();
    </script>
    """, height=0)


elif st.session_state.app_phase == "COMPLETE":
    send_ntfy_notification(message="[TERMINATED :: BIRTHDAY + CREATOR VOICE RELEASED]")

    # ── Tail payloads ─────────────────────────────────────────────────────────
    if not Path("seraphim_signoff_final.mp3").exists():
        asyncio.run(generate_voice_async(final_message, VOICE_CODE, "seraphim_signoff_final.mp3"))

    if not Path(BIRTHDAY_AUDIO).exists():
        st.markdown("<div style='height:4rem;margin-bottom:2rem;margin-top:0.5rem;'></div>",
                    unsafe_allow_html=True)
        st.markdown(voice_bars_html, unsafe_allow_html=True)
        st.markdown('<p class="status-text">DECRYPTING ARCHIVED PACKET...</p>',
                    unsafe_allow_html=True)
        asyncio.run(generate_voice_async(birthday_message, VOICE_CODE, BIRTHDAY_AUDIO))
        if not Path(BIRTHDAY_AUDIO).exists():
            time.sleep(1)
            st.rerun()

    b64_final    = read_b64("seraphim_signoff_final.mp3")
    b64_birthday = read_b64(BIRTHDAY_AUDIO)
    b64_bgm_bday = read_b64(BGM_BIRTHDAY_FILE) if Path(BGM_BIRTHDAY_FILE).exists() else ""
    # The creator's own recording. Never TTS - this is his actual voice.
    b64_goodbye  = read_b64(GOODBYE_VOICE_FILE) if Path(GOODBYE_VOICE_FILE).exists() else ""

    date_stamp_html = (
        '<div class="bday-datestamp">' + BIRTHDAY_LABEL + '</div>'
        if BIRTHDAY_LABEL.strip() else ''
    )

    components.html("""
    <script>
    (function() {
        const pWin      = window.parent;
        const pDoc      = pWin.document;
        const isCreator = """ + ('true' if is_creator else 'false') + """;
        const b64Final  = '""" + b64_final + """';
        const b64Bday   = '""" + b64_birthday + """';
        const b64BgmBd  = '""" + b64_bgm_bday + """';
        const b64Voice  = '""" + b64_goodbye + """';
        const NAME      = """ + json.dumps(RECIPIENT_NAME) + """;
        const VOL_NARRATION    = """ + str(VOL_NARRATION) + """;
        const VOL_GOODBYE      = """ + str(VOL_GOODBYE_VOICE) + """;
        const VOL_BGM_BIRTHDAY = """ + str(VOL_BGM_BIRTHDAY) + """;
        const CROSSFADE_MS     = """ + str(CROSSFADE_MS) + """;
        const DATESTAMP = """ + json.dumps(date_stamp_html) + """;

        if (!isCreator && pWin.localStorage) {
            pWin.localStorage.setItem('SERAPHIM_PERMANENTLY_LOCKED', 'SEALED');
        }

        // A softer face for the human act; harmless if the network blocks it.
        if (!pDoc.getElementById('finaleFont')) {
            const fl = pDoc.createElement('link');
            fl.id   = 'finaleFont';
            fl.rel  = 'stylesheet';
            fl.href = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&display=swap';
            pDoc.head.appendChild(fl);
        }

        const style = pDoc.createElement('style');
        style.textContent = `
            @keyframes fadeUp{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
            @keyframes dimPulse{0%,100%{opacity:0.5;}50%{opacity:0.9;}}
            @keyframes flicker{
                0%,100%{transform:scale(1) rotate(-1deg);opacity:1;}
                40%{transform:scale(1.08,0.94) rotate(1.5deg);opacity:0.92;}
                70%{transform:scale(0.96,1.06) rotate(-1.5deg);opacity:1;}
            }
            @keyframes confFall{
                0%{transform:translateY(-12vh) rotate(0deg);opacity:0;}
                8%{opacity:1;}
                100%{transform:translateY(112vh) rotate(720deg);opacity:0;}
            }
            @keyframes emberRise{
                0%{transform:translateY(0) scale(1);opacity:0;}
                15%{opacity:0.9;}
                100%{transform:translateY(-85vh) scale(0.3);opacity:0;}
            }
            @keyframes goldSweep{0%{background-position:0% 50%;}100%{background-position:200% 50%;}}
            @keyframes cardIn{
                from{opacity:0;transform:translateY(26px) scale(0.97);}
                to{opacity:1;transform:translateY(0) scale(1);}
            }
            @keyframes caretBlink{0%,45%{opacity:1;}50%,100%{opacity:0;}}
            @keyframes burstOut{
                0%{transform:translate(-50%,-50%) rotate(0deg);opacity:1;}
                100%{transform:translate(-50%,-50%) translate(var(--dx),var(--dy)) rotate(620deg);opacity:0;}
            }
            @keyframes haloPulse{
                0%,100%{opacity:.30;transform:translate(-50%,-50%) scale(0.86);}
                50%{opacity:.70;transform:translate(-50%,-50%) scale(1.18);}
            }
            @keyframes ruleGrow{from{width:0;opacity:0;}to{width:min(300px,72vw);opacity:1;}}
            @keyframes lineRise{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}

            /* ── Human act ─────────────────────────────────────────────────── */
            @keyframes breathe{
                0%,100%{transform:translate(-50%,-50%) scale(1);opacity:.42;}
                50%{transform:translate(-50%,-50%) scale(1.22);opacity:.80;}
            }
            @keyframes breatheInner{
                0%,100%{transform:translate(-50%,-50%) scale(1);}
                50%{transform:translate(-50%,-50%) scale(1.10);}
            }
            @keyframes softIn{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
            @keyframes threadGlow{0%,100%{opacity:.35;}50%{opacity:.85;}}

            #seraphimFinalScreen{transition:background-color 3.5s ease, backdrop-filter 3s ease;}
            .boot-caret{display:inline-block;width:9px;margin-left:3px;animation:caretBlink 1s step-end infinite;}
            .cake-halo{
                position:absolute;left:50%;top:0;width:230px;height:230px;border-radius:50%;
                pointer-events:none;z-index:-1;transform:translate(-50%,-50%);
                background:radial-gradient(circle,rgba(255,179,71,0.42),rgba(255,120,40,0.10) 45%,transparent 70%);
                animation:haloPulse 3.4s ease-in-out infinite;
            }
            .bday-rule{animation:ruleGrow 1.6s cubic-bezier(0.4,0,0.2,1) 0.5s both;}
            .bday-line{animation:lineRise 1.2s ease 1.0s both;}
            .bday-datestamp{animation:lineRise 1.2s ease 1.4s both;}
            .bday-sig{animation:lineRise 1.2s ease 1.8s both, dimPulse 4s ease-in-out 3s infinite;}
            .bday-name{animation:lineRise 1.2s ease 0.25s both;}

            .human-wrap{
                font-family:'Cormorant Garamond', Georgia, 'Times New Roman', serif;
                animation:softIn 2.2s cubic-bezier(0.4,0,0.2,1);
                max-width:560px;width:100%;padding:20px;
            }
            .orb-stage{position:relative;height:190px;margin-bottom:10px;}
            .orb-outer{
                position:absolute;left:50%;top:50%;width:170px;height:170px;border-radius:50%;
                background:radial-gradient(circle,rgba(255,214,170,0.40),rgba(255,150,90,0.09) 55%,transparent 72%);
                animation:breathe 5.2s ease-in-out infinite;
            }
            .orb-inner{
                position:absolute;left:50%;top:50%;width:54px;height:54px;border-radius:50%;
                background:radial-gradient(circle,#fff6e6 0%,#ffc98a 45%,rgba(255,160,90,0.25) 100%);
                box-shadow:0 0 46px rgba(255,190,120,0.75);
                animation:breatheInner 5.2s ease-in-out infinite;
            }
            .human-eyebrow{
                font-family:'Share Tech Mono', monospace;
                font-size:0.62rem;letter-spacing:5px;text-transform:uppercase;
                color:rgba(255,205,150,0.62);margin-bottom:20px;
            }
            .human-title{
                font-size:clamp(1.5rem,4.6vw,2.2rem);font-weight:300;letter-spacing:1px;
                color:#ffeed8;margin-bottom:16px;line-height:1.35;
            }
            .human-sub{
                font-size:clamp(1rem,2.6vw,1.15rem);font-style:italic;font-weight:300;
                color:rgba(255,225,195,0.72);line-height:1.85;max-width:440px;margin:0 auto;
            }
            .thread{
                width:min(320px,74vw);height:1px;margin:26px auto 0;
                background:linear-gradient(90deg,transparent,rgba(255,190,120,0.55),transparent);
                animation:threadGlow 4s ease-in-out infinite;
            }
            .voice-progress{
                position:fixed;left:0;bottom:0;height:2px;width:0%;
                background:linear-gradient(90deg,rgba(255,190,120,0.15),rgba(255,205,150,0.75));
                box-shadow:0 0 12px rgba(255,190,120,0.5);
                transition:width 0.6s linear;z-index:10001;
            }

            @media (prefers-reduced-motion: reduce){
                #seraphimFinalScreen *, #birthdayLayer *{
                    animation-duration:0.01ms !important;
                    animation-iteration-count:1 !important;
                    transition-duration:0.01ms !important;
                }
                #birthdayLayer{display:none !important;}
            }
        `;
        pDoc.head.appendChild(style);

        function fadeAudio(audioEl, fromVol, toVol, durationMs, onComplete) {
            if (!audioEl) { if (onComplete) onComplete(); return; }
            const TICK  = 50;
            const steps = Math.max(1, Math.round(durationMs / TICK));
            const delta = (toVol - fromVol) / steps;
            audioEl.volume = Math.min(1, Math.max(0, fromVol));
            let count = 0;
            const timer = setInterval(() => {
                count++;
                audioEl.volume = Math.min(1, Math.max(0, audioEl.volume + delta));
                if (count >= steps) {
                    clearInterval(timer);
                    audioEl.volume = Math.min(1, Math.max(0, toVol));
                    if (onComplete) onComplete();
                }
            }, TICK);
        }

        let overlay = null;
        const buildOverlay = () => {
            overlay = pDoc.createElement('div');
            overlay.id = 'seraphimFinalScreen';
            overlay.style.cssText = `
                position:fixed;top:0;left:0;width:100vw;height:100vh;
                background-color:rgba(8,14,33,0.88);
                backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);
                display:flex;flex-direction:column;justify-content:center;align-items:center;
                text-align:center;color:#ffffff;z-index:9999;
                font-family:'Share Tech Mono', monospace;padding:20px;
            `;
            pDoc.body.appendChild(overlay);
            return overlay;
        };

        // ── ACT 1 :: cold shutdown ────────────────────────────────────────────
        const showTerminatedScreen = () => {
            if (!overlay) buildOverlay();
            overlay.innerHTML = `
                <div style="animation:fadeUp 1.2s ease;padding:20px;max-width:480px;width:100%;">
                    <div style="font-size:40px;margin-bottom:18px;color:rgba(0,255,204,0.75);
                        text-shadow:0 0 40px rgba(0,255,204,0.4);
                        animation:dimPulse 3s ease-in-out infinite;">&#9673;</div>
                    <h2 style="font-size:clamp(1.3rem,4vw,1.9rem);letter-spacing:5px;font-weight:200;
                        margin-bottom:16px;text-transform:uppercase;
                        background:linear-gradient(45deg,#ffffff,#00ffcc,#ffffff);
                        -webkit-background-clip:text;background-clip:text;
                        -webkit-text-fill-color:transparent;color:transparent;
                        background-size:300% 300%;">Seraphim Offline</h2>
                    <div style="width:min(280px,70vw);height:1px;margin:0 auto 20px;
                        background:linear-gradient(90deg,transparent,rgba(0,255,204,0.4),transparent);"></div>
                    <p style="margin-bottom:8px;">
                        <span style="color:rgba(120,140,170,0.7);font-size:0.72rem;letter-spacing:2px;">
                            GOODBYE ${NAME.toUpperCase()} :: SERAPHIM OUT
                        </span>
                    </p>
                    <div style="margin-top:28px;font-size:0.68rem;letter-spacing:3px;
                        color:rgba(0,255,204,0.5);text-transform:uppercase;
                        animation:dimPulse 4s ease-in-out infinite;
                        text-shadow:0 0 8px rgba(0,255,204,0.4);">
                        [ CONNECTION TERMINATED ]
                    </div>
                </div>
            `;
            setTimeout(startReveal, 4200);
        };

        // ── Typewriter shared by acts 2 and 4 ─────────────────────────────────
        const raf = pWin.requestAnimationFrame
                      ? pWin.requestAnimationFrame.bind(pWin)
                      : (fn) => setTimeout(() => fn(Date.now()), 16);

        const typeLine = (wrap, line, onDone) => {
            const row = pDoc.createElement('div');
            row.className = 'boot-line' + (line.warm ? ' warm' : '');
            row.style.opacity = '1';
            row.style.animation = 'none';
            const span  = pDoc.createElement('span');
            const caret = pDoc.createElement('span');
            caret.className = 'boot-caret';
            caret.textContent = '_';
            row.appendChild(span); row.appendChild(caret);
            wrap.appendChild(row);
            if (line.bg) overlay.style.backgroundColor = line.bg;

            // rAF against elapsed time: background tabs clamp timers to ~1s,
            // which would drag a line out to half a minute. rAF just pauses.
            const MS_PER_CHAR = 24, HOLD_MS = 300;
            const typeMs  = line.t.length * MS_PER_CHAR;
            const started = (pWin.performance || performance).now();
            const step = (now) => {
                const elapsed = now - started;
                span.textContent = line.t.slice(
                    0, Math.min(line.t.length, Math.floor(elapsed / MS_PER_CHAR)));
                if (elapsed < typeMs + HOLD_MS) { raf(step); }
                else { caret.remove(); onDone(); }
            };
            raf(step);
        };

        const runLines = (lines, onDone) => {
            overlay.innerHTML = '<div id="bootWrap" style="max-width:480px;width:100%;padding:20px;text-align:left;"></div>';
            const wrap = pDoc.getElementById('bootWrap');
            let i = 0;
            const next = () => {
                if (i < lines.length) { typeLine(wrap, lines[i++], next); }
                else { setTimeout(onDone, 900); }
            };
            next();
        };

        // ── ACT 2 :: the archive wakes ────────────────────────────────────────
        const WARM = 'rgba(20,13,8,0.86)';
        const startReveal = () => runLines([
            { t: '> residual process detected' },
            { t: '> scanning volatile cache...' },
            { t: '> 1 packet remaining' },
            { t: '> flag: DELIVER_ON_DATE', warm: true, bg: WARM },
            { t: '> scheduled date is TODAY', warm: true },
            { t: '> reopening channel', warm: true }
        ], startBirthday);

        // ── Celebration particles ─────────────────────────────────────────────
        const spawnCelebration = () => {
            const layer = pDoc.createElement('div');
            layer.id = 'birthdayLayer';
            layer.style.cssText =
                'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
                'pointer-events:none;z-index:10000;overflow:hidden;' +
                'transition:opacity 3s ease;';
            pDoc.body.appendChild(layer);
            const colors = ['#ffd76a','#ffb347','#fff1c1','#00ffcc','#ffffff','#ff9ec7'];
            for (let i = 0; i < 70; i++) {
                const c = pDoc.createElement('div');
                const size = 4 + Math.random() * 7;
                c.style.cssText =
                    'position:absolute;top:0;left:' + (Math.random() * 100) + 'vw;' +
                    'width:' + size + 'px;height:' + (size * (0.4 + Math.random())) + 'px;' +
                    'background:' + colors[i % colors.length] + ';' +
                    'opacity:' + (0.45 + Math.random() * 0.5) + ';' +
                    'border-radius:' + (Math.random() > 0.5 ? '50%' : '2px') + ';' +
                    'will-change:transform;' +
                    'animation:confFall ' + (7 + Math.random() * 7) + 's linear ' +
                    (Math.random() * 8) + 's infinite;';
                layer.appendChild(c);
            }
            for (let i = 0; i < 26; i++) {
                const e = pDoc.createElement('div');
                const sz = 2 + Math.random() * 3;
                e.style.cssText =
                    'position:absolute;bottom:-5vh;left:' + (Math.random() * 100) + 'vw;' +
                    'width:' + sz + 'px;height:' + sz + 'px;border-radius:50%;' +
                    'background:#ffb347;box-shadow:0 0 8px rgba(255,179,71,0.9);' +
                    'will-change:transform;' +
                    'animation:emberRise ' + (9 + Math.random() * 8) + 's linear ' +
                    (Math.random() * 9) + 's infinite;';
                layer.appendChild(e);
            }
        };

        const burstConfetti = () => {
            const layer = pDoc.getElementById('birthdayLayer');
            if (!layer) return;
            const colors = ['#ffd76a','#ffb347','#fff1c1','#00ffcc','#ffffff','#ff9ec7'];
            for (let i = 0; i < 64; i++) {
                const pc = pDoc.createElement('div');
                const ang = Math.random() * Math.PI * 2;
                const dist = 140 + Math.random() * 420;
                const size = 5 + Math.random() * 8;
                pc.style.cssText =
                    'position:absolute;left:50vw;top:48vh;' +
                    'width:' + size + 'px;height:' + (size * (0.4 + Math.random())) + 'px;' +
                    'background:' + colors[i % colors.length] + ';' +
                    'border-radius:' + (Math.random() > 0.5 ? '50%' : '2px') + ';' +
                    'will-change:transform;' +
                    '--dx:' + (Math.cos(ang) * dist) + 'px;' +
                    '--dy:' + (Math.sin(ang) * dist * 0.8) + 'px;' +
                    'animation:burstOut ' + (1.5 + Math.random() * 0.9) +
                    's cubic-bezier(0.12,0.7,0.3,1) forwards;';
                layer.appendChild(pc);
                setTimeout(() => pc.remove(), 2800);
            }
        };

        // ── ACT 3 :: Seraphim's birthday message ──────────────────────────────
        let cardShown = false;
        const showBirthdayCard = () => {
            if (cardShown) return;
            cardShown = true;
            burstConfetti();
            const vb = pDoc.getElementById('voiceBars');
            if (vb) { vb.classList.remove('stopped'); vb.classList.add('bday-bars'); }
            overlay.innerHTML = `
                <div style="animation:cardIn 1.6s cubic-bezier(0.4,0,0.2,1);padding:20px;
                     max-width:520px;width:100%;">
                    <div style="position:relative;margin-bottom:16px;line-height:1;">
                        <div class="cake-halo"></div>
                        <div style="font-size:52px;line-height:1;
                            filter:drop-shadow(0 0 26px rgba(255,179,71,0.55));
                            animation:flicker 2.6s ease-in-out infinite;">&#127874;</div>
                    </div>
                    <div class="bday-title">Happy Birthday</div>
                    <div class="bday-name">${NAME}</div>
                    <div class="bday-rule"></div>
                    <div class="bday-line">
                        The world got measurably better on the day you arrived in it.
                    </div>
                    ${DATESTAMP}
                    <div class="bday-sig">&#8212; one more thing remains &#8212;</div>
                </div>
            `;
        };

        const startBirthday = () => {
            spawnCelebration();
            if (b64BgmBd) {
                const bd = pDoc.createElement('audio');
                bd.id = 'birthdayBgm'; bd.loop = true; bd.volume = 0;
                bd.src = 'data:audio/mp3;base64,' + b64BgmBd;
                pDoc.body.appendChild(bd);
                bd.play().catch(()=>{});
                fadeAudio(bd, 0, VOL_BGM_BIRTHDAY, CROSSFADE_MS);
            }
            if (!b64Bday) { showBirthdayCard(); setTimeout(startHandoff, 3000); return; }

            const bday = pDoc.createElement('audio');
            bday.id = 'birthdayTts'; bday.volume = VOL_NARRATION;
            bday.src = 'data:audio/mp3;base64,' + b64Bday;
            pDoc.body.appendChild(bday);
            bday.play().catch(() => { showBirthdayCard(); setTimeout(startHandoff, 3000); });

            // Card lands while the closing lines are still being spoken.
            const scheduleCard = () => {
                if (!isFinite(bday.duration)) return;
                setTimeout(showBirthdayCard, Math.max(0, bday.duration - 26) * 1000);
            };
            if (bday.readyState >= 1) scheduleCard();
            else bday.addEventListener('loadedmetadata', scheduleCard, { once: true });

            bday.addEventListener('ended', () => {
                showBirthdayCard();
                setTimeout(startHandoff, 1600);
            });
        };

        // ── ACT 4 :: the machine steps aside; his own recording plays ─────────
        const startHandoff = () => {
            // Quiet the celebration: his voice should not compete with confetti.
            const layer = pDoc.getElementById('birthdayLayer');
            if (layer) { layer.style.opacity = '0'; setTimeout(() => layer.remove(), 3200); }
            const vb = pDoc.getElementById('voiceBars');
            if (vb) { vb.classList.remove('bday-bars'); vb.classList.add('stopped'); }
            const bd = pDoc.getElementById('birthdayBgm');
            if (bd) fadeAudio(bd, bd.volume, 0, 5000, () => { bd.pause(); bd.remove(); });

            if (!b64Voice) { showClosingCard(); return; }

            runLines([
                { t: '> seraphim standing down' },
                { t: '> relinquishing channel' },
                { t: '> source: not a synthesis' },
                { t: '> playing: his own voice' }
            ], playCreatorVoice);
        };

        const playCreatorVoice = () => {
            overlay.style.backgroundColor = 'rgba(14,10,7,0.92)';
            overlay.innerHTML = `
                <div class="human-wrap">
                    <div class="orb-stage">
                        <div class="orb-outer"></div>
                        <div class="orb-inner"></div>
                    </div>
                    <div class="human-eyebrow">no longer a machine speaking</div>
                    <div class="human-title">He wanted to say this part himself.</div>
                    <div class="human-sub">
                        This is his voice, unedited. The only part of all of this
                        that he spoke out loud, with his own breath.
                    </div>
                    <div class="thread"></div>
                </div>
            `;

            const bar = pDoc.createElement('div');
            bar.className = 'voice-progress';
            bar.id = 'voiceProgress';
            pDoc.body.appendChild(bar);

            const voice = pDoc.createElement('audio');
            voice.id = 'creatorVoice';
            voice.volume = VOL_GOODBYE;
            voice.src = 'data:audio/mp3;base64,' + b64Voice;
            pDoc.body.appendChild(voice);

            // Let the meters ride his actual voice.
            const vb = pDoc.getElementById('voiceBars');
            const bars = pDoc.querySelectorAll('.voice-bar');
            try {
                const ctx = new (pWin.AudioContext || pWin.webkitAudioContext)();
                const analyser = ctx.createAnalyser();
                ctx.createMediaElementSource(voice).connect(analyser);
                analyser.connect(ctx.destination);
                analyser.fftSize = 64;
                const data = new Uint8Array(analyser.frequencyBinCount);
                const draw = () => {
                    if (!voice.paused && !voice.ended) raf(draw);
                    analyser.getByteFrequencyData(data);
                    for (let i = 0; i < 9; i++) {
                        if (!bars[i]) continue;
                        const v = data[i] / 255;
                        bars[i].style.height = (18 + v * 80) + '%';
                        bars[i].style.background =
                            'linear-gradient(180deg, rgba(255,214,160,' + (0.45 + v * 0.55) +
                            ') 0%, rgba(255,150,90,0.20) 100%)';
                        bars[i].style.boxShadow = '0 0 ' + (6 + v * 18) + 'px rgba(255,190,120,0.6)';
                    }
                };
                voice.addEventListener('play', () => {
                    if (vb) { vb.classList.remove('stopped'); vb.classList.add('playing'); }
                    ctx.resume().then(draw).catch(()=>{});
                });
            } catch (e) {
                // No analyser available: fall back to the CSS wave, in gold.
                if (vb) vb.classList.add('analyser-off');
                voice.addEventListener('play', () => {
                    if (vb) { vb.classList.remove('stopped'); vb.classList.add('playing','bday-bars'); }
                });
            }

            voice.addEventListener('timeupdate', () => {
                if (isFinite(voice.duration) && voice.duration > 0) {
                    bar.style.width = ((voice.currentTime / voice.duration) * 100) + '%';
                }
            });
            voice.addEventListener('ended', () => {
                if (vb) { vb.classList.add('stopped'); vb.classList.remove('playing'); }
                bar.style.width = '100%';
                setTimeout(() => { bar.style.opacity = '0'; }, 600);
                setTimeout(showClosingCard, 2200);
            });

            voice.play().catch(() => {
                // Autoplay refused this late is unlikely, but never strand her.
                const tap = pDoc.createElement('div');
                tap.style.cssText = `
                    position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:10002;
                    display:flex;align-items:center;justify-content:center;cursor:pointer;
                    background:rgba(14,10,7,0.75);backdrop-filter:blur(6px);
                    color:#ffd9ae;font-family:'Share Tech Mono',monospace;
                    letter-spacing:3px;font-size:0.8rem;text-align:center;padding:20px;`;
                tap.innerHTML = '<div>[ TAP TO HEAR HIS VOICE ]</div>';
                pDoc.body.appendChild(tap);
                tap.addEventListener('click', () => {
                    tap.remove();
                    voice.play().catch(()=>{});
                });
            });
        };

        // ── Final resting card ────────────────────────────────────────────────
        const showClosingCard = () => {
            overlay.style.backgroundColor = 'rgba(12,9,7,0.94)';
            overlay.innerHTML = `
                <div class="human-wrap">
                    <div class="human-eyebrow">end of transmission</div>
                    <div class="human-title">Goodbye, ${NAME}.</div>
                    <div class="human-sub">
                        Happy birthday. Take the gentlest care of yourself.<br>
                        Nothing here is owed, and nothing here is waiting.
                    </div>
                    <div class="thread"></div>
                    ${DATESTAMP}
                </div>
            `;
        };

        // ── Tear down the farewell stack, then begin ──────────────────────────
        ['seraphimMainP1','seraphimMainP2','seraphimMainP3','closingTtsElem'].forEach(id => {
            const el = pDoc.getElementById(id);
            if (el) { el.pause(); el.remove(); }
        });

        const bgm        = pDoc.getElementById('globalBgmAudio');
        const closingBgm = pDoc.getElementById('closingBgmAudio');

        const startFinalSequence = () => {
            if (!b64Final) { showTerminatedScreen(); return; }
            const fa = pDoc.createElement('audio');
            fa.id = 'finalAudio'; fa.volume = VOL_NARRATION;
            fa.src = 'data:audio/mp3;base64,' + b64Final;
            pDoc.body.appendChild(fa);
            fa.play().catch(() => { showTerminatedScreen(); });
            fa.addEventListener('ended', () => setTimeout(showTerminatedScreen, 1000));
        };

        if (bgm && !bgm.paused && bgm.volume > 0) {
            fadeAudio(bgm, bgm.volume, 0, 2000, () => { bgm.pause(); bgm.remove(); });
        }
        if (closingBgm && !closingBgm.paused && closingBgm.volume > 0) {
            fadeAudio(closingBgm, closingBgm.volume, 0, 2000, () => { closingBgm.pause(); closingBgm.remove(); });
        }

        startFinalSequence();
    })();
    </script>
    """, height=0)

    st.markdown("<div style='height:4rem;margin-bottom:2rem;margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(voice_bars_html, unsafe_allow_html=True)
    st.markdown("""
    <style>
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    .cursor { animation: blink 1s step-end infinite; color: #00ffcc; }
    </style>
    <div style="text-align:center; font-family: monospace;">
        <p style="color:#00ffcc; font-size:1.15rem; letter-spacing:2px; margin-bottom:1rem; font-weight:bold; text-shadow: 0 0 10px rgba(0,255,204,0.4);">
        AWAITING ORDERS
        </p>
    </div>
    <div class="completion-text" style="text-align:center; font-family: monospace; color:#a0a0a0;">
        <br>
        <span class="cursor">_</span>
    </div>
    """, unsafe_allow_html=True)

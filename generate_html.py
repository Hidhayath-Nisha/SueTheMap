"""Generate sue_the_map.html — single self-contained file."""
import json
import os

# Read Gemini API key from .env (never committed to git)
def _load_env_key():
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('GEMINI_API_KEY='):
                    val = line.split('=', 1)[1].strip()
                    return val if val and val != 'your_key_here' else ''
    except FileNotFoundError:
        pass
    return os.environ.get('GEMINI_API_KEY', '')

GEMINI_KEY = _load_env_key()

with open('dail_data.json', 'r', encoding='utf-8') as f:
    dail_json_str = f.read()

with open('us-states.json', 'r', encoding='utf-8') as f:
    geo_json_str = f.read()

# Escape </script> to prevent premature HTML tag closure
dail_json_safe = dail_json_str.replace('</', '<\/')
geo_json_safe = geo_json_str.replace('</', '<\/')

CSS = """\
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#f4f6f9;--surface:#ffffff;--surface2:#f0f2f6;--border:#dde2ea;
  --accent:#dc2626;--accent2:#ea580c;--law-blue:#1d4ed8;
  --text:#0f172a;--muted:#64748b;--active-green:#16a34a;
}
html,body{height:100%;width:100%;overflow:hidden;background:var(--bg);color:var(--text);
  font-family:'DM Sans',sans-serif;font-size:15px;}
#header{height:62px;background:var(--surface);border-bottom:2px solid var(--border);
  display:flex;align-items:center;padding:0 20px;gap:16px;flex-shrink:0;z-index:100;
  box-shadow:0 1px 4px rgba(0,0,0,.07);}
#logo{font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:2px;color:var(--text);white-space:nowrap;}
#logo span{color:var(--accent);}
#mode-toggle{display:flex;background:var(--bg);border:1px solid var(--border);border-radius:24px;overflow:hidden;flex-shrink:0;}
.mode-btn{padding:7px 16px;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:600;
  border:none;background:transparent;color:var(--muted);cursor:pointer;transition:all .25s;white-space:nowrap;}
.mode-btn.law-active{background:var(--accent);color:#fff;}
.mode-btn.pub-active{background:var(--accent2);color:#fff;}
#share-btn{padding:7px 15px;background:var(--surface2);border:1px solid var(--border);border-radius:20px;
  font-family:'DM Sans',sans-serif;font-size:13px;font-weight:600;color:var(--muted);cursor:pointer;transition:all .2s;white-space:nowrap;}
#share-btn:hover{background:var(--law-blue);color:#fff;border-color:var(--law-blue);}
#share-btn.copied{background:var(--active-green);color:#fff;border-color:var(--active-green);}
#global-stats{display:flex;gap:22px;margin-left:auto;flex-shrink:0;}
.gstat{display:flex;flex-direction:column;align-items:center;}
.gstat-num{font-family:'DM Mono',monospace;font-size:18px;font-weight:600;}
.gstat-lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:1px;}
#main{display:flex;height:calc(100vh - 62px - 26px);overflow:hidden;}
#left-panel{width:290px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;box-shadow:1px 0 4px rgba(0,0,0,.04);}
.panel-tabs{display:flex;border-bottom:1px solid var(--border);flex-shrink:0;}
.ptab{flex:1;padding:11px 4px;text-align:center;font-size:12px;font-weight:600;color:var(--muted);
  cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;text-transform:uppercase;letter-spacing:.4px;}
.ptab.active{color:var(--text);border-bottom-color:var(--accent);}
.tab-content{flex:1;overflow-y:auto;padding:14px;}
.tab-content::-webkit-scrollbar{width:4px;}
.tab-content::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
#mic-area{text-align:center;padding:8px 0 12px;}
#mic-btn{width:60px;height:60px;border-radius:50%;background:var(--accent);border:none;
  cursor:pointer;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;
  transition:all .2s;box-shadow:0 2px 10px rgba(220,38,38,.3);}
#mic-btn:hover{transform:scale(1.06);box-shadow:0 4px 18px rgba(220,38,38,.4);}
#mic-btn.listening{animation:micPulse 1s infinite;}
@keyframes micPulse{0%{box-shadow:0 0 0 0 rgba(220,38,38,.7);}70%{box-shadow:0 0 0 18px rgba(220,38,38,0);}100%{box-shadow:0 0 0 0 rgba(220,38,38,0);}}
#mic-btn svg{width:26px;height:26px;fill:#fff;}
#mic-status{font-size:12px;color:var(--muted);min-height:18px;}
#query-box{width:100%;background:var(--bg);border:1.5px solid var(--border);border-radius:10px;
  color:var(--text);padding:10px 12px;font-family:'DM Sans',sans-serif;font-size:14px;
  resize:none;height:62px;margin-top:10px;outline:none;transition:border-color .2s;}
#query-box:focus{border-color:var(--law-blue);}
#query-box::placeholder{color:#94a3b8;}
#query-btn{width:100%;margin-top:10px;padding:10px;background:var(--law-blue);border:none;
  border-radius:10px;color:#fff;font-family:'DM Sans',sans-serif;font-size:14px;font-weight:600;
  cursor:pointer;transition:background .2s;display:flex;align-items:center;justify-content:center;gap:6px;}
#query-btn:hover{background:#1e40af;}
#query-btn:disabled{background:#94a3b8;cursor:not-allowed;}
.section-label{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;
  letter-spacing:.8px;margin:12px 0 7px;}
.chips{display:flex;flex-wrap:wrap;gap:6px;}
.chip{background:var(--surface2);border:1px solid var(--border);border-radius:12px;
  padding:5px 11px;font-size:12px;color:var(--muted);cursor:pointer;transition:all .15s;}
.chip:hover{background:var(--border);color:var(--text);border-color:#c0c8d8;}
#ai-response{background:var(--bg);border:1.5px solid var(--border);border-radius:10px;
  padding:12px;font-size:14px;line-height:1.7;color:var(--text);min-height:60px;display:none;margin-top:10px;}
#ai-response.show{display:block;}
.alert-banner{background:rgba(220,38,38,.07);border:1.5px solid rgba(220,38,38,.3);
  border-radius:10px;padding:12px 14px;margin-bottom:12px;}
.ab-count{font-family:'DM Mono',monospace;font-size:28px;font-weight:700;color:var(--accent);}
.ab-text{font-size:13px;color:var(--text);margin-top:2px;line-height:1.55;}
.uc-card{background:var(--surface2);border:1px solid var(--border);border-radius:10px;
  padding:11px;margin-bottom:8px;cursor:pointer;transition:all .15s;}
.uc-card:hover{border-color:var(--accent);background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.08);}
.uc-caption{font-size:13px;font-weight:600;color:var(--text);margin-bottom:5px;line-height:1.4;}
.uc-meta{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:5px;}
.badge{font-size:11px;padding:3px 8px;border-radius:9px;font-weight:600;}
.b-state{background:rgba(29,78,216,.12);color:var(--law-blue);}
.b-sector{background:rgba(234,88,12,.12);color:var(--accent2);}
.b-active{background:rgba(22,163,74,.12);color:var(--active-green);}
.b-inactive{background:#e2e8f0;color:#64748b;}
.b-class{background:rgba(234,88,12,.1);color:var(--accent2);}
.uc-sig{font-size:12px;color:var(--muted);line-height:1.55;}
select.fsel{width:100%;background:var(--surface);border:1.5px solid var(--border);border-radius:8px;
  color:var(--text);padding:8px 10px;font-family:'DM Sans',sans-serif;font-size:14px;margin-bottom:10px;
  appearance:none;outline:none;transition:border-color .2s;}
select.fsel:focus{border-color:var(--law-blue);}
.clear-btn{width:100%;padding:9px;background:var(--surface2);border:1px solid var(--border);
  border-radius:9px;color:var(--muted);cursor:pointer;font-size:13px;font-family:'DM Sans',sans-serif;font-weight:600;}
.clear-btn:hover{background:var(--border);color:var(--text);}
#globe-container{flex:1;position:relative;overflow:hidden;}
#globeViz{width:100%;height:100%;}
#globe-loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  background:#e8edf4;z-index:20;flex-direction:column;gap:14px;color:var(--muted);}
#globe-loading .gl-title{font-family:'Bebas Neue',sans-serif;font-size:52px;letter-spacing:3px;color:var(--text);opacity:.4;}
#globe-loading .gl-title span{color:var(--accent);}
#year-bar{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);
  display:flex;gap:5px;z-index:5;}
.yc{background:rgba(255,255,255,.88);border:1px solid var(--border);border-radius:12px;
  padding:4px 11px;font-size:11px;font-weight:600;color:var(--muted);cursor:pointer;white-space:nowrap;transition:all .15s;
  box-shadow:0 1px 3px rgba(0,0,0,.1);}
.yc:hover{background:#fff;color:var(--text);}
.yc.on{background:var(--accent);border-color:var(--accent);color:#fff;box-shadow:0 2px 8px rgba(220,38,38,.3);}
#right-panel{width:340px;flex-shrink:0;background:var(--surface);border-left:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;box-shadow:-1px 0 4px rgba(0,0,0,.04);}
#right-tabs{display:flex;border-bottom:1px solid var(--border);flex-shrink:0;}
.rtab{flex:1;padding:11px 4px;text-align:center;font-size:12px;font-weight:600;color:var(--muted);
  cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;text-transform:uppercase;letter-spacing:.4px;}
.rtab.active{color:var(--text);border-bottom-color:var(--law-blue);}
#right-body{flex:1;overflow-y:auto;padding:16px;}
#right-body::-webkit-scrollbar{width:4px;}
#right-body::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
#state-placeholder{display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:220px;text-align:center;color:var(--muted);}
#state-placeholder p{font-size:13px;line-height:1.65;margin-top:12px;}
.sb-name{font-family:'Bebas Neue',sans-serif;font-size:34px;letter-spacing:1px;color:var(--text);}
.sb-sub{font-size:13px;color:var(--muted);margin-bottom:12px;}
.stat-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px;}
.sc{background:var(--bg);border:1px solid var(--border);border-radius:9px;padding:10px;text-align:center;}
.sc-n{font-family:'DM Mono',monospace;font-size:20px;font-weight:600;color:var(--text);}
.sc-l{font-size:11px;color:var(--muted);margin-top:3px;font-weight:500;}
.cov-alert{background:rgba(234,88,12,.08);border:1.5px solid rgba(234,88,12,.3);
  border-radius:9px;padding:11px;margin-bottom:12px;font-size:13px;line-height:1.55;color:var(--text);}
.mini-bars{margin-bottom:12px;}
.mbar-row{display:flex;align-items:center;gap:7px;margin-bottom:6px;}
.mbar-lbl{width:116px;font-size:12px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0;font-weight:500;}
.mbar-bg{flex:1;height:9px;background:var(--bg);border-radius:4px;overflow:hidden;border:1px solid var(--border);}
.mbar-fill{height:100%;background:var(--law-blue);border-radius:4px;transition:width .5s;}
.mbar-cnt{font-family:'DM Mono',monospace;font-size:12px;color:var(--muted);width:24px;text-align:right;flex-shrink:0;font-weight:600;}
.case-card{background:var(--bg);border:1px solid var(--border);border-radius:9px;padding:11px;margin-bottom:9px;}
.cc-title{font-size:13px;font-weight:600;color:var(--text);margin-bottom:6px;line-height:1.45;}
.cc-badges{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:6px;}
.cc-desc{font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:6px;}
.cc-media{display:flex;align-items:center;gap:4px;}
.mdot{width:7px;height:7px;border-radius:50%;background:var(--active-green);}
.mdot.empty{background:#cbd5e1;}
.cc-src a{font-size:12px;color:var(--law-blue);text-decoration:none;display:block;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:3px;}
.cc-src a:hover{text-decoration:underline;}
.sector-row{display:flex;align-items:center;gap:8px;padding:9px 6px;border-bottom:1px solid var(--border);
  cursor:pointer;transition:background .15s;border-radius:6px;}
.sector-row:hover{background:var(--surface2);}
.sector-row.on{background:rgba(220,38,38,.07);}
.sr-rank{font-family:'DM Mono',monospace;font-size:12px;color:var(--muted);width:20px;flex-shrink:0;font-weight:600;}
.sr-name{flex:1;font-size:13px;color:var(--text);font-weight:500;}
.sr-bar-bg{width:55px;height:6px;background:var(--bg);border-radius:4px;overflow:hidden;flex-shrink:0;border:1px solid var(--border);}
.sr-bar-fill{height:100%;background:var(--accent);border-radius:4px;transition:width .5s;}
.sr-cnt{font-family:'DM Mono',monospace;font-size:13px;color:var(--accent);width:30px;text-align:right;flex-shrink:0;font-weight:700;}
.clr-sect-btn{width:100%;padding:8px 12px;background:rgba(220,38,38,.07);border:1.5px solid rgba(220,38,38,.3);
  border-radius:8px;color:var(--accent);font-size:13px;cursor:pointer;margin-bottom:10px;font-family:'DM Sans',sans-serif;font-weight:600;}
.clr-sect-btn:hover{background:rgba(220,38,38,.13);}
#reset-btn{position:absolute;top:14px;left:14px;background:rgba(255,255,255,.92);border:1px solid var(--border);\n  border-radius:9px;padding:7px 13px;font-size:12px;font-weight:600;color:var(--muted);cursor:pointer;\n  z-index:5;box-shadow:0 2px 8px rgba(0,0,0,.1);transition:all .15s;font-family:'DM Sans',sans-serif;}\n#reset-btn:hover{background:#fff;color:var(--text);box-shadow:0 3px 12px rgba(0,0,0,.15);}\n#legend{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.92);border:1px solid var(--border);\n  border-radius:9px;padding:9px 12px;z-index:5;box-shadow:0 2px 8px rgba(0,0,0,.1);min-width:130px;}\n.leg-title{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}\n.leg-grad{height:10px;border-radius:4px;background:linear-gradient(to right,rgba(59,130,246,0.5),rgba(189,50,46,0.8),rgba(220,20,20,0.95));margin-bottom:3px;}\n.leg-labels{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);font-family:'DM Mono',monospace;}\n#footer{height:26px;background:var(--surface);border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;}
#footer span{font-size:12px;color:var(--muted);}
#footer a{color:var(--muted);text-decoration:none;}
#footer a:hover{color:var(--text);text-decoration:underline;}
#browser-warn{background:rgba(234,88,12,.08);border-bottom:1px solid rgba(234,88,12,.3);
  padding:6px 16px;font-size:12px;color:var(--accent2);display:none;text-align:center;flex-shrink:0;}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid var(--border);
  border-top-color:var(--law-blue);border-radius:50%;animation:spin .7s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:2px;}
@media print{
  #left-panel,#globe-container,#mode-toggle,#share-btn,#footer{display:none!important;}
  #right-panel{width:100%;border:none;box-shadow:none;}
  #right-body{overflow:visible;}
  body,html{overflow:visible;height:auto;}
  #main{height:auto;display:block;}
  .case-card{break-inside:avoid;page-break-inside:avoid;}
}
/* MODE PAGE */
#mode-page{position:fixed;inset:0;background:var(--bg);z-index:1000;overflow-y:auto;
  display:none;}
#mode-page.open{display:block;animation:mpIn .25s ease;}
@keyframes mpIn{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:none;}}
#mp-header{position:sticky;top:0;background:var(--surface);border-bottom:2px solid var(--border);
  padding:16px 32px;display:flex;align-items:center;justify-content:space-between;z-index:10;gap:16px;}
#mp-title{font-family:'Bebas Neue',sans-serif;font-size:34px;color:var(--text);letter-spacing:1px;}
#mp-subtitle{font-size:15px;color:var(--muted);margin-top:2px;}
#mp-close{background:none;border:1px solid var(--border);border-radius:8px;padding:10px 24px;
  cursor:pointer;font-size:16px;color:var(--text);font-family:'DM Sans',sans-serif;flex-shrink:0;}
#mp-close:hover{background:var(--surface2);}
#mp-body{padding:28px 32px;max-width:1200px;margin:0 auto;font-size:15px;}
.mp-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px;}
.mp-stat{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px;}
.mp-stat-num{font-family:'DM Mono',monospace;font-size:40px;font-weight:700;line-height:1;}
.mp-stat-lbl{font-size:14px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:7px;}
.mp-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.mp-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;}
.mp-card-title{font-size:14px;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);
  font-weight:600;margin-bottom:18px;}
.mp-bar-row{display:flex;align-items:center;gap:10px;margin-bottom:11px;}
.mp-bar-label{font-size:15px;color:var(--text);width:140px;flex-shrink:0;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.mp-bar-track{flex:1;height:11px;background:var(--surface2);border-radius:6px;overflow:hidden;}
.mp-bar-fill{height:100%;border-radius:6px;}
.mp-bar-val{font-size:14px;color:var(--muted);font-family:'DM Mono',monospace;width:34px;text-align:right;}
.mp-year-bar{display:flex;align-items:flex-end;gap:4px;height:120px;margin-top:12px;padding-bottom:2px;}
.mp-yr-col{display:flex;flex-direction:column;align-items:center;gap:3px;flex:1;}
.mp-yr-fill{width:100%;border-radius:3px 3px 0 0;min-height:3px;}
.mp-yr-lbl{font-size:10px;color:var(--muted);transform:rotate(-45deg);transform-origin:top center;margin-top:4px;}
.mp-yr-num{font-size:10px;color:var(--muted);font-family:'DM Mono',monospace;}
.mp-story-card{background:var(--surface2);border-radius:8px;padding:14px 16px;
  border-left:3px solid var(--accent2);}
.mp-story-title{font-size:15px;font-weight:600;color:var(--text);margin-bottom:4px;}
.mp-story-meta{font-size:13px;color:var(--muted);line-height:1.6;}
.mp-case-table{width:100%;border-collapse:collapse;font-size:15px;margin-top:6px;}
.mp-case-table th{text-align:left;padding:10px 10px;font-size:13px;text-transform:uppercase;
  letter-spacing:.5px;color:var(--muted);border-bottom:2px solid var(--border);white-space:nowrap;}
.mp-case-table td{padding:13px 10px;border-bottom:1px solid var(--border);vertical-align:top;}
.mp-case-table tr.case-main:hover td{background:var(--surface2);cursor:pointer;}
.mp-case-caption{font-weight:600;color:var(--text);margin-bottom:5px;font-size:15px;}
.mp-case-desc{font-size:14px;color:var(--muted);line-height:1.6;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.mp-case-sig{font-size:13px;color:var(--law-blue);font-style:italic;margin-top:5px;}
.mp-expand-row td{background:var(--surface2);padding:18px 22px!important;border-bottom:2px solid var(--border);}
.mp-expand-body{font-size:14px;line-height:1.75;color:var(--text);}
.mp-expand-label{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);font-weight:600;margin-top:14px;margin-bottom:5px;}
.mp-read-more{font-size:13px;color:var(--law-blue);cursor:pointer;margin-top:4px;display:inline-block;border:none;background:none;padding:0;font-family:'DM Sans',sans-serif;}
.mp-badge{display:inline-block;padding:4px 10px;border-radius:10px;font-size:13px;font-weight:600;}
.badge-active{background:#dcfce7;color:#15803d;}
.badge-inactive{background:#f1f5f9;color:#64748b;}
.badge-uncov{background:#fff7ed;color:#c2410c;}
.mp-filter-row{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;}
.mp-fsel{border:1px solid var(--border);border-radius:7px;padding:9px 14px;
  font-size:15px;background:var(--surface);color:var(--text);font-family:'DM Sans',sans-serif;cursor:pointer;}
.mp-pub-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;
  padding:22px;border-left:4px solid var(--accent2);}
.mp-pub-card-head{font-size:17px;font-weight:700;color:var(--text);margin-bottom:7px;}
.mp-pub-card-meta{font-size:14px;color:var(--muted);margin-bottom:10px;display:flex;gap:14px;flex-wrap:wrap;}
.mp-pub-card-desc{font-size:15px;color:#334155;line-height:1.75;margin-bottom:10px;}
.mp-pub-card-sig{font-size:14px;color:var(--law-blue);font-style:italic;border-top:1px solid var(--border);padding-top:10px;margin-top:8px;}
"""

BODY = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Sue the Map: interactive AI litigation intelligence tool mapping 293 AI lawsuits across 34 US states from the DAIL database.">
<meta property="og:title" content="Sue the Map — AI Litigation Intelligence">
<meta property="og:description" content="293 AI lawsuits. 34 states. 139 uncovered. Explore the full landscape of US AI litigation.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#f4f6f9">
<title>SUE THE MAP — AI Litigation Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/globe.gl@2/dist/globe.gl.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
CSS_PLACEHOLDER
</style>
</head>
<body>
<div id="browser-warn">⚠️ Voice input works best in Chrome or Edge. All other features work in modern browsers.</div>
<div id="header">
  <div id="logo">SUE <span>THE</span> MAP</div>
  <div id="mode-toggle">
    <button class="mode-btn law-active" id="law-btn" onclick="openModePage('law')">⚖️ LAW MODE</button>
    <button class="mode-btn" id="pub-btn" onclick="openModePage('public')">🌍 PUBLIC MODE</button>
  </div>
  <button id="share-btn" onclick="shareApp()" title="Copy shareable link">🔗 Share</button>
  <div id="global-stats">
    <div class="gstat"><span class="gstat-num" id="gs-total" style="color:var(--text)">–</span><span class="gstat-lbl">Cases</span></div>
    <div class="gstat"><span class="gstat-num" id="gs-active" style="color:var(--active-green)">–</span><span class="gstat-lbl">Active</span></div>
    <div class="gstat"><span class="gstat-num" id="gs-states" style="color:var(--law-blue)">–</span><span class="gstat-lbl">States</span></div>
    <div class="gstat"><span class="gstat-num" id="gs-uncov" style="color:var(--accent2)">–</span><span class="gstat-lbl">Uncovered</span></div>
  </div>
</div>
<div id="main">
  <div id="left-panel">
    <div class="panel-tabs">
      <div class="ptab active" id="ptab-ai" onclick="switchLeft('ai')">AI Query</div>
      <div class="ptab" id="ptab-alerts" onclick="switchLeft('alerts')">
        <span id="alert-tab-law">⚠ Coverage Gap</span>
        <span id="alert-tab-pub" style="display:none">📰 Untold Stories</span>
      </div>
      <div class="ptab" id="ptab-filters" onclick="switchLeft('filters')">Filters</div>
    </div>
    <div class="tab-content" id="tab-ai">
      <div id="mic-area">
        <div id="mic-btn" onclick="toggleMic()" title="Click to speak">
          <svg viewBox="0 0 24 24"><path d="M12 15c1.66 0 3-1.34 3-3V6c0-1.66-1.34-3-3-3S9 4.34 9 6v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V6zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-2.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        </div>
        <div id="mic-status">Click 🎙 to speak your question</div>
      <div style="font-size:10px;color:#94a3b8;text-align:center;margin-top:4px">
        <kbd style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:3px;padding:1px 5px;font-size:9px">/</kbd> to focus search &nbsp;
        <kbd style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:3px;padding:1px 5px;font-size:9px">←→</kbd> cycle states
      </div>
      </div>
      <textarea id="query-box" placeholder="e.g. Which states have facial recognition cases with no media coverage?"></textarea>
      <button id="query-btn" onclick="submitQuery()">Ask AI ›</button>
      <div class="section-label" id="chips-lbl">Suggested Queries</div>
      <div class="chips" id="chips"></div>
      <div id="ai-response"></div>
    </div>
    <div class="tab-content" id="tab-alerts" style="display:none">
      <div class="alert-banner">
        <div class="ab-count" id="ab-num">–</div>
        <div class="ab-text">
          <span id="ab-law-txt">active AI lawsuits have received <strong>NO</strong> media coverage</span>
          <span id="ab-pub-txt" style="display:none">AI lawsuits have <strong>never been covered</strong> by press</span>
        </div>
      </div>
      <div class="section-label" id="alerts-title-law">Underreported Litigation — Coverage Gap Analysis</div>
      <div class="section-label" id="alerts-title-pub" style="display:none">Stories Nobody Is Covering Yet</div>
      <div id="uncov-list"></div>
    </div>
    <div class="tab-content" id="tab-filters" style="display:none">
      <div class="section-label">Status</div>
      <select class="fsel" id="f-status" onchange="applyFilters()">
        <option value="">All Statuses</option>
        <option value="active">Active Only</option>
        <option value="inactive">Inactive Only</option>
      </select>
      <div class="section-label">Sector / Area</div>
      <select class="fsel" id="f-sector" onchange="applyFilters()"></select>
      <div class="section-label">Year Filed</div>
      <select class="fsel" id="f-year" onchange="applyFilters()"></select>
      <div class="section-label">Case Type</div>
      <select class="fsel" id="f-class" onchange="applyFilters()">
        <option value="">All Cases</option>
        <option value="yes">Class Actions Only</option>
        <option value="no">Individual Cases Only</option>
      </select>
      <button class="clear-btn" onclick="clearFilters()">Clear All Filters</button>
    </div>
  </div>
  <div id="globe-container">
    <div id="globe-loading">
      <div class="gl-title">SUE <span>THE</span> MAP</div>
      <div class="spinner"></div>
      <span style="font-size:11px">Loading litigation map...</span>
    </div>
    <div id="globeViz"></div>
    <div id="year-bar"></div>
    <button id="reset-btn" onclick="resetGlobe()">&#x27F3; Reset View</button>
    <div id="legend">
      <div class="leg-title">Cases per State</div>
      <div class="leg-scale">
        <div class="leg-grad"></div>
        <div class="leg-labels"><span>0</span><span>Few</span><span>103+</span></div>
      </div>
    </div>
  </div>
  <div id="right-panel">
    <div id="right-tabs">
      <div class="rtab active" id="rtab-state" onclick="switchRight('state')">State</div>
      <div class="rtab" id="rtab-timeline" onclick="switchRight('timeline')">Timeline</div>
      <div class="rtab" id="rtab-sectors" onclick="switchRight('sectors')">Sectors</div>
    </div>
    <div id="right-body">
      <div id="tab-state">
        <div id="state-placeholder">
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".4"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          <p>Click any state on the globe to<br>see its full litigation briefing</p>
        </div>
        <div id="state-briefing"></div>
      </div>
      <div id="tab-timeline" style="display:none">
        <div class="section-label" id="tl-title-law">Annual Case Filing Trends (2011–2026)</div>
        <div class="section-label" id="tl-title-pub" style="display:none">AI Lawsuits Filed Each Year</div>
        <div id="timeline-chart"></div>
      </div>
      <div id="tab-sectors" style="display:none">
        <div class="section-label" id="sect-title-law">National Sector Breakdown</div>
        <div class="section-label" id="sect-title-pub" style="display:none">What AI Lawsuits Are About</div>
        <div id="sect-clr-wrap" style="display:none">
          <button class="clr-sect-btn" onclick="clearSectorFilter()">✕ Clear sector filter</button>
        </div>
        <div id="sectors-list"></div>
      </div>
    </div>
  </div>
</div>
<div id="footer"><span>Built with <a href="https://dail.gwlaw.edu" target="_blank">DAIL data from GW Law</a> · GeorgeHacksxAI 2026</span></div>
<div id="mode-page">
  <div id="mp-header">
    <div>
      <div id="mp-title">⚖️ Legal Intelligence Dashboard</div>
      <div id="mp-subtitle">293 AI Litigation Cases · GW Law DAIL Dataset</div>
    </div>
    <button id="mp-close" onclick="closeModePage()">✕ Back to Globe</button>
  </div>
  <div id="mp-body"></div>
</div>
<script>
let GEMINI_API_KEY = '__GEMINI_KEY__' || localStorage.getItem('sue_map_gk') || '';
"""

JS = """\
// ═══════ STATE ═══════
let mode='law',selState=null,globe=null,statesGeo=null,listening=false,recog=null;
let activeYr=null,activeSect=null;
let filters={status:'',sector:'',year:'',cls:''};

// ═══════ MAPPINGS ═══════
const N2A={
  'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
  'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
  'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
  'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
  'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
  'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH',
  'New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC',
  'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA',
  'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',
  'Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
  'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','District of Columbia':'DC'
};
const CTRS={
  CA:[-119.4,36.8],NY:[-74.2,43],IL:[-89,40],TX:[-99,31],FL:[-81.5,27.8],
  WA:[-120.5,47.4],MA:[-71.8,42.3],MI:[-84.5,44],GA:[-83.4,32.7],CO:[-105.5,39],
  VA:[-78.5,37.5],PA:[-77.2,40.9],OH:[-82.9,40.4],NJ:[-74.5,40],TN:[-86.2,35.8],
  MO:[-92.5,38.5],MN:[-94.4,46.4],AZ:[-111.5,34.3],MD:[-76.6,39.1],NC:[-79,35.5],
  IN:[-86.3,40],CT:[-72.7,41.5],WI:[-89.5,44.5],NV:[-116.9,38.8],OR:[-120.5,44],
  LA:[-92,30.9],AL:[-86.8,32.8],IA:[-93.1,42.1],UT:[-111.5,39.3],KS:[-98.4,38.5],
  DE:[-75.5,39],DC:[-77,38.9],NE:[-99.9,41.5],RI:[-71.5,41.7],SC:[-80.9,33.8]
};
const SPUB={
  'Generative AI':'AI Chatbots & Content','Facial Recognition':'Face Scanning Tech',
  'Autonomous Vehicles':'Self-Driving Cars','Civil Rights':'Civil Rights Violations',
  'Copyright':'Copyright & Ownership','Biometric Data':'Body Data Collection',
  'Criminal Justice':'Criminal Justice AI','Housing':'Housing Discrimination',
  'Health':'Healthcare AI','Social Media':'Social Media Algorithms',
  'Privacy':'Privacy Violations','Advertising':'Targeted Advertising',
  'Fraud':'AI-Enabled Fraud','Employment':'Workplace AI',
  'Intellectual Property':'Intellectual Property',
  'Constitutional Law':'Constitutional Rights','Agency':'Government AI'
};
const SCOLS={
  'Generative AI':'#ff3f3f','Civil Rights':'#4f8ef7','Copyright':'#ff8c42',
  'Facial Recognition':'#9b59b6','Biometric Data':'#e74c3c','Criminal Justice':'#27ae60',
  'Health':'#1abc9c','Housing':'#f39c12','Privacy':'#e67e22','Advertising':'#3498db',
  'Autonomous Vehicles':'#2ecc71','Fraud':'#e74c3c'
};
function sl(s){return mode==='public'?(SPUB[s]||s):s;}

// ═══════ INIT ═══════
document.addEventListener('DOMContentLoaded',()=>{
  const c=/Chrome/.test(navigator.userAgent)&&!/Edg/.test(navigator.userAgent);
  const e=/Edg/.test(navigator.userAgent);
  if(!c&&!e) document.getElementById('browser-warn').style.display='block';
  initStats(); populateFilters(); renderUncovered(); renderSectors(); renderTimeline();
  initVoice(); updateChips(); loadGlobe(); initKeyboard();
  // Auto-select the state with most cases after globe loads
  setTimeout(()=>{
    const top=Object.entries(DAIL_DATA.states).sort((a,b)=>b[1].total-a[1].total)[0];
    if(top) selectState(top[1].name);
  },2500);
});

function animCount(id,target){
  const el=document.getElementById(id);
  let cur=0;const step=Math.max(1,Math.ceil(target/50));
  const t=setInterval(()=>{cur=Math.min(cur+step,target);el.textContent=cur;if(cur>=target)clearInterval(t);},35);
}
function initStats(){
  const D=DAIL_DATA;
  animCount('gs-total',D.total_cases);
  const totalActive=Object.values(D.states).reduce((s,st)=>s+(st.active||0),0);
  animCount('gs-active',totalActive);
  document.getElementById('gs-states').textContent=Object.keys(D.states).length;
  animCount('gs-uncov',D.total_uncovered_active);
  document.getElementById('ab-num').textContent=D.total_uncovered_active;
}

// ═══════ GLOBE ═══════
function loadGlobe(){
  statesGeo=US_STATES_GEO;
  initGlobe();
}

function cntForState(name){
  const a=N2A[name],sd=a&&DAIL_DATA.states[a];if(!sd)return 0;
  if(activeSect)return sd.sectors[activeSect]||0;
  if(activeYr)return sd.years[activeYr]||0;
  if(filters.status==='active')return sd.active||0;
  if(filters.status==='inactive')return(sd.total-sd.active)||0;
  return sd.total;
}

function stateCol(name){
  const cnt=cntForState(name);
  if(cnt===0)return 'rgba(150,180,220,0.18)';
  const t=Math.min(cnt/103,1);
  if(t<0.08)return 'rgba(59,130,246,0.45)';
  if(t<0.25){const tt=(t-.08)/.17;const a=0.45+tt*0.2;return `rgba(${Math.round(59+tt*130)},${Math.round(130-tt*80)},${Math.round(246-tt*200)},${a.toFixed(2)})`; }
  if(t<0.55){const tt=(t-.25)/.3;return `rgba(${Math.round(189+tt*50)},${Math.round(50-tt*30)},${Math.round(46-tt*20)},${(0.65+tt*0.15).toFixed(2)})`; }
  return `rgba(${Math.round(220+tt*20)},${Math.round(20)},${Math.round(20)},0.88)`;
}

function getAlt(name){
  const a=N2A[name],sd=a&&DAIL_DATA.states[a];
  return sd?0.005+(sd.total/103)*0.045:0.005;
}

function ttHtml(d){
  const nm=d.properties.name,a=N2A[nm],sd=a&&DAIL_DATA.states[a];
  if(!sd)return `<div style="padding:10px 12px;font-family:'DM Sans',sans-serif;color:#0f172a;background:#fff;border-radius:8px"><b>${nm}</b><br><span style="color:#64748b;font-size:12px">No recorded cases</span></div>`;
  const top=Object.entries(sd.sectors).sort((a,b)=>b[1]-a[1])[0];
  return `<div style="padding:10px 12px;font-family:'DM Sans',sans-serif;color:#0f172a;min-width:170px;background:#fff;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.15)">
    <b style="font-size:15px;color:#0f172a">${nm}</b><br>
    <span style="color:#dc2626;font-family:'DM Mono',monospace;font-size:20px;font-weight:700">${sd.total}</span>
    <span style="color:#64748b;font-size:13px"> cases</span><br>
    <span style="color:#64748b;font-size:12px">${sd.active} active · ${sl(top[0])}</span>
    ${sd.uncovered_active>0?`<br><span style="color:#ea580c;font-size:11px;font-weight:600">⚠ ${sd.uncovered_active} uncovered</span>`:''}
  </div>`;
}

function initGlobe(){
  const el=document.getElementById('globeViz');
  document.getElementById('globe-loading').style.display='none';
  globe=Globe({animateIn:false})(el)
    .width(el.offsetWidth||800).height(el.offsetHeight||600)
    .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
    .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
    .polygonsData(statesGeo.features)
    .polygonCapColor(d=>stateCol(d.properties.name))
    .polygonSideColor(()=>'rgba(220,38,38,0.15)')
    .polygonStrokeColor(()=>'rgba(255,255,255,0.7)')
    .polygonAltitude(d=>getAlt(d.properties.name))
    .polygonLabel(d=>ttHtml(d))
    .onPolygonClick(d=>selectState(d.properties.name))
    .onPolygonHover(d=>{
      globe.polygonAltitude(dd=>{
        const base=getAlt(dd.properties.name);
        return(d&&dd===d)?base+0.025:base;
      });
    })
    .pointOfView({lat:39.5,lng:-98.35,altitude:1.75},1200);
  globe.controls().autoRotate=true;
  globe.controls().autoRotateSpeed=0.3;
  globe.controls().enableDamping=true;
  const gc=document.getElementById('globe-container');
  gc.addEventListener('mousedown',()=>globe.controls().autoRotate=false);
  gc.addEventListener('touchstart',()=>globe.controls().autoRotate=false);
  buildYearBar();
  window.addEventListener('resize',()=>{globe.width(el.offsetWidth).height(el.offsetHeight);});
}

function refreshGlobe(){
  if(!globe)return;
  globe.polygonCapColor(d=>stateCol(d.properties.name));
}

// ═══════ STATE SELECTION ═══════
function selectState(name){
  const a=N2A[name];
  if(!a||!DAIL_DATA.states[a])return;
  selState=a;
  renderBriefing(a);
  switchRight('state');
  if(globe){
    const[lng,lat]=CTRS[a]||[-98,39.5];
    globe.pointOfView({lat,lng,altitude:1.15},1200);
  }
}

// ═══════ STATE BRIEFING ═══════
function renderBriefing(a){
  const sd=DAIL_DATA.states[a];if(!sd)return;
  document.getElementById('state-placeholder').style.display='none';
  const el=document.getElementById('state-briefing');
  const classC=sd.cases.filter(c=>c.class_action).length;
  const mediaPct=sd.total>0?Math.round((sd.total_media/sd.total)*100):0;
  const statusLine=mode==='law'
    ?`${sd.total} cases filed · ${sd.active} active · ${classC} class actions`
    :`${sd.total} AI lawsuits · ${sd.active} still in court · ${classC} group cases`;
  let covAlert='';
  if(sd.uncovered_active>0){
    const n=sd.uncovered_active,s=n>1?'s':'';
    covAlert=mode==='law'
      ?`<div class="cov-alert">⚠️ ${n} active case${s} in this jurisdiction have received no secondary source coverage.</div>`
      :`<div class="cov-alert">📰 ${n} lawsuit${s} here have never been covered by press — potential story opportunity.</div>`;
  }
  const topS=Object.entries(sd.sectors).sort((a,b)=>b[1]-a[1]).slice(0,5);
  const maxS=topS[0]?.[1]||1;
  const sBars=topS.map(([s,n])=>`
    <div class="mbar-row">
      <div class="mbar-lbl" title="${sl(s)}">${sl(s)}</div>
      <div class="mbar-bg"><div class="mbar-fill" style="width:${(n/maxS*100).toFixed(1)}%"></div></div>
      <div class="mbar-cnt">${n}</div>
    </div>`).join('');
  const spark=buildSpark(sd.years);
  const caseHtml=buildCaseList(sd.cases);
  el.innerHTML=`
    <div class="sb-name">${sd.name}</div>
    <div class="sb-sub">${statusLine}</div>
    <div class="stat-cards">
      <div class="sc"><div class="sc-n">${sd.total}</div><div class="sc-l">${mode==='law'?'Total Cases':'Lawsuits'}</div></div>
      <div class="sc"><div class="sc-n" style="color:var(--active-green)">${sd.active}</div><div class="sc-l">${mode==='law'?'Active':'In Court'}</div></div>
      <div class="sc"><div class="sc-n" style="color:var(--law-blue)">${mediaPct}%</div><div class="sc-l">${mode==='law'?'Media Coverage':'In Press'}</div></div>
    </div>
    ${covAlert}
    <div class="section-label">${mode==='law'?'Top Sectors by Case Volume':'What These Lawsuits Are About'}</div>
    <div class="mini-bars">${sBars}</div>
    <div class="section-label">${mode==='law'?'Annual Filing Rate':'Lawsuits Filed Per Year'}</div>
    ${spark}
    <div class="section-label" style="margin-top:10px">${mode==='law'?'Case Docket':'All Lawsuits'} <span style="color:var(--muted);font-weight:400">(${sd.cases.length})</span></div>
    ${caseHtml}`;
}

function buildSpark(yrData){
  const yrs=Object.keys(yrData).sort();if(!yrs.length)return '';
  const W=284,H=50,vals=yrs.map(y=>yrData[y]),maxV=Math.max(...vals,1);
  const xS=i=>(i/(yrs.length-1||1))*(W-20)+10;
  const yS=v=>H-6-(v/maxV)*(H-12);
  const pts=yrs.map((y,i)=>`${xS(i).toFixed(1)},${yS(yrData[y]).toFixed(1)}`).join(' ');
  const dots=yrs.map((y,i)=>`<circle cx="${xS(i).toFixed(1)}" cy="${yS(yrData[y]).toFixed(1)}" r="2" fill="var(--law-blue)"/>`).join('');
  const lbls=yrs.map((y,i)=>`<text x="${xS(i).toFixed(1)}" y="${H}" text-anchor="middle" font-size="8" fill="var(--muted)" font-family="DM Mono,monospace">${y.slice(2)}</text>`).join('');
  return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:${H}px;overflow:visible">
    <polyline points="${pts}" fill="none" stroke="var(--law-blue)" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" opacity=".8"/>
    ${dots}${lbls}</svg>`;
}

function buildCaseList(cases){
  let c=[...cases];
  if(filters.status==='active')c=c.filter(x=>x.status.toLowerCase().includes('active'));
  if(filters.status==='inactive')c=c.filter(x=>!x.status.toLowerCase().includes('active'));
  if(activeSect)c=c.filter(x=>x.sector===activeSect);
  if(activeYr)c=c.filter(x=>x.year&&String(x.year)===activeYr);
  if(filters.cls==='yes')c=c.filter(x=>x.class_action);
  if(filters.cls==='no')c=c.filter(x=>!x.class_action);
  if(!c.length)return '<div style="text-align:center;color:var(--muted);padding:16px;font-size:11px">No cases match current filters</div>';
  return c.slice(0,30).map(x=>{
    const ia=x.status.toLowerCase().includes('active');
    const sb=ia?`<span class="badge b-active">${mode==='law'?'Active':'In Court'}</span>`:`<span class="badge b-inactive">${mode==='law'?'Inactive':'Settled'}</span>`;
    const cb=x.class_action?`<span class="badge b-class">${mode==='law'?'Class Action':'Group Case'}</span>`:'';
    const sectb=`<span class="badge b-sector">${sl(x.sector)}</span>`;
    const dots=Array(5).fill(0).map((_,i)=>`<div class="mdot ${i<x.media_count?'':'empty'}"></div>`).join('');
    const srcs=x.sources&&x.sources.length?`<div class="cc-src">${x.sources.slice(0,2).map(s=>`<a href="${s.link}" target="_blank" rel="noopener">📎 ${(s.title||'').slice(0,55)}${(s.title||'').length>55?'...':''}</a>`).join('')}</div>`:'';
    const desc=(x.description||'').slice(0,mode==='law'?155:125);
    return `<div class="case-card">
      <div class="cc-title">${x.caption}</div>
      <div class="cc-badges">${sb}${cb}${sectb}<span style="font-size:10px;color:var(--muted)">${x.year||''}</span></div>
      <div class="cc-desc">${desc}${desc.length<(x.description||'').length?'…':''}</div>
      <div class="cc-media">${dots}<span style="font-size:10px;color:var(--muted);margin-left:4px">${x.media_count===0?'No coverage':x.media_count+' source'+(x.media_count>1?'s':'')}</span></div>
      ${srcs}</div>`;
  }).join('');
}

// ═══════ KEYBOARD NAV ═══════
function initKeyboard(){
  const stList=Object.keys(DAIL_DATA.states);
  document.addEventListener('keydown',e=>{
    if(e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT')return;
    if(e.key==='ArrowRight'||e.key==='ArrowLeft'){
      const i=selState?stList.indexOf(selState):-1;
      const next=e.key==='ArrowRight'?stList[(i+1)%stList.length]:stList[(i-1+stList.length)%stList.length];
      selectState(DAIL_DATA.states[next].name);
    }
    if(e.key==='Escape')resetGlobe();
    if(e.key==='/'){
      e.preventDefault();
      document.getElementById('query-box').focus();
      switchLeft('ai');
    }
  });
}

function shareApp(){
  const url=window.location.href+(selState?'#'+selState:'');
  navigator.clipboard.writeText(url).then(()=>{
    const b=document.getElementById('share-btn');
    b.textContent='✓ Copied!';b.classList.add('copied');
    setTimeout(()=>{b.textContent='🔗 Share';b.classList.remove('copied');},2000);
  }).catch(()=>{
    prompt('Copy this link:',window.location.href);
  });
}

function resetGlobe(){
  if(!globe)return;
  globe.controls().autoRotate=true;
  globe.pointOfView({lat:39.5,lng:-98.35,altitude:1.75},1000);
  selState=null;
  document.getElementById('state-placeholder').style.display='';
  document.getElementById('state-briefing').innerHTML='';
}

// ═══════ TIMELINE ═══════
function renderTimeline(){
  const ct=document.getElementById('timeline-chart');if(!ct)return;
  const W=ct.offsetWidth||292,H=220,m={t:22,r:8,b:38,l:28},iW=W-m.l-m.r,iH=H-m.t-m.b;
  const yt=DAIL_DATA.year_trends;
  const yrs=Object.keys(yt).filter(y=>parseInt(y)>=2011&&parseInt(y)<=2026).sort();
  const vals=yrs.map(y=>yt[y].total),maxV=Math.max(...vals,1);
  const bW=Math.max(4,iW/yrs.length-2);
  const xS=i=>m.l+i*(iW/yrs.length)+(iW/yrs.length-bW)/2;
  const yS=v=>m.t+iH-(v/maxV)*iH;
  const bH=v=>(v/maxV)*iH;
  function bCol(y){const s=yt[y]?.sectors;if(!s)return '#252538';const t=Object.entries(s).sort((a,b)=>b[1]-a[1])[0];return SCOLS[t?.[0]]||'#4f8ef7';}
  let svg=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;overflow:visible;font-family:'DM Sans',sans-serif">`;
  for(let i=0;i<=4;i++){
    const y2=m.t+iH*(1-i/4),v=Math.round(maxV*i/4);
    svg+=`<line x1="${m.l}" y1="${y2.toFixed(1)}" x2="${m.l+iW}" y2="${y2.toFixed(1)}" stroke="#252538" stroke-width="0.5"/>
      <text x="${m.l-3}" y="${(y2+3).toFixed(1)}" text-anchor="end" font-size="8" fill="#5a5a7a" font-family="DM Mono,monospace">${v}</text>`;
  }
  yrs.forEach((y,i)=>{
    const v=vals[i],x=xS(i),h=bH(v),by=yS(v);
    const isA=activeYr===y,op=activeYr&&!isA?0.3:0.88;
    svg+=`<rect x="${(x+(isA?-1:0)).toFixed(1)}" y="${m.t+iH}" width="${(bW+(isA?2:0)).toFixed(1)}" height="0" fill="${bCol(y)}" rx="2" opacity="${op}" style="cursor:pointer" onclick="setYear('${y}')">
      <animate attributeName="height" from="0" to="${h.toFixed(1)}" dur="${(0.25+i*0.025).toFixed(2)}s" begin="0.1s" fill="freeze"/>
      <animate attributeName="y" from="${m.t+iH}" to="${by.toFixed(1)}" dur="${(0.25+i*0.025).toFixed(2)}s" begin="0.1s" fill="freeze"/>
    </rect>`;
    if(h>12)svg+=`<text x="${(x+bW/2).toFixed(1)}" y="${(by-2.5).toFixed(1)}" text-anchor="middle" font-size="7.5" fill="#e8e8f2" opacity="0.65">${v}</text>`;
    if(i%2===0||yrs.length<=12)svg+=`<text x="${(x+bW/2).toFixed(1)}" y="${m.t+iH+13}" text-anchor="middle" font-size="8.5" fill="#5a5a7a" font-family="DM Mono,monospace">${y.slice(2)}</text>`;
  });
  const i22=yrs.indexOf('2022'),i23=yrs.indexOf('2023');
  if(i22>=0&&i23>=0){
    const ax=(xS(i22)+xS(i23))/2+bW/2,ay=Math.min(yS(vals[i22]),yS(vals[i23]))-22;
    svg+=`<line x1="${ax.toFixed(1)}" y1="${(ay+19).toFixed(1)}" x2="${ax.toFixed(1)}" y2="${(Math.min(yS(vals[i22]),yS(vals[i23]))-1).toFixed(1)}" stroke="#ff8c42" stroke-width="1" stroke-dasharray="3,2"/>
    <rect x="${(ax-56).toFixed(1)}" y="${(ay-4).toFixed(1)}" width="112" height="22" rx="3" fill="rgba(255,140,66,0.12)" stroke="rgba(255,140,66,0.4)" stroke-width="0.5"/>
    <text x="${ax.toFixed(1)}" y="${(ay+7).toFixed(1)}" text-anchor="middle" font-size="8.5" fill="#ff8c42">ChatGPT launches →</text>
    <text x="${ax.toFixed(1)}" y="${(ay+17).toFixed(1)}" text-anchor="middle" font-size="8.5" fill="#ff8c42">GenAI litigation surges</text>`;
  }
  svg+='</svg>';
  ct.innerHTML=svg;
}

function buildYearBar(){
  const el=document.getElementById('year-bar');
  const yrs=Object.keys(DAIL_DATA.year_trends).filter(y=>parseInt(y)>=2017).sort().reverse();
  el.innerHTML=`<div class="yc ${!activeYr?'on':''}" onclick="setYear(null)">All</div>`+
    yrs.map(y=>`<div class="yc ${activeYr===y?'on':''}" onclick="setYear('${y}')">${y}</div>`).join('');
}

function setYear(y){
  activeYr=(activeYr===y)?null:y;
  buildYearBar();refreshGlobe();renderTimeline();
  if(selState)renderBriefing(selState);
}

// ═══════ SECTORS ═══════
function renderSectors(){
  const el=document.getElementById('sectors-list');if(!el)return;
  const s=Object.entries(DAIL_DATA.sector_totals).sort((a,b)=>b[1]-a[1]).slice(0,14);
  const maxC=s[0]?.[1]||1;
  el.innerHTML=s.map(([sec,n],i)=>`
    <div class="sector-row ${activeSect===sec?'on':''}" onclick="setSector('${sec}')">
      <div class="sr-rank">${String(i+1).padStart(2,'0')}</div>
      <div class="sr-name">${sl(sec)}</div>
      <div class="sr-bar-bg"><div class="sr-bar-fill" style="width:${(n/maxC*100).toFixed(1)}%"></div></div>
      <div class="sr-cnt">${n}</div>
    </div>`).join('');
}

function setSector(s){
  activeSect=(activeSect===s)?null:s;
  document.getElementById('sect-clr-wrap').style.display=activeSect?'block':'none';
  renderSectors();refreshGlobe();if(selState)renderBriefing(selState);
}

function clearSectorFilter(){
  activeSect=null;
  document.getElementById('sect-clr-wrap').style.display='none';
  renderSectors();refreshGlobe();if(selState)renderBriefing(selState);
}

// ═══════ JOURNALIST ALERTS ═══════
function renderUncovered(){
  const cases=[];
  for(const[a,sd]of Object.entries(DAIL_DATA.states)){
    for(const c of sd.cases){
      if(c.media_count===0&&c.status.toLowerCase().includes('active')){
        cases.push({...c,stAbbr:a,stName:sd.name});
      }
    }
  }
  cases.sort((a,b)=>(b.significance?.length||0)-(a.significance?.length||0));
  document.getElementById('ab-num').textContent=cases.length;
  const el=document.getElementById('uncov-list');
  el.innerHTML=cases.slice(0,50).map(c=>`
    <div class="uc-card" onclick="selectState('${c.stName}')">
      <div class="uc-caption">${c.caption}</div>
      <div class="uc-meta">
        <span class="badge b-state">${c.stAbbr}</span>
        <span class="badge b-sector">${sl(c.sector)}</span>
        ${c.year?`<span style="font-size:10px;color:var(--muted)">${c.year}</span>`:''}
        ${c.class_action?`<span class="badge b-class">${mode==='law'?'Class Action':'Group Case'}</span>`:''}
      </div>
      ${c.significance?`<div class="uc-sig">${c.significance.slice(0,120)}${c.significance.length>120?'…':''}</div>`:''}
    </div>`).join('');
}

// ═══════ FILTERS ═══════
function populateFilters(){
  const se=document.getElementById('f-sector');
  se.innerHTML='<option value="">All Sectors</option>'+
    Object.keys(DAIL_DATA.sector_totals).sort().map(s=>`<option value="${s}">${s}</option>`).join('');
  const ye=document.getElementById('f-year');
  ye.innerHTML='<option value="">All Years</option>'+
    Object.keys(DAIL_DATA.year_trends).filter(y=>parseInt(y)>=2011).sort().reverse()
      .map(y=>`<option value="${y}">${y}</option>`).join('');
}

function applyFilters(){
  filters.status=document.getElementById('f-status').value;
  filters.sector=document.getElementById('f-sector').value;
  filters.year=document.getElementById('f-year').value;
  filters.cls=document.getElementById('f-class').value;
  if(filters.sector)activeSect=filters.sector;
  if(filters.year)activeYr=filters.year;
  refreshGlobe();if(selState)renderBriefing(selState);
}

function clearFilters(){
  ['f-status','f-sector','f-year','f-class'].forEach(id=>document.getElementById(id).value='');
  filters={status:'',sector:'',year:'',cls:''};
  activeSect=null;activeYr=null;
  buildYearBar();refreshGlobe();if(selState)renderBriefing(selState);
}

// ═══════ VOICE ═══════
function initVoice(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){document.getElementById('mic-btn').style.opacity='0.4';document.getElementById('mic-status').textContent='Voice not supported';return;}
  recog=new SR();recog.lang='en-US';recog.continuous=false;recog.interimResults=false;
  recog.onstart=()=>{listening=true;document.getElementById('mic-btn').classList.add('listening');document.getElementById('mic-status').textContent='🔴 Listening...';};
  recog.onend=()=>{listening=false;document.getElementById('mic-btn').classList.remove('listening');document.getElementById('mic-status').textContent='Click 🎙 to speak';};
  recog.onerror=e=>{listening=false;document.getElementById('mic-btn').classList.remove('listening');document.getElementById('mic-status').textContent=e.error==='not-allowed'?'❌ Mic access denied':'Try again';};
  recog.onresult=e=>{const t=e.results[0][0].transcript;document.getElementById('query-box').value=t;submitQuery();};
}

function toggleMic(){
  if(!recog)return;
  if(listening){recog.stop();}else{try{recog.start();}catch(e){document.getElementById('mic-status').textContent='Error — try again';}}
}

// ═══════ CHIPS ═══════
const LAW_CHIPS=['Most GenAI cases by jurisdiction?','Facial recognition — no press coverage','Civil rights AI cases by state','California class action trends'];
const PUB_CHIPS=["Which states sue over AI chatbots?","AI lawsuits nobody's covering yet","Tell me about face scanning lawsuits","State with the most AI lawsuits?"];

function updateChips(){
  const c=mode==='law'?LAW_CHIPS:PUB_CHIPS;
  document.getElementById('chips-lbl').textContent=mode==='law'?'Suggested Queries':'Try Asking';
  document.getElementById('chips').innerHTML=c.map(q=>`<div class="chip" onclick="useChip(this)" data-q="${q.replace(/"/g,'&quot;')}">💬 ${q.slice(0,40)}${q.length>40?'...':''}</div>`).join('');
}

function useChip(el){document.getElementById('query-box').value=el.dataset.q;submitQuery();}

// ═══════ API KEY MANAGEMENT ═══════
function setApiKey(){
  const k=prompt('Paste your Google Gemini API key (stored locally in your browser only):');
  if(k&&k.trim().startsWith('AIza')){
    GEMINI_API_KEY=k.trim();
    localStorage.setItem('sue_map_gk',GEMINI_API_KEY);
    document.getElementById('ai-response').innerHTML='<span style="color:var(--active-green)">✓ API key saved. Ask your question!</span>';
  } else if(k!==null){
    alert('That does not look like a Gemini key (should start with AIza…). Try again.');
  }
}
function clearApiKey(){
  localStorage.removeItem('sue_map_gk');GEMINI_API_KEY='';
  alert('API key cleared.');
}

// ═══════ TEXT TO SPEECH ═══════
let speaking=false;
function speakText(text){
  if(!window.speechSynthesis)return;
  window.speechSynthesis.cancel();
  const utt=new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g,''));
  utt.rate=0.95;utt.pitch=1;utt.volume=1;
  const voices=window.speechSynthesis.getVoices();
  const pref=voices.find(v=>v.lang==='en-US'&&v.name.includes('Female'))||voices.find(v=>v.lang==='en-US')||voices[0];
  if(pref)utt.voice=pref;
  utt.onstart=()=>{speaking=true;document.getElementById('speak-btn').textContent='⏹ Stop';}
  utt.onend=()=>{speaking=false;document.getElementById('speak-btn').textContent='🔊 Read Aloud';}
  window.speechSynthesis.speak(utt);
}
function toggleSpeak(){
  if(speaking){window.speechSynthesis.cancel();speaking=false;document.getElementById('speak-btn').textContent='🔊 Read Aloud';}
  else{const t=document.getElementById('ai-response').innerText;if(t)speakText(t);}
}

// ═══════ GEMINI API ═══════
async function submitQuery(){
  const q=document.getElementById('query-box').value.trim();if(!q)return;
  const btn=document.getElementById('query-btn');
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>';
  const resp=document.getElementById('ai-response');
  resp.classList.add('show');resp.innerHTML='<span class="spinner"></span> Analyzing...';
  if(!GEMINI_API_KEY){
    resp.innerHTML='<span style="color:var(--accent2)">⚠️ No API key set.</span> <button onclick="setApiKey()" style="margin-left:6px;padding:2px 10px;border:1px solid var(--law-blue);border-radius:4px;background:none;color:var(--law-blue);cursor:pointer;font-size:13px">Enter Gemini Key ›</button>';
    btn.disabled=false;btn.innerHTML='Ask AI ›';return;
  }
  const lSys='You are a legal research analyst for the DAIL (Database of AI Litigation) maintained by GW Law. Answer in precise legal terminology. Reference specific jurisdictions, causes of action, and legal issues. Be analytical. 3-4 sentences.';
  const pSys="You are a journalist explaining AI lawsuits to everyday people. Use plain language, zero jargon. Make it feel like a news brief. 2-3 sentences max.";
  const top10=Object.entries(DAIL_DATA.states).sort((a,b)=>b[1].total-a[1].total).slice(0,10).map(([k,v])=>`${k}(${v.total})`).join(',');
  const ctx=`Dataset: ${DAIL_DATA.total_cases} AI litigation cases (2011-2026) across ${Object.keys(DAIL_DATA.states).length} US states.
States by volume: ${top10}
Top sectors: ${Object.entries(DAIL_DATA.sector_totals).slice(0,7).map(([k,v])=>`${k}(${v})`).join(',')}
Yearly trend: ${Object.entries(DAIL_DATA.year_trends).filter(([y])=>parseInt(y)>=2020).map(([y,v])=>`${y}(${v.total})`).join(',')}
${DAIL_DATA.total_uncovered_active} active cases have zero media coverage.
Current filter: sector=${activeSect||'none'}, year=${activeYr||'none'}
Question: ${q}`;
  try{
    const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        contents:[{role:'user',parts:[{text:(mode==='law'?lSys:pSys)+'\\n\\n'+ctx}]}],
        generationConfig:{maxOutputTokens:400}
      })
    });
    if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.error?.message||`HTTP ${r.status}`);}
    const data=await r.json();
    const text=data.candidates?.[0]?.content?.parts?.[0]?.text||'No response.';
    resp.innerHTML=`<div style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">AI ${mode==='law'?'Legal':'News'} Briefing</div>${text}
    <br><button id="speak-btn" onclick="toggleSpeak()" style="margin-top:8px;background:var(--surface2);border:1px solid var(--border);border-radius:7px;padding:5px 12px;font-size:12px;cursor:pointer;font-family:'DM Sans',sans-serif;color:var(--text)">🔊 Read Aloud</button>`;
    speakText(text);
    const mentioned=Object.values(DAIL_DATA.states).map(s=>s.name).find(n=>text.includes(n));
    if(mentioned)selectState(mentioned);
  }catch(e){
    resp.innerHTML=`<span style="color:var(--accent)">⚠ Error: ${e.message}</span>`;
  }
  btn.disabled=false;btn.innerHTML='Ask AI ›';
}

// ═══════ MODE SWITCH ═══════
function setMode(m){
  mode=m;
  document.getElementById('law-btn').className='mode-btn'+(m==='law'?' law-active':'');
  document.getElementById('pub-btn').className='mode-btn'+(m==='public'?' pub-active':'');
  [['alert-tab-law','alert-tab-pub'],['ab-law-txt','ab-pub-txt'],
   ['alerts-title-law','alerts-title-pub'],['tl-title-law','tl-title-pub'],
   ['sect-title-law','sect-title-pub']].forEach(([l,p])=>{
    document.getElementById(l).style.display=m==='law'?'':'none';
    document.getElementById(p).style.display=m==='public'?'':'none';
  });
  updateChips();renderSectors();renderUncovered();renderTimeline();
  if(selState)renderBriefing(selState);
}

// ═══════ MODE PAGE ═══════
function openModePage(m){
  setMode(m);
  const pg=document.getElementById('mode-page');
  const hdr=document.getElementById('mp-title');
  const sub=document.getElementById('mp-subtitle');
  if(m==='law'){
    hdr.textContent='\u2696\ufe0f Legal Intelligence Dashboard';
    sub.textContent='293 AI Litigation Cases \u00b7 GW Law DAIL Dataset';
  } else {
    hdr.textContent='📰 The Untold Story';
    sub.textContent='Active AI lawsuits the media isn\u2019t covering';
  }
  pg.classList.add('open');
  pg.scrollTop=0;
  if(m==='law')renderLawPage();else renderPublicPage();
}
function closeModePage(){
  document.getElementById('mode-page').classList.remove('open');
}
function _bar(label,val,max,color){
  return `<div class="mp-bar-row">
    <div class="mp-bar-label" title="${label}">${label}</div>
    <div class="mp-bar-track"><div class="mp-bar-fill" style="width:${(val/max*100).toFixed(1)}%;background:${color}"></div></div>
    <div class="mp-bar-val">${val}</div></div>`;
}
function _yrBars(years,color){
  const mx=Math.max(...years.map(([,v])=>v.total));
  return years.map(([yr,v])=>`<div class="mp-yr-col">
    <div class="mp-yr-num">${v.total}</div>
    <div class="mp-yr-fill" style="height:${Math.max(3,(v.total/mx*88)).toFixed(0)}px;background:${color}"></div>
    <div class="mp-yr-lbl">${yr}</div></div>`).join('');
}
function renderLawPage(){
  const D=DAIL_DATA;
  const totalActive=Object.values(D.states).reduce((s,st)=>s+(st.active||0),0);
  const topStates=Object.entries(D.states).sort((a,b)=>b[1].total-a[1].total).slice(0,10);
  const sectors=Object.entries(D.sector_totals).sort((a,b)=>b[1]-a[1]).slice(0,8);
  const years=Object.entries(D.year_trends).filter(([y])=>parseInt(y)>=2015).sort(([a],[b])=>a-b);
  const covGap=Object.entries(D.states).filter(([,s])=>s.uncovered_active>0)
    .sort((a,b)=>b[1].uncovered_active-a[1].uncovered_active).slice(0,8);
  const allCases=Object.values(D.states).flatMap(s=>s.cases||[]);
  document.getElementById('mp-body').innerHTML=`
  <div class="mp-stats">
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--text)">${D.total_cases}</div><div class="mp-stat-lbl">Total AI Cases (2011\u20132026)</div></div>
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--active-green)">${totalActive}</div><div class="mp-stat-lbl">Active Litigations</div></div>
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--law-blue)">${Object.keys(D.states).length}</div><div class="mp-stat-lbl">States with AI Cases</div></div>
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--accent2)">${D.total_uncovered_active}</div><div class="mp-stat-lbl">Active \u2014 Zero Coverage</div></div>
  </div>
  <div class="mp-grid">
    <div class="mp-card">
      <div class="mp-card-title">Top 10 States by Case Volume</div>
      ${topStates.map(([c,s])=>_bar(s.name||c,s.total,topStates[0][1].total,'var(--accent)')).join('')}
    </div>
    <div class="mp-card">
      <div class="mp-card-title">Sector Breakdown</div>
      ${sectors.map(([n,v])=>_bar(n,v,sectors[0][1],'var(--law-blue)')).join('')}
    </div>
    <div class="mp-card">
      <div class="mp-card-title">Annual Filing Trends (2015\u20132026)</div>
      <div class="mp-year-bar">${_yrBars(years,'var(--law-blue)')}</div>
    </div>
    <div class="mp-card">
      <div class="mp-card-title">Coverage Gap \u2014 Unreported Active Cases by State</div>
      <table style="width:100%;border-collapse:collapse;font-size:12px;">
        <thead><tr style="color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.4px">
          <th style="text-align:left;padding:4px 0">State</th>
          <th style="text-align:right;padding:4px 6px">Total</th>
          <th style="text-align:right;padding:4px 6px">Active</th>
          <th style="text-align:right;padding:4px 0;color:var(--accent2)">Uncovered</th>
        </tr></thead><tbody>
        ${covGap.map(([c,s])=>`<tr style="border-top:1px solid var(--border)">
          <td style="padding:7px 0;font-weight:500">${s.name||c}</td>
          <td style="text-align:right;color:var(--muted);padding:7px 6px">${s.total}</td>
          <td style="text-align:right;color:var(--active-green);padding:7px 6px">${s.active}</td>
          <td style="text-align:right;color:var(--accent2);font-weight:700;padding:7px 0">${s.uncovered_active}</td>
        </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>
  <div class="mp-card" style="margin-top:18px">
    <div class="mp-card-title">All Cases \u2014 Full Litigation Index (${allCases.length})</div>
    <div class="mp-filter-row">
      <select class="mp-fsel" id="lf-status" onchange="filterLawCases()">
        <option value="">All Statuses</option>
        <option value="Active">Active Only</option>
        <option value="Inactive">Inactive Only</option>
      </select>
      <select class="mp-fsel" id="lf-sector" onchange="filterLawCases()">
        <option value="">All Sectors</option>
        ${Object.keys(D.sector_totals).sort().map(s=>`<option value="${s}">${s}</option>`).join('')}
      </select>
      <select class="mp-fsel" id="lf-year" onchange="filterLawCases()">
        <option value="">All Years</option>
        ${Object.keys(D.year_trends).sort((a,b)=>b-a).map(y=>`<option value="${y}">${y}</option>`).join('')}
      </select>
      <select class="mp-fsel" id="lf-cov" onchange="filterLawCases()">
        <option value="">Any Coverage</option>
        <option value="0">No Media Coverage</option>
      </select>
      <span id="lf-count" style="font-size:14px;color:var(--muted);align-self:center;margin-left:4px"></span>
    </div>
    <div style="overflow-x:auto">
      <table class="mp-case-table" id="law-case-table">
        <thead><tr>
          <th style="min-width:220px">Case</th>
          <th>State</th>
          <th>Year</th>
          <th>Sector</th>
          <th>Status</th>
          <th>Media</th>
          <th>Class Action</th>
        </tr></thead>
        <tbody id="law-case-tbody"></tbody>
      </table>
    </div>
  </div>`;
  window._lawCases=allCases;
  filterLawCases();
}
function filterLawCases(){
  const status=document.getElementById('lf-status')?.value||'';
  const sector=document.getElementById('lf-sector')?.value||'';
  const year=document.getElementById('lf-year')?.value||'';
  const cov=document.getElementById('lf-cov')?.value||'';
  let cases=(window._lawCases||[]).filter(c=>{
    if(status&&c.status!==status)return false;
    if(sector&&c.sector!==sector)return false;
    if(year&&String(c.year)!==year)return false;
    if(cov==='0'&&c.media_count>0)return false;
    return true;
  });
  const tbody=document.getElementById('law-case-tbody');
  if(!tbody)return;
  document.getElementById('lf-count').textContent=`${cases.length} case${cases.length!==1?'s':''}`;
  tbody.innerHTML=cases.map((c,i)=>{
    const rowId=`cr-${i}`;
    const hasMore=(c.description&&c.description.length>0)||c.issues||c.significance||c.orgs;
    return `<tr class="case-main" onclick="toggleCase('${rowId}')">
    <td>
      <div class="mp-case-caption">${c.caption||'—'}</div>
      ${c.description?`<div class="mp-case-desc">${c.description}</div>`:''}${hasMore?`<button class="mp-read-more" onclick="event.stopPropagation();toggleCase('${rowId}')">+ Read full story</button>`:''}
    </td>
    <td style="white-space:nowrap">${c.state||'—'}</td>
    <td style="white-space:nowrap;font-family:'DM Mono',monospace">${c.year||'—'}</td>
    <td style="white-space:nowrap;font-size:13px;color:var(--muted)">${c.sector||'—'}</td>
    <td><span class="mp-badge ${c.status==='Active'?'badge-active':'badge-inactive'}">${c.status||'—'}</span></td>
    <td style="text-align:center;font-family:'DM Mono',monospace">${c.media_count===0?'<span class="mp-badge badge-uncov">None</span>':c.media_count}</td>
    <td style="text-align:center">${c.class_action?'Yes':'No'}</td>
  </tr>
  <tr id="${rowId}" class="mp-expand-row" style="display:none">
    <td colspan="7">
      <div class="mp-expand-body">
        ${c.description?`<div class="mp-expand-label">What Happened</div><div>${c.description}</div>`:''}
        ${c.significance?`<div class="mp-expand-label">Why It Matters</div><div style="color:var(--law-blue)">${c.significance}</div>`:''}
        ${c.issues?`<div class="mp-expand-label">Legal Issues</div><div style="color:var(--muted)">${c.issues}</div>`:''}
        ${c.orgs?`<div class="mp-expand-label">Organizations</div><div style="color:var(--muted)">${c.orgs}</div>`:''}
      </div>
    </td>
  </tr>`;
  }).join('');
}
function toggleCase(id){
  const row=document.getElementById(id);
  if(!row)return;
  const open=row.style.display!=='none';
  row.style.display=open?'none':'table-row';
  const btn=row.previousElementSibling?.querySelector('.mp-read-more');
  if(btn)btn.textContent=open?'+ Read full story':'\u2212 Collapse';
}
function renderPublicPage(){
  const D=DAIL_DATA;
  const totalActive=Object.values(D.states).reduce((s,st)=>s+(st.active||0),0);
  const years=Object.entries(D.year_trends).filter(([y])=>parseInt(y)>=2015).sort(([a],[b])=>a-b);
  const topSectors=Object.entries(D.sector_totals).sort((a,b)=>b[1]-a[1]).slice(0,6);
  const uncovCases=Object.values(D.states)
    .flatMap(s=>(s.cases||[]).filter(c=>c.status==='Active'&&c.media_count===0))
    .sort((a,b)=>(b.year||0)-(a.year||0));
  document.getElementById('mp-body').innerHTML=`
  <div class="mp-stats">
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--text)">${D.total_cases}</div><div class="mp-stat-lbl">AI Lawsuits Filed in the US</div></div>
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--active-green)">${totalActive}</div><div class="mp-stat-lbl">Still Active in Courts</div></div>
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--accent2)">${D.total_uncovered_active}</div><div class="mp-stat-lbl">Active Cases \u2014 No Press</div></div>
    <div class="mp-stat"><div class="mp-stat-num" style="color:var(--law-blue)">${Object.keys(D.states).length}</div><div class="mp-stat-lbl">States Affected</div></div>
  </div>
  <div class="mp-grid">
    <div class="mp-card">
      <div class="mp-card-title">Which industries are getting sued most?</div>
      ${topSectors.map(([n,v])=>_bar(n,v,topSectors[0][1],'var(--accent2)')).join('')}
    </div>
    <div class="mp-card">
      <div class="mp-card-title">Is it getting worse? Lawsuits filed each year</div>
      <div class="mp-year-bar">${_yrBars(years,'var(--accent)')}</div>
      <p style="font-size:13px;color:var(--muted);margin-top:12px">Filings surged after 2022 \u2014 when mainstream AI tools launched and people began suing.</p>
    </div>
  </div>
  <div class="mp-card" style="margin-top:18px">
    <div class="mp-card-title">\u26a0 Stories Nobody Is Writing \u2014 ${uncovCases.length} Active Cases With Zero Media Coverage</div>
    <p style="font-size:14px;color:var(--muted);margin-bottom:18px">These are real lawsuits happening right now. No reporters. No press. Just people in court fighting AI companies.</p>
    <div style="display:flex;flex-direction:column;gap:12px">
      ${uncovCases.map(c=>`<div class="mp-pub-card">
        <div class="mp-pub-card-head">${c.caption||'Unnamed Case'}</div>
        <div class="mp-pub-card-meta">
          <span>📍 ${c.state||'Unknown'}</span>
          <span>📅 Filed ${c.year||'?'}</span>
          <span>🏭 ${c.sector||'Unknown sector'}</span>
          ${c.class_action?'<span style="color:var(--law-blue);font-weight:600">Class Action</span>':''}
        </div>
        ${c.description?`<div class="mp-pub-card-desc">${c.description}</div>`:''}
        ${c.significance?`<div class="mp-pub-card-sig">Why it matters: ${c.significance}</div>`:''}
      </div>`).join('')}
    </div>
  </div>`;
}

// ═══════ TABS ═══════
function switchLeft(t){
  ['ai','alerts','filters'].forEach(x=>{
    document.getElementById('ptab-'+x).classList.toggle('active',x===t);
    document.getElementById('tab-'+x).style.display=x===t?'':'none';
  });
}

function switchRight(t){
  ['state','timeline','sectors'].forEach(x=>{
    document.getElementById('rtab-'+x).classList.toggle('active',x===t);
    document.getElementById('tab-'+x).style.display=x===t?'':'none';
  });
  if(t==='timeline')renderTimeline();
  if(t==='sectors')renderSectors();
}
"""

CLOSE = "\n</script>\n</body>\n</html>"

final = BODY.replace('CSS_PLACEHOLDER', CSS) + "const DAIL_DATA = " + dail_json_safe + ";\nconst US_STATES_GEO = " + geo_json_safe + ";\n" + JS + CLOSE
final = final.replace('__GEMINI_KEY__', GEMINI_KEY)

with open('sue_the_map.html', 'w', encoding='utf-8') as f:
    f.write(final)

size = len(final)
print(f"Generated sue_the_map.html")
print(f"File size: {size // 1024} KB ({size:,} bytes)")
print("Open sue_the_map.html in Chrome or Edge to run it.")

"""Render the authored Markdown report and generated demo appendix to standalone HTML."""
from pathlib import Path
import html,re
from seed import DEMOS,opportunities
from server import score,draft
root=Path(__file__).parent
md=(root/'docs/REPORT.md').read_text(); parts=[]
for block in md.split('\n\n'):
 lines=block.splitlines()
 for line in lines:
  line=html.escape(line)
  line=re.sub(r'https://[^\s<]+',lambda m:'<a href="'+m[0]+'">'+m[0]+'</a>',line)
  if line.startswith('#'):
   n=len(line)-len(line.lstrip('#')); parts.append(f'<h{n}>'+line[n:].strip()+f'</h{n}>')
  else: parts.append('<p>'+line+'</p>')
parts.append('<h2>Appendix: opportunity comparison and email drafts</h2><p>Generated from the same curated research and drafting code as the application. Access and company-size qualification remain unverified for all prospects. These are proposals, not confirmed client needs.</p>')
for name in DEMOS:
 parts.append('<h2>'+name+'</h2><p>'+html.escape(opportunities(name)[0]['target_fit'])+'</p>')
 for o in sorted(opportunities(name),key=lambda o:-score(o)):
  subject,body=draft(name,o)
  parts.append('<section><h3>'+html.escape(o['team'])+' · '+str(score(o))+'/100</h3><p><strong>'+html.escape(o['title'])+'</strong></p><p>'+html.escape(o['scope'])+'</p><p>Success measure: '+html.escape(o['metric'])+'</p><p>Suggested role: '+html.escape(o['role'])+'</p><p>Subject: '+html.escape(subject)+'</p><pre>'+html.escape(body)+'</pre></section>')
style='body{font:15px/1.7 system-ui;color:#243e33;background:#f4f5ef;max-width:940px;margin:45px auto;padding:35px}h1,h2{font-family:Georgia}h1{font-size:44px}h2{font-size:27px;margin-top:40px}h3{margin-top:32px}a{color:#28674e;overflow-wrap:anywhere}pre{font:14px/1.7 system-ui;white-space:pre-wrap;background:#fff;padding:24px;border:1px solid #d9dfd3;border-radius:8px}section{margin:30px 0}p{margin:10px 0}header{border-bottom:2px solid #264d38;padding-bottom:15px;letter-spacing:2px;font-size:11px}@media print{body{background:white;margin:0;padding:0;max-width:none}h2,h3{break-after:avoid}pre{break-inside:avoid}a{color:inherit}header{display:none}}'
(root/'static/report.css').write_text(style)
(root/'static/report.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lumnus Outreach — Project Report</title><link rel="stylesheet" href="report.css"></head><body><header>LUMNUS CONSULTING · TECH TEAM FINAL PROJECT</header>'+''.join(parts)+'</body></html>')

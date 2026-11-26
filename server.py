#!/usr/bin/env python3
"""Lumnus Outreach: a loopback-only, dependency-free prototype."""
import argparse, csv, io, json, os, re, secrets, sqlite3, threading, webbrowser
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from seed import DEMOS, ALIASES, opportunities
from services import SERVICES, CATEGORIES, SOURCE, CHECKED, capability_sentence
from research import live_research, validate_opportunities, ResearchError

ROOT=Path(__file__).resolve().parent
DB=Path(os.getenv('LUMNUS_DATA_DIR',str(ROOT/'data')))/'outreach.sqlite3'
TOKEN=secrets.token_urlsafe(32)
STATES=['Draft','Approved','Sent','Replied','Meeting','Closed']
RESEARCH_LOCK=threading.Lock()
CONFIG_LOCK=threading.Lock()

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def norm(s): return re.sub(r'[^a-z0-9]','',s.casefold())
@contextmanager
def connect():
    db=sqlite3.connect(DB,timeout=15)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with db:
            yield db
    finally:
        db.close()

def init_db():
    DB.parent.mkdir(parents=True,exist_ok=True)
    with connect() as db:
        db.executescript('''PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS companies(id INTEGER PRIMARY KEY,name TEXT NOT NULL,key TEXT UNIQUE NOT NULL,owner TEXT NOT NULL DEFAULT '',contact TEXT NOT NULL DEFAULT '',warm TEXT NOT NULL DEFAULT '',notes TEXT NOT NULL DEFAULT '',mode TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS opportunities(id INTEGER PRIMARY KEY,company_id INTEGER NOT NULL REFERENCES companies(id),team_key TEXT NOT NULL,payload TEXT NOT NULL,subject TEXT NOT NULL,body TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Draft',reviewer TEXT NOT NULL DEFAULT '',reviewed TEXT NOT NULL DEFAULT '',recipient TEXT NOT NULL DEFAULT '',followup TEXT NOT NULL DEFAULT '',notes TEXT NOT NULL DEFAULT '',version INTEGER NOT NULL DEFAULT 1,UNIQUE(company_id,team_key));
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,opportunity_id INTEGER,company_id INTEGER,action TEXT NOT NULL,created TEXT NOT NULL);
''')
        columns={r[1] for r in db.execute('PRAGMA table_info(companies)')}
        for column,definition in [('archived','INTEGER NOT NULL DEFAULT 0'),('version','INTEGER NOT NULL DEFAULT 1'),('research_meta',"TEXT NOT NULL DEFAULT '{}'")]:
            if column not in columns: db.execute(f'ALTER TABLE companies ADD COLUMN {column} {definition}')
        db.execute("CREATE TABLE IF NOT EXISTS research_jobs(id TEXT PRIMARY KEY,name TEXT NOT NULL,status TEXT NOT NULL,error TEXT NOT NULL DEFAULT '',company_id INTEGER,created TEXT NOT NULL,finished TEXT NOT NULL DEFAULT '')")

def audit(db,cid,oid,action): db.execute('INSERT INTO events(opportunity_id,company_id,action,created) VALUES(?,?,?,?)',(oid,cid,action,now()))
def score(o): return round(sum(a*b for a,b in zip(o['scores'],[30,30,25,15]))/5)
def draft(name,o,warm=''):
    if o.get('service_ids'):
        intro='I’m with Lumnus Consulting, a student-run consulting organization at UC San Diego.'
        body=f"Hello {o['team']} team,\n\n{intro}\n\n{o['pitch_hook']}\n\n{o['pitch_offer']} {o['pitch_value']}\n\n{capability_sentence(o['service_ids'])} We would confirm scope, staffing and existing work with you before committing.\n\nWould a 15-minute introductory call be useful to assess the fit, or is there someone else on your team we should speak with?\n\nBest,\nLumnus Consulting\nhttps://lumnusconsulting.net/"
        return o['subject'],body
    return 'A focused pilot for '+o['team']+' at '+name, f"Hello {o['team']} team,\n\nI’m with Lumnus Consulting at UC San Diego. {o['evidence'][0]['fact']}\n\n{o['scope']}\n\nWould you be open to a 15-minute introductory call to explore whether this fits your priorities?\n\nBest,\nLumnus Consulting"

def add_company(data,items):
    name=clean(data,'name',120,True)
    with connect() as db:
        try:
            cid=db.execute('INSERT INTO companies(name,key,owner,contact,warm,notes,mode,created) VALUES(?,?,?,?,?,?,?,?)',(name,norm(name),clean(data,'owner',120),clean(data,'contact',300),clean(data,'warm',1000),clean(data,'notes',4000),data['mode'],now())).lastrowid
        except sqlite3.IntegrityError: raise ValueError('This company already exists. Open its record to avoid duplicate outreach.') from None
        db.execute('UPDATE companies SET research_meta=? WHERE id=?',(json.dumps(data.get('research_meta',{})),cid))
        for o in items:
            subject,body=draft(name,o,data.get('warm',''))
            db.execute('INSERT INTO opportunities(company_id,team_key,payload,subject,body) VALUES(?,?,?,?,?)',(cid,norm(o['team']),json.dumps(o),subject,body))
        audit(db,cid,None,'Company added: '+data['mode']+' research')
    return cid

def clean(data,k,limit=4000,required=False):
    value=data.get(k,'')
    if not isinstance(value,str) or len(value)>limit: raise ValueError(f'{k} must be text of at most {limit} characters.')
    value=value.strip()
    if required and not value: raise ValueError(f'{k} is required.')
    return value

def snapshot():
    with connect() as db:
        companies=[dict(r) for r in db.execute('SELECT * FROM companies ORDER BY id')]
        for c in companies:
            c['research_meta']=json.loads(c['research_meta'])
            c['opportunities']=[]
            for r in db.execute('SELECT * FROM opportunities WHERE company_id=?',(c['id'],)):
                stored=dict(r); payload=json.loads(stored.pop('payload')); o={**payload,**stored}; o['score']=score(o)
                o['source_age_days']=max((datetime.now(timezone.utc).date()-datetime.strptime(e['accessed'],'%Y-%m-%d').date()).days for e in o['evidence'])
                c['opportunities'].append(o)
            c['opportunities'].sort(key=lambda o:-o['score'])
        return dict(companies=companies,events=[dict(r) for r in db.execute('SELECT * FROM events ORDER BY id DESC LIMIT 300')],live_configured=bool(os.getenv('OPENAI_API_KEY')),schema_version=2,services=SERVICES,service_categories=CATEGORIES,services_checked=CHECKED,demo_companies=DEMOS,jobs=[dict(r) for r in db.execute('SELECT * FROM research_jobs ORDER BY created DESC LIMIT 10')])

def update_opportunity(oid,data):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT * FROM opportunities WHERE id=?',(oid,)).fetchone()
        if row is None: raise ValueError('Opportunity not found.')
        r=dict(row)
        if data.get('version')!=r['version']: raise ValueError('This draft changed in another window. Refresh before saving.')
        subject=clean(data,'subject',300,True); body=clean(data,'body',15000,True)
        recipient=clean(data,'recipient',254)
        if recipient and not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+',recipient): raise ValueError('Enter a valid recipient email or leave it blank.')
        followup=clean(data,'followup',10)
        if followup:
            try: datetime.strptime(followup,'%Y-%m-%d')
            except ValueError: raise ValueError('Follow-up date must use YYYY-MM-DD.') from None
        status=data.get('status',r['status'])
        if status not in STATES: raise ValueError('Unknown outreach status.')
        changed=(subject!=r['subject'] or body!=r['body'] or recipient!=r['recipient'])
        reviewer=r['reviewer']; reviewed=r['reviewed']
        if changed:
            if r['status'] in ['Sent','Replied','Meeting','Closed']: raise ValueError('Sent outreach is a historical record. Edit notes or follow-up only.')
            status='Draft'; reviewer=''; reviewed=''
        if status=='Approved' and (r['status']=='Draft' or changed):
            reviewer=clean(data,'reviewer',120,True)
            if data.get('checks')!=[True,True,True]: raise ValueError('Confirm all three review checks before approval.')
            if not recipient: raise ValueError('Add a verified recipient email before approving.')
            reviewed=now()
        allowed={'Draft':{'Draft','Approved'},'Approved':{'Approved','Draft','Sent'},'Sent':{'Sent','Replied','Closed'},'Replied':{'Replied','Meeting','Closed'},'Meeting':{'Meeting','Closed'},'Closed':{'Closed'}}
        if not changed and status not in allowed[r['status']]: raise ValueError('Review and approve the draft before tracking the next stage.')
        if status=='Sent' and r['status']!='Sent':
            if data.get('confirm_sent') is not True: raise ValueError('Confirm that you sent this email manually.')
            if db.execute("SELECT id FROM opportunities WHERE id!=? AND lower(recipient)=lower(?) AND status IN ('Sent','Replied','Meeting','Closed')",(oid,recipient)).fetchone(): raise ValueError('This recipient already has recorded outreach. Coordinate with the company owner before proceeding.')
        notes=clean(data,'notes',6000)
        db.execute('UPDATE opportunities SET subject=?,body=?,recipient=?,followup=?,notes=?,status=?,reviewer=?,reviewed=?,version=version+1 WHERE id=?',(subject,body,recipient,followup,notes,status,reviewer,reviewed,oid))
        audit(db,r['company_id'],oid,'Saved draft; approval cleared' if changed else 'Updated outreach: '+status)

def seed_demo():
    for name in DEMOS:
        with connect() as db:
            if db.execute('SELECT id FROM companies WHERE key=?',(norm(name),)).fetchone(): continue
        add_company(dict(name=name,mode='curated',owner='Demo consultant',warm='ILLUSTRATIVE ONLY: a UCSD alumnus could offer an introduction to the Academy team. No real person or permission is verified.' if name=='HubSpot' else ''),opportunities(name))

def validate_intake(data):
    for k,limit in [('name',120),('location',200),('owner',120),('contact',300),('warm',1000)]: clean(data,k,limit,k=='name')
    if not norm(data['name']): raise ValueError('Enter a company name with letters or numbers.')
    with connect() as db:
        if db.execute('SELECT id FROM companies WHERE key=?',(norm(data['name']),)).fetchone(): raise ValueError('Company already exists, possibly in Archived. Open its existing record to avoid duplicate outreach.')

def run_job(jobid,data):
    try:
        items,meta=live_research(data['name'],data.get('location',''),with_metadata=True)
        data['research_meta']=meta
        data['notes']='Location hint: '+data['location'] if data.get('location') else ''
        cid=add_company(data,items)
        with connect() as db: db.execute("UPDATE research_jobs SET status='complete',company_id=?,finished=? WHERE id=?",(cid,now(),jobid))
    except Exception as e:
        message=str(e) if isinstance(e,ValueError) else 'Research failed unexpectedly. No automatic retry was made.'
        with connect() as db: db.execute("UPDATE research_jobs SET status='failed',error=?,finished=? WHERE id=?",(message+' Provider usage may be billed even when no company is saved.',now(),jobid))
    finally: RESEARCH_LOCK.release()

def start_job(data):
    validate_intake(data)
    if data.get('accept_charges') is not True: raise ValueError('Acknowledge API charges before starting live research.')
    if not os.getenv('OPENAI_API_KEY'): raise ValueError('Live research is not configured. Add an API key in Settings, or use prepared research.')
    if not RESEARCH_LOCK.acquire(False): raise ValueError('Another live research run is in progress. Wait for it to finish.')
    jobid=secrets.token_hex(12)
    try:
        with connect() as db: db.execute('INSERT INTO research_jobs(id,name,status,created) VALUES(?,?,?,?)',(jobid,data['name'],'running',now()))
        threading.Thread(target=run_job,args=(jobid,{**data,'mode':'live'}),daemon=True).start()
    except Exception:
        RESEARCH_LOCK.release();raise
    return jobid

def save_configuration(data):
    key=clean(data,'api_key',500,True)
    if not key.startswith('sk-') or any(c.isspace() for c in key): raise ValueError('Enter an OpenAI API key without spaces. It is saved only on this computer.')
    with CONFIG_LOCK:
        target=ROOT/'.env'; temp=ROOT/'.env.tmp'
        fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        try:
            with os.fdopen(fd,'w') as f: f.write('OPENAI_API_KEY='+key+'\nOPENAI_MODEL=gpt-6.2-sol\n')
            os.chmod(temp,0o600);os.replace(temp,target)
        finally:
            if temp.exists():temp.unlink()
        os.environ['OPENAI_API_KEY']=key
        os.environ['OPENAI_MODEL']='gpt-6.2-sol'


class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args): pass
    def respond(self,obj,status=200,kind='application/json'):
        body=json.dumps(obj).encode() if kind=='application/json' else obj.encode() if isinstance(obj,str) else obj
        self.send_response(status)
        self.send_header('Content-Type',kind+'; charset=utf-8'); self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers(); self.wfile.write(body)
    def host_ok(self): return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
    def do_GET(self):
        if not self.host_ok(): return self.respond({'error':'Local access only.'},403)
        path=urlparse(self.path).path
        if path=='/api/state': return self.respond({**snapshot(),'token':TOKEN})
        if path=='/api/brief-template':
            return self.send_export(json.dumps({'name':'Patagonia','opportunities':opportunities('Patagonia')},indent=2),'prepared-research-example.json','application/json')
        if path=='/api/export':
            self.send_export(json.dumps(snapshot(),indent=2),'lumnus-backup.json','application/json'); return
        if path=='/api/csv':
            stream=io.StringIO(); w=csv.writer(stream); w.writerow(['Company','Team','Project','Score','Owner','Status','Recipient','Follow-up'])
            for c in snapshot()['companies']:
                for o in c['opportunities']:
                    vals=[c['name'],o['team'],o['title'],o['score'],c['owner'],o['status'],o['recipient'],o['followup']]
                    w.writerow(["'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v for v in vals])
            return self.send_export(stream.getvalue(),'lumnus-pipeline.csv','text/csv')
        files={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/report':'report.html','/report.css':'report.css'}
        if path not in files: return self.respond({'error':'Not found'},404)
        file=ROOT/'static'/files[path]
        if not file.exists(): return self.respond({'error':'Not found'},404)
        return self.respond(file.read_bytes(),kind={'html':'text/html','js':'text/javascript','css':'text/css'}[file.suffix[1:]])
    def send_export(self,body,name,kind):
        b=body.encode(); self.send_response(200); self.send_header('Content-Type',kind); self.send_header('Content-Disposition','attachment; filename="'+name+'"'); self.send_header('Content-Length',str(len(b))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        if not self.host_ok() or self.headers.get('X-Lumnus-Token')!=TOKEN: return self.respond({'error':'Refresh the app to reconnect securely.'},403)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=1000000: raise ValueError('Request size is invalid.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError('Expected an object.')
            path=urlparse(self.path).path
            if path=='/api/config':
                save_configuration(data);return self.respond({'ok':True})
            if path=='/api/companies':
                validate_intake(data)
                if data.get('mode')=='live': return self.respond({'job_id':start_job(data)},202)
                if data.get('mode')=='curated':
                    match=ALIASES.get(norm(data['name']))
                    if not match: raise ValueError('Prepared research is available for HubSpot, Patagonia and Oura. Use live research for a new company, or import a prepared brief.')
                    data['name']=match;items=opportunities(match)
                elif data.get('mode')=='imported':
                    brief=data.get('brief')
                    if not isinstance(brief,dict) or not isinstance(brief.get('name'),str) or norm(brief['name'])!=norm(data['name']): raise ValueError('The prepared brief must match the company name.')
                    items=validate_opportunities(brief.get('opportunities'))
                else: raise ValueError('Choose prepared, live or imported research.')
                data['notes']=('Location hint: '+clean(data,'location',200)) if data.get('location') else ''
                cid=add_company(data,validate_opportunities(items));return self.respond({'id':cid})
            elif path=='/api/demo': seed_demo()
            elif re.fullmatch(r'/api/opportunities/\d+',path): update_opportunity(int(path.rsplit('/',1)[1]),data)
            elif re.fullmatch(r'/api/companies/\d+',path):
                cid=int(path.rsplit('/',1)[1])
                with connect() as db:
                    db.execute('BEGIN IMMEDIATE')
                    row=db.execute('SELECT * FROM companies WHERE id=?',(cid,)).fetchone()
                    if not row: raise ValueError('Company not found.')
                    if data.get('version')!=row['version']: raise ValueError('Company details changed in another window. Refresh before saving.')
                    if 'archived' in data:
                        if type(data['archived'])!=bool:raise ValueError('Invalid archive choice.')
                        db.execute('UPDATE companies SET archived=?,version=version+1 WHERE id=?',(int(data['archived']),cid))
                        audit(db,cid,None,'Company archived' if data['archived'] else 'Company restored')
                    else:
                        db.execute('UPDATE companies SET owner=?,contact=?,warm=?,notes=?,version=version+1 WHERE id=?',(clean(data,'owner',120),clean(data,'contact',300),clean(data,'warm',1000),clean(data,'notes',4000),cid)); audit(db,cid,None,'Updated company coordination notes')
            else: return self.respond({'error':'Not found'},404)
            self.respond({'ok':True})
        except (ValueError,KeyError,TypeError) as e: self.respond({'error':str(e)},400)
        except Exception:
            self.respond({'error':'An unexpected error occurred. Saved records are unchanged; see the terminal for details.'},500)
            import traceback; traceback.print_exc()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); parser.add_argument('--no-browser',action='store_true'); args=parser.parse_args()
    # Optional local configuration, deliberately excluded from sharing.
    config=ROOT/'.env'
    if config.exists():
        for line in config.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                k,v=line.split('=',1)
                if k.strip() in ('OPENAI_API_KEY','OPENAI_MODEL'): os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
    init_db()
    with connect() as db: db.execute("UPDATE research_jobs SET status='failed',error='Server restarted before completion. Check provider usage before retrying; there was no automatic retry.',finished=? WHERE status='running'",(now(),))
    try: server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except OSError as e:
        print(f'Could not start local server: {e}. If the port is in use, reopen the running app or use --port 8766.'); return
    print(f'Lumnus Outreach is ready: http://127.0.0.1:{args.port}\nKeep this window open. Press Ctrl+C to stop.\nData: {DB}',flush=True)
    if not args.no_browser: threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__=='__main__': main()

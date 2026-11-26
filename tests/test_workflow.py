import json, os, sys, tempfile, threading, unittest, urllib.request, urllib.error
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server, research

class WorkflowTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); server.DB=Path(self.tmp.name)/'test.sqlite3'; server.init_db(); server.seed_demo()
 def tearDown(self): self.tmp.cleanup()
 def first(self): return server.snapshot()['companies'][0]['opportunities'][0]
 def payload(self,o,**changes):
  data={k:o[k] for k in ['version','subject','body','recipient','followup','notes','status']}; data.update(changes); return data
 def approved(self):
  o=self.first(); server.update_opportunity(o['id'],self.payload(o,recipient='review@example.com')); o=self.first()
  server.update_opportunity(o['id'],self.payload(o,status='Approved',reviewer='Reviewer',checks=[True]*3)); return self.first()
 def test_demo_has_nine_distinct_sourced_projects(self):
  s=server.snapshot(); self.assertEqual(len(s['companies']),3)
  for c in s['companies']:
   self.assertEqual(len(c['opportunities']),3); research.validate_opportunities(c['opportunities']); self.assertEqual(len(set(o['title'] for o in c['opportunities'])),3)
  self.assertIn('ILLUSTRATIVE',s['companies'][0]['warm'])
 def test_idempotence_and_duplicate_company(self):
  server.seed_demo(); self.assertEqual(len(server.snapshot()['companies']),3)
  with self.assertRaisesRegex(ValueError,'already exists'): server.add_company({'name':' HUBSPOT! ','mode':'curated'},[])
 def test_no_review_bypass(self):
  o=self.first()
  for stage in ['Sent','Replied','Meeting','Closed']:
   with self.assertRaises(ValueError): server.update_opportunity(o['id'],self.payload(o,status=stage))
  with self.assertRaises(ValueError): server.update_opportunity(o['id'],self.payload(o,status='Approved',reviewer='Reviewer',checks=[True]*3))
 def test_all_checks_required(self):
  o=self.first(); server.update_opportunity(o['id'],self.payload(o,recipient='review@example.com')); o=self.first()
  with self.assertRaisesRegex(ValueError,'three review'): server.update_opportunity(o['id'],self.payload(o,status='Approved',reviewer='R',checks=[True,False,True]))
 def test_edit_clears_approval(self):
  o=self.approved(); server.update_opportunity(o['id'],self.payload(o,body=o['body']+'\nEdited.')); new=self.first(); self.assertEqual(new['status'],'Draft'); self.assertEqual(new['reviewed'],'')
 def test_stale_tab_blocked(self):
  o=self.first(); server.update_opportunity(o['id'],self.payload(o,notes='First change'))
  with self.assertRaisesRegex(ValueError,'another window'): server.update_opportunity(o['id'],self.payload(o,notes='Stale change'))
  self.assertEqual(self.first()['notes'],'First change')
 def test_manual_send_history_lock(self):
  o=self.approved()
  with self.assertRaisesRegex(ValueError,'manually'): server.update_opportunity(o['id'],self.payload(o,status='Sent'))
  server.update_opportunity(o['id'],self.payload(o,status='Sent',confirm_sent=True)); o=self.first()
  with self.assertRaisesRegex(ValueError,'historical'): server.update_opportunity(o['id'],self.payload(o,subject='Changed'))
  server.update_opportunity(o['id'],self.payload(o,status='Replied',notes='Interested')); self.assertEqual(self.first()['status'],'Replied')
 def test_duplicate_recipient_blocked(self):
  o=self.approved(); server.update_opportunity(o['id'],self.payload(o,status='Sent',confirm_sent=True)); other=server.snapshot()['companies'][0]['opportunities'][1]
  server.update_opportunity(other['id'],self.payload(other,recipient='REVIEW@example.com')); other=server.snapshot()['companies'][0]['opportunities'][1]
  server.update_opportunity(other['id'],self.payload(other,status='Approved',reviewer='R',checks=[True]*3)); other=server.snapshot()['companies'][0]['opportunities'][1]
  with self.assertRaisesRegex(ValueError,'already has recorded'): server.update_opportunity(other['id'],self.payload(other,status='Sent',confirm_sent=True))
 def test_validation_missing_key(self):
  o=self.first()
  for change in [dict(followup='2026-99-99'),dict(recipient='bad email'),dict(body=''),dict(subject='x'*301)]:
   with self.assertRaises(ValueError): server.update_opportunity(o['id'],self.payload(o,**change))
  with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
   with self.assertRaisesRegex(ValueError,'not configured'): research.live_research('New Company')
 def test_persistence(self):
  o=self.first(); server.update_opportunity(o['id'],self.payload(o,notes='Persisted')); server.init_db(); self.assertEqual(self.first()['notes'],'Persisted')
 def test_provider_validation(self):
  items=server.opportunities('HubSpot'); items[0]['evidence'][0]['url']='javascript:alert(1)'
  with self.assertRaises(ValueError): research.validate_opportunities(items)
  items=server.opportunities('HubSpot'); items[1]['team']=items[0]['team']
  with self.assertRaises(ValueError): research.validate_opportunities(items)
 def test_live_adapter_and_provenance(self):
  items=server.opportunities('HubSpot'); response={'status':'completed','output':[{'type':'web_search_call','action':{'sources':[{'url':o['evidence'][0]['url']} for o in items]}},{'type':'message','content':[{'type':'output_text','text':json.dumps({'opportunities':items})}]}]}
  def mocked(*args,**kwargs):
   import io
   return io.BytesIO(json.dumps(response).encode())
  with patch.dict(os.environ,{'OPENAI_API_KEY':'test'}),patch('urllib.request.urlopen',side_effect=mocked):
   self.assertEqual(len(research.live_research('HubSpot')),3); response['output'][0]['action']['sources']=[]
   with self.assertRaisesRegex(ValueError,'absent'): research.live_research('HubSpot')
 def test_concurrent_edit_only_one_wins(self):
  from concurrent.futures import ThreadPoolExecutor
  o=self.first(); gate=threading.Barrier(2)
  def edit(note):
   gate.wait()
   try: server.update_opportunity(o['id'],self.payload(o,notes=note)); return 'saved'
   except ValueError: return 'stale'
  with ThreadPoolExecutor(max_workers=2) as pool:
   results=list(pool.map(edit,['One','Two']))
  self.assertEqual(sorted(results),['saved','stale'])
 def test_intake_exposes_both_research_modes(self):
  from html.parser import HTMLParser
  class Options(HTMLParser):
   values=[]
   def handle_starttag(self,tag,attrs):
    if tag=='option': self.values.append(dict(attrs).get('value'))
  parser=Options(); parser.feed((server.ROOT/'static/index.html').read_text())
  self.assertIn('curated',parser.values); self.assertIn('live',parser.values)
 def test_http_security_and_exports(self):
  http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler); t=threading.Thread(target=http.serve_forever,daemon=True); t.start(); base=f'http://127.0.0.1:{http.server_port}'
  try:
   with urllib.request.urlopen(base+'/api/state') as r: self.assertEqual(len(json.load(r)['companies']),3)
   for path in ['/','/app.js','/style.css','/api/csv','/api/export','/report','/report.css']:
    with urllib.request.urlopen(base+path) as r: self.assertEqual(r.status,200)
   req=urllib.request.Request(base+'/api/demo',data=b'{}',headers={'Content-Type':'application/json'})
   with self.assertRaises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
   self.assertEqual(e.exception.code,403);req.add_header('X-Lumnus-Token',server.TOKEN)
   with urllib.request.urlopen(req) as r: self.assertTrue(json.load(r)['ok'])
   req=urllib.request.Request(base+'/api/state',headers={'Host':'evil.example'})
   with self.assertRaises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
   self.assertEqual(e.exception.code,403)
  finally: http.shutdown();http.server_close();t.join()
 def test_import_cannot_override_workflow_fields(self):
  items=server.opportunities('HubSpot'); items[0].update(id=999,status='Approved',body='Injected',version=99,recipient='attacker@example.com')
  clean=research.validate_opportunities(items)
  self.assertNotIn('status',clean[0]);self.assertNotIn('id',clean[0])
  cid=server.add_company({'name':'Test imported company','mode':'imported'},clean)
  saved=next(c for c in server.snapshot()['companies'] if c['id']==cid)['opportunities'][0]
  self.assertEqual(saved['status'],'Draft');self.assertEqual(saved['recipient'],'');self.assertNotEqual(saved['body'],'Injected')
 def test_service_fit_and_concrete_deliverables_required(self):
  for field,value in [('service_ids',['invented']),('deliverables',[]),('discovery_questions',[]),('scores',[True,5,5,1]),('subject','x'*101)]:
   items=server.opportunities('HubSpot');items[0][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):research.validate_opportunities(items)
 def test_future_sources_and_normalized_duplicate_teams_rejected(self):
  items=server.opportunities('HubSpot');items[0]['evidence'][0]['accessed']='2999-01-01'
  with self.assertRaises(ValueError):research.validate_opportunities(items)
  items=server.opportunities('HubSpot');items[1]['team']=items[0]['team']+'_'
  with self.assertRaises(ValueError):research.validate_opportunities(items)
 def test_live_requires_charge_ack_and_key(self):
  with patch.dict(os.environ,{'OPENAI_API_KEY':'sk-test'}):
   with self.assertRaisesRegex(ValueError,'Acknowledge'):server.start_job({'name':'New company'})
  with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
   with self.assertRaisesRegex(ValueError,'not configured'):server.start_job({'name':'New company','accept_charges':True})
 def test_job_success_failure_and_busy_guard(self):
  entered=threading.Event();release=threading.Event()
  def mocked(*args,**kwargs):
   entered.set();release.wait(5);return server.opportunities('HubSpot'),{'model':'mock'}
  with patch.dict(os.environ,{'OPENAI_API_KEY':'sk-test'}),patch.object(server,'live_research',side_effect=mocked):
   job=server.start_job({'name':'New target','accept_charges':True});self.assertTrue(entered.wait(2))
   try:
    with self.assertRaisesRegex(ValueError,'in progress'):server.start_job({'name':'Other target','accept_charges':True})
   finally:release.set()
   self.assertTrue(server.RESEARCH_LOCK.acquire(timeout=5));server.RESEARCH_LOCK.release()
   result=next(j for j in server.snapshot()['jobs'] if j['id']==job);self.assertEqual(result['status'],'complete')
  with patch.dict(os.environ,{'OPENAI_API_KEY':'sk-test'}),patch.object(server,'live_research',side_effect=research.ResearchError('Simulated provider failure')):
   job=server.start_job({'name':'Failure target','accept_charges':True})
   self.assertTrue(server.RESEARCH_LOCK.acquire(timeout=5));server.RESEARCH_LOCK.release()
   result=next(j for j in server.snapshot()['jobs'] if j['id']==job)
   self.assertEqual(result['status'],'failed');self.assertIn('billed',result['error'])
   self.assertFalse(any(c['name']=='Failure target' for c in server.snapshot()['companies']))
 def test_key_save_is_local_and_not_exported(self):
  with patch.object(server,'ROOT',Path(self.tmp.name)),patch.dict(os.environ,{},clear=False),patch('urllib.request.urlopen') as remote:
   server.save_configuration({'api_key':'sk-test-not-real'})
   self.assertEqual((Path(self.tmp.name)/'.env').stat().st_mode&0o777,0o600)
   self.assertNotIn('sk-test-not-real',json.dumps(server.snapshot()));remote.assert_not_called()
 def test_import_and_company_version_routes(self):
  http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);t=threading.Thread(target=http.serve_forever,daemon=True);t.start();base=f'http://127.0.0.1:{http.server_port}'
  def post(path,data):
   req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Lumnus-Token':server.TOKEN})
   with urllib.request.urlopen(req) as r:return json.load(r)
  try:
   with patch.object(server,'live_research') as paid:
    result=post('/api/companies',{'name':'Imported Target','mode':'imported','brief':{'name':'Imported Target','opportunities':server.opportunities('Patagonia')}});paid.assert_not_called()
   cid=result['id'];post('/api/companies/'+str(cid),{'version':1,'archived':True})
   with self.assertRaises(urllib.error.HTTPError) as error:post('/api/companies/'+str(cid),{'version':1,'archived':False})
   self.assertEqual(error.exception.code,400)
   c=next(c for c in server.snapshot()['companies'] if c['id']==cid);self.assertEqual(c['archived'],1)
   with self.assertRaises(ValueError):server.validate_intake({'name':'Imported Target'})
   post('/api/companies/'+str(cid),{'version':2,'archived':False})
   for path in ['/.env','/data/outreach.sqlite3','/../server.py']:
    with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(base+path)
  finally:http.shutdown();http.server_close();t.join()
if __name__=='__main__': unittest.main()

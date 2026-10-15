"""Local teaching app. Never use fake credentials/settings as production defaults."""
import json, os, sqlite3, time, uuid, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
HOST=os.getenv('BIND_HOST','0.0.0.0'); PORT=int(os.getenv('PORT','8080'))
STATELESS=os.getenv('STATELESS','0')=='1'; DB=os.getenv('DB_PATH','/data/notes.db')
COUNTERS={'2xx':0,'5xx':0,'4xx':0}; LATENCY=[0.0,0]; LOCK=threading.Lock()
if not STATELESS:
 Path(DB).parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect(DB) as db:db.execute('CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, body TEXT NOT NULL)')
def emit(level,message,rid):
 record={'timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'level':level,'message':message,'request_id':rid}
 line=json.dumps(record)
 print(line,flush=True)
 if os.getenv('LOG_FILE'):
  try:
   with open(os.environ['LOG_FILE'],'a') as f:f.write(line+'\n')
  except OSError as error:print(json.dumps({'level':'ERROR','message':'log-write-failed','error':str(error)}),flush=True)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def respond(self,status,obj):
  rid=self.headers.get('X-Request-ID') or str(uuid.uuid4());data=json.dumps(obj).encode()
  self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.send_header('X-Request-ID',rid);self.end_headers();self.wfile.write(data)
  if self.path!='/metrics':
   with LOCK:
    COUNTERS[f'{status//100}xx']=COUNTERS.get(f'{status//100}xx',0)+1;LATENCY[0]+=time.monotonic()-self.started;LATENCY[1]+=1
   emit('ERROR' if status>=500 else 'INFO','request-failed' if status>=500 else 'request-complete',rid)
 def do_GET(self):
  self.started=time.monotonic()
  if self.path=='/metrics':
   with LOCK:
    lines=['# TYPE cloudnotes_requests_total counter']+[f'cloudnotes_requests_total{{status_class="{k}"}} {v}' for k,v in COUNTERS.items()]
    lines += ['# TYPE cloudnotes_request_duration_seconds summary',f'cloudnotes_request_duration_seconds_sum {LATENCY[0]}',f'cloudnotes_request_duration_seconds_count {LATENCY[1]}']
   data=('\n'.join(lines)+'\n').encode();self.send_response(200);self.send_header('Content-Type','text/plain; version=0.0.4');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  if self.path=='/health':return self.respond(200,{'status':'ok'})
  if self.path=='/ready':return self.respond(503 if Path('/tmp/not-ready').exists() else 200,{'ready':not Path('/tmp/not-ready').exists()})
  if self.path=='/info':return self.respond(200,{'mode':os.getenv('APP_MODE','development'),'instance':os.getenv('HOSTNAME','local'),'stateless':STATELESS})
  if self.path=='/fail':return self.respond(500,{'error':'controlled-test-failure'})
  if self.path=='/notes':
   if STATELESS:return self.respond(200,{'notes':[{'id':1,'body':'read-only drill fixture'}]})
   with sqlite3.connect(DB) as db:rows=db.execute('SELECT id,body FROM notes ORDER BY id').fetchall()
   return self.respond(200,{'notes':[{'id':r[0],'body':r[1]} for r in rows]})
  return self.respond(404,{'error':'not found'})
 def do_POST(self):
  self.started=time.monotonic()
  if self.path!='/notes':return self.respond(404,{'error':'not found'})
  if STATELESS:return self.respond(405,{'error':'read-only drill'})
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=4096:raise ValueError('body length')
   body=json.loads(self.rfile.read(length));note=body.get('body')
   if not isinstance(note,str) or not note.strip():raise ValueError('body required')
   with sqlite3.connect(DB) as db:
    cur=db.execute('INSERT INTO notes(body) VALUES(?)',(note,));nid=cur.lastrowid
   return self.respond(201,{'id':nid})
  except (ValueError,TypeError,json.JSONDecodeError):return self.respond(400,{'error':'invalid body'})
if __name__=='__main__':
 emit('INFO','server-starting','startup');ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()

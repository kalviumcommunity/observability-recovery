import subprocess,time,json,urllib.request
from pathlib import Path
ns='observability-recovery';out=Path('evidence');out.mkdir(exist_ok=True)
pods=json.loads(subprocess.check_output(['kubectl','-n',ns,'get','pods','-l','app=cloudnotes','-o','json'],text=True))['items']
if len(pods)!=2:raise SystemExit('Start with exactly two application Pods')
victim=pods[0]['metadata']['name']
observer=pods[1]['metadata']['name']
subprocess.run(['kubectl','-n',ns,'delete','pod',victim,'--wait=false'],check=True)
start=time.monotonic();samples=[];elapsed=None
while time.monotonic()-start<90:
 data=json.loads(subprocess.check_output(['kubectl','-n',ns,'get','deployment','cloudnotes','-o','json'],text=True))
 ready=data.get('status',{}).get('readyReplicas',0)
 try:
  probe=subprocess.run(['kubectl','-n',ns,'exec',observer,'--','python3','-c',"import urllib.request; r=urllib.request.urlopen('http://cloudnotes:8080/health',timeout=2); print(r.status)"],text=True,capture_output=True,timeout=6)
  status=int(probe.stdout.strip()) if probe.returncode==0 else 'probe-unavailable'
 except Exception:status='unavailable'
 samples.append({'timestamp':time.time(),'elapsed_seconds':time.monotonic()-start,'ready_replicas':ready,'http_status':status})
 current=json.loads(subprocess.check_output(['kubectl','-n',ns,'get','pods','-l','app=cloudnotes','-o','json'],text=True))['items']
 if ready==2 and len(current)==2 and victim not in [p['metadata']['name'] for p in current] and all(any(c['type']=='Ready' and c['status']=='True' for c in p.get('status',{}).get('conditions',[])) for p in current):elapsed=time.monotonic()-start;break
 time.sleep(.5)
template=json.loads(Path('reports/drill-template.json').read_text());template['observations']=samples;template['elapsed']=elapsed
(out/'recovery.json').write_text(json.dumps(template,indent=2));print(json.dumps(template,indent=2))
if elapsed is None:raise SystemExit('No desired-replica recovery within 90 seconds')

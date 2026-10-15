"""Student-visible checks. Intended outcomes are documented, not secret answers."""
import argparse, json, ipaddress, os, subprocess, sys, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())
def need(condition,message):
 if not condition:raise AssertionError(message)
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
def http(path,code=200):
 base=os.getenv('BASE_URL','http://127.0.0.1:'+str(read('contract.json')['host_port']))
 try:
  with urllib.request.urlopen(base+path,timeout=5) as r:status=r.status;body=r.read().decode()
 except urllib.error.HTTPError as e:status=e.code;body=e.read().decode()
 need(status==code,f'{path}: expected {code}, got {status}');return body
def network():
 d=read('architecture/network.json');nets=[ipaddress.ip_network(d[t],strict=True) for t in ['web','app','data']]
 for n in nets:need(n.is_private and n.version==4 and n.num_addresses>=128,'Private IPv4 subnet needs >=128 addresses')
 for i,n in enumerate(nets):
  for other in nets[i+1:]:need(not n.overlaps(other),'Overlapping tier CIDRs')
 print('PASS: disjoint private tier ranges; this does not enforce traffic isolation')
def access():
 d=read('architecture/access.json' if (ROOT/'architecture/access.json').exists() else 'architecture/iam.json')
 need(d['application_identity']=='app-runtime@example.invalid','Keep dedicated fake application identity')
 bindings={(x['role'],x['resource']) for x in d['bindings']}
 need(bindings=={('roles/cloudsql.client','projects/demo-project'),('roles/secretmanager.secretAccessor','projects/demo-project/secrets/db-demo')},'Use only the documented SQL connection and secret-read contracts')
 need(d['administrator_identity']!=d['application_identity'],'Separate administrator identity')
 print('PASS: scoped IAM design, not a live GCP enforcement test')
def terraform():
 for cmd in [['init','-backend=false'],['fmt','-check','-recursive'],['validate'],['plan','-input=false','-out=tfplan']]:
  run('terraform','-chdir=terraform',*cmd)
 print('PASS: local Terraform inventory plan only; no GCP provider validation')
def container():
 cfg=read('contract.json');run('docker','build','-t',cfg['image'],'.')
 d=json.loads(subprocess.check_output(['docker','image','inspect',cfg['image']],text=True))[0]
 need(d['Config']['User']=='10001:10001','Preserve non-root runtime')
 print('PASS: image builds as non-root; use runtime check for service behavior')
def release():
 network();access();d=read('release/env.json');need(d['app_subnet_name']=='app','Release must reference declared app subnet')
 run('terraform','-chdir=terraform','validate')
 print('PASS: release configuration refers to the architecture inventory')
def runtime():
 http('/health');http('/notes');print('PASS: actual health and notes HTTP responses')
def service():
 import xml.etree.ElementTree as unused
 d=read('k8s/service.json');dep=read('k8s/deployment.json')
 labels=dep['spec']['template']['metadata']['labels'];sel=d['spec']['selector']
 need(sel and all(labels.get(k)==v for k,v in sel.items()),'Service selector does not match Pod labels')
 print('PASS: Service selects workload labels; runtime evidence still required')
def config():
 dep=read('k8s/deployment.json');cm=read('k8s/configmap.json')
 for e in dep['spec']['template']['spec']['containers'][0]['env']:
  ref=e.get('valueFrom',{}).get('configMapKeyRef')
  if ref:need(ref['name']==cm['metadata']['name'] and ref['key'] in cm['data'],'Missing ConfigMap key')
 print('PASS: ConfigMap references exist; use /info to verify consumption')
def probe():
 dep=read('k8s/deployment.json');c=dep['spec']['template']['spec']['containers'][0]
 need(c['readinessProbe']['httpGet']['path']=='/ready','Readiness must use supplied readiness endpoint')
 need(c['livenessProbe']['httpGet']['path']=='/health','Preserve health liveness probe')
 print('PASS: readiness and liveness contracts')
def replicas():
 need(read('k8s/deployment.json')['spec']['replicas']==2,'Drill requires two stateless replicas')
 print('PASS: desired replica count; capture actual replacement evidence separately')
def metrics():
 need('port: 8080' in (ROOT/'monitoring/prometheus.yml').read_text() and 'cloudnotes-metrics.observability-recovery.svc.cluster.local' in (ROOT/'monitoring/prometheus.yml').read_text(),'Use per-Pod DNS discovery and the documented metrics port')
 print('PASS: metrics target design; verify actual Prometheus target UP')
def report():
 need(read('reports/drill-template.json')['unit']=='seconds','Report unit must match sampler output')
 print('PASS: report units; replace template observations with actual drill evidence')
def resolve():
 txt=(ROOT/'network/resolve.env').read_text() if (ROOT/'network/resolve.env').exists() else (ROOT/'network/request.env').read_text()
 need('HOSTNAME=notes.test' in txt.splitlines(),'Request hostname and local resolution override differ')
 run('sh','scripts/request.sh');print('PASS: actual hostname request through local override')
def logging():
 d=read('app/log-schema.json');need(d['level_field']=='level','Log schema requires level field')
 out=http('/fail',500)
 print('PASS: level-field contract and controlled failing request; query logs by request id too')
def queries():
 need(read('monitoring/queries.json')['request_counter']=='cloudnotes_requests_total','Query must match emitted request counter')
 body=http('/metrics');need('cloudnotes_requests_total' in body,'Expected actual request metric')
 print('PASS: actual metric name and query contract')
def permissions():
 run('docker','compose','exec','-T','app','python3','-c',"import os; from pathlib import Path; p=Path('/app/logs/permission-check'); p.write_text('ok'); p.unlink(); print('uid',os.getuid(),'write OK')")
def firewall():
 d=read('architecture/firewall.json');rules=d['rules']
 def allowed(source,port,tier):
  return any(x['port']==port and x['target']==tier and ipaddress.ip_address(source) in ipaddress.ip_network(x['source']) for x in rules)
 need(allowed('10.20.1.10',5432,'data'),'Application-to-database path must work')
 need(not allowed('203.0.113.7',5432,'data'),'Internet must not reach database')
 need(allowed('203.0.113.7',443,'web'),'Public HTTPS entry must remain')
 need(all(x['source']=='10.20.1.0/24' for x in rules if x['port']==5432),'Database source contract is application subnet')
 print('PASS: positive and negative design simulation, not live firewall enforcement')
def entrypoint():
 d=read('architecture/entrypoint.json');need(d['public_login_scheme']=='https' and d['public_login_port']==443 and d['http_redirect_to_https'] is True,'Cloud public login entry must use HTTPS/443 and HTTP redirect')
 print('PASS: target cloud TLS design; local HTTP does NOT prove TLS deployment')
FUNCTIONS={k:v for k,v in list(globals().items()) if k in ['network','access','terraform','container','release','runtime','service','config','probe','replicas','metrics','report','resolve','logging','queries','permissions','firewall','entrypoint']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('check',choices=sorted(FUNCTIONS));args=p.parse_args()
 try:FUNCTIONS[args.check]()
 except (AssertionError,Exception) as e:print('FAIL:',str(e),file=sys.stderr);sys.exit(1)

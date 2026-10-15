import sys,time,urllib.request,urllib.error
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:18083'
path=sys.argv[2] if len(sys.argv)>2 else '/health'
duration=min(max(int(sys.argv[3]),1),120) if len(sys.argv)>3 else 75
end=time.monotonic()+duration
while time.monotonic()<end:
 try:
  with urllib.request.urlopen(base+path,timeout=2) as r:print(time.time(),r.status,flush=True)
 except urllib.error.HTTPError as e:print(time.time(),e.code,flush=True)
 except Exception as e:print(time.time(),type(e).__name__,flush=True)
 time.sleep(.15)

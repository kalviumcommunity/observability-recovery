import subprocess,sys
checks=['probe', 'replicas', 'metrics', 'report', 'runtime']
failures=[]
for check in checks:
 result=subprocess.run([sys.executable,'checks/check.py',check])
 if result.returncode:failures.append(check)
print('Failed checks:',failures)
sys.exit(bool(failures))

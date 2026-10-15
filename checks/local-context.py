import subprocess,sys
c=subprocess.check_output(['kubectl','config','current-context'],text=True).strip()
if c!='docker-desktop' and c!='minikube' and not c.startswith('kind-'):
 sys.exit('Refusing non-local Kubernetes context: '+c)
print('Local context:',c)

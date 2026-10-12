from scapy.all import *
import sys
conf.verb=0
ifc=next(i for i in conf.ifaces.values() if getattr(i,'ip','')=='192.168.1.10' or getattr(i,'name','')=='Local')
print('iface',ifc.name,ifc.mac)
def run(vlan):
    for n in range(3):
        e=Ether(src=ifc.mac,dst='ff:ff:ff:ff:ff:ff')
        if vlan is not None: e=e/Dot1Q(vlan=vlan,prio=0)
        p=e/PPPoED(code=0x09,len=4)/PPPoETag(tag_type=0x0101,tag_len=0)
        
        ans=srp1(p,iface=ifc,timeout=5)
        if ans:
            print('vlan',vlan,'PADO' if ans[PPPoED].code==7 else ans[PPPoED].code, ans.src, ans.summary()); return True
        print('vlan',vlan,'try',n+1,'sem resposta')
    return False
for v in (10,None): run(v)

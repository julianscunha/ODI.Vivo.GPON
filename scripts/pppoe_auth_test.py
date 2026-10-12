from scapy.all import *
import struct,hashlib,time,sys,threading
conf.verb=0
ifc=next(i for i in conf.ifaces.values() if getattr(i,'name','')=='Local')
V=1335; USER=sys.argv[1].encode(); PWD=sys.argv[2].encode(); MY=ifc.mac
S=dict(srv=None,sid=0,auth=None,srv_ack=False,our_ack=False,auth_sent=False,result=None,ip=None,cookie=b'')
def tx(dst,et,payload): sendp(Ether(src=MY,dst=dst)/Dot1Q(vlan=V,type=et)/Raw(payload),iface=ifc,verbose=0)
def disc(dst,code,sid,tags=b''): tx(dst,0x8863,struct.pack('!BBHH',0x11,code,sid,len(tags))+tags)
def tag(t,v): return struct.pack('!HH',t,len(v))+v
def sess(proto,code,i,data): 
    ppp=struct.pack('!H',proto)+struct.pack('!BBH',code,i,len(data)+4)+data
    tx(S['srv'],0x8864,struct.pack('!BBHH',0x11,0,S['sid'],len(ppp))+ppp)
def log(*a): print(f'[{time.time()-T0:5.1f}s]',*a,flush=True)
def h(p):
    if not (p.haslayer(Dot1Q) and p[Dot1Q].vlan==V and p.src!=MY): return
    et=p[Dot1Q].type; b=bytes(p[Dot1Q].payload)
    if len(b)<6: return
    vt,code,sid,ln=struct.unpack('!BBHH',b[:6]); pl=b[6:6+ln]
    if et==0x8863:
        if code==0x07 and S['srv'] is None:
            S['srv']=p.src; tags=b''; i=0
            while i+4<=len(pl):
                t,l=struct.unpack('!HH',pl[i+0:i+4]); v=pl[i+4:i+4+l]; i+=4+l
                if t==0x0102: log('PADO AC-Name',v.decode(errors='replace'))
                if t==0x0104: S['cookie']=v
            disc(S['srv'],0x19,0,tag(0x0101,b'')+(tag(0x0104,S['cookie']) if S['cookie'] else b'')); log('PADR enviado')
        elif code==0x65 and S['sid']==0:
            S['sid']=sid; log('PADS sessao',sid); sess(0xc021,1,1,struct.pack('!BBH',1,4,1492))
        elif code==0xa7: log('PADT recebido'); S['result']=S['result'] or 'PADT'
    elif et==0x8864 and sid==S['sid'] and len(pl)>=6:
        proto=struct.unpack('!H',pl[:2])[0]; c,i,l=struct.unpack('!BBH',pl[2:6]); d=pl[6:2+l]
        if proto==0xc021:
            if c==1:
                o=0
                while o+2<=len(d):
                    t,ol=d[o],d[o+1]
                    if t==3: S['auth']=struct.unpack('!H',d[o+2:o+4])[0]
                    o+=ol
                log('LCP conf-req do servidor, auth=',hex(S['auth']) if S['auth'] else None); sess(0xc021,2,i,d); S['srv_ack']=True
            elif c==2: S['our_ack']=True; log('LCP conf-ack nosso')
            elif c==3 or c==4: log('LCP nak/rej',d.hex()); 
            elif c==9: sess(0xc021,10,i,d)
            elif c==5: log('LCP terminate'); S['result']=S['result'] or 'LCP-TERM'
            if S['srv_ack'] and S['our_ack'] and not S['auth_sent'] and S['auth']==0xc023:
                S['auth_sent']=True; sess(0xc023,1,1,bytes([len(USER)])+USER+bytes([len(PWD)])+PWD); log('PAP enviado')
        elif proto==0xc023:
            log('PAP resposta', 'ACK' if c==2 else 'NAK', d[1:].decode(errors='replace') if d else ''); S['result']='PAP-ACK' if c==2 else 'PAP-NAK'
        elif proto==0xc223:
            if c==1:
                vl=d[0]; val=d[1:1+vl]; resp=hashlib.md5(bytes([i])+PWD+val).digest()
                sess(0xc223,2,i,bytes([16])+resp+USER); log('CHAP respondido')
            elif c==3: log('CHAP sucesso'); S['result']='CHAP-OK'
            elif c==4: log('CHAP falha',d); S['result']='CHAP-FAIL'
        elif proto==0x8021:
            log('IPCP code',c,d.hex()); S['result']=S['result'] or 'IPCP'
T0=time.time()
sn=AsyncSniffer(iface=ifc,prn=h,store=False); sn.start(); time.sleep(1)
disc('ff:ff:ff:ff:ff:ff',0x09,0,tag(0x0101,b'')); log('PADI enviado')
while time.time()-T0<30 and S['result'] not in ('PAP-ACK','PAP-NAK','CHAP-OK','CHAP-FAIL','PADT','LCP-TERM'): time.sleep(0.3)
time.sleep(2)
if S['sid']: disc(S['srv'],0xa7,S['sid']); log('PADT enviado')
sn.stop(); print('RESULTADO',S['result'])

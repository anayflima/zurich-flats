import json,os,sys,time,urllib.request,urllib.parse,subprocess
import datetime,zoneinfo
RUN=os.environ.get('RUN') or datetime.datetime.now(zoneinfo.ZoneInfo('Europe/Zurich')).date().isoformat()
_d=datetime.date.fromisoformat(RUN)
while _d.weekday()>=5:_d+=datetime.timedelta(days=1)
TTDATE=_d.strftime('%m/%d/%Y')
M='/work/m/'
h=open(M+'prev2.html',encoding='utf-8').read()
def g(n):
    k='const %s=`'%n;i=h.find(k)+len(k);return h[i:h.find('`',i)]
def setc(h,n,v):
    k='const %s=`'%n;i=h.find(k)+len(k);e=h.find('`',i);return h[:i]+v+h[e:]
TS={x.split('|')[0]:x.split('|') for x in g('TS').split('~') if x.strip()}
R={x.split('|')[0]:x.split('|') for x in open(M+'new_raw.txt',encoding='utf-8').read().split('~') if x.strip()}
q=urllib.parse.urlencode({'from':'47.378,8.5865','to':'Zürich HB','date':TTDATE,'time':'08:00','num':4})
try:
    with urllib.request.urlopen('https://timetable.search.ch/api/route.json?'+q,timeout=30) as r: print('probe',r.status,len(r.read()))
except Exception as e: print('probe err',repr(e)[:200])
MAP={'bus':'bus','tram':'tram','strain':'S-Bahn','ship':'boat'}
def route(lat,lon,to):
    q=urllib.parse.urlencode({'from':'%.6f,%.6f'%(lat,lon),'to':to,'date':TTDATE,'time':'08:00','num':4})
    for a in range(4):
        try:
            with urllib.request.urlopen('https://timetable.search.ch/api/route.json?'+q,timeout=30) as r:j=json.load(r)
            cs=[c for c in j.get('connections',[]) if c.get('duration')]
            if not cs:return None
            c=min(cs,key=lambda c:int(c['duration']))
            ls=[]
            for l in c.get('legs',[]):
                ty=l.get('type')
                if not ty or ty=='walk':continue
                ln=l.get('line') or ''
                s=(MAP[ty]+' '+ln).strip() if ty in MAP else (ln or l.get('type_name') or ty)
                if not ls or ls[-1]!=s:ls.append(s)
            return [str(round(int(c['duration'])/60)),', '.join(ls) or 'walk']
        except Exception as e:
            time.sleep(5*(a+1))
    return None

def route_od(lat,lon,to):
    import re as _re
    q=urllib.parse.urlencode({'from':'%.5f,%.5f'%(lat,lon),'to':to,'date':TTDATE,'time':'08:00','limit':4})
    CAT={'T':'tram','B':'bus','BAT':'boat','FUN':'funicular'}
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://transport.opendata.ch/v1/connections?'+q,headers={'User-Agent':'zurich-flats/1.0'}),timeout=40) as r:j=json.load(r)
            best=None
            for c in j.get('connections',[]):
                mm=_re.match(r'(\d+)d(\d+):(\d+):(\d+)',c.get('duration') or '')
                if not mm:continue
                dd=int(mm.group(1))*1440+int(mm.group(2))*60+int(mm.group(3))+int(mm.group(4))/60
                if best is None or dd<best[0]:best=(dd,c)
            if not best:return None
            ls=[]
            for s in best[1].get('sections',[]):
                jn=s.get('journey')
                if not jn:continue
                ca=(jn.get('category') or '').strip();nu=(jn.get('number') or '').strip()
                l=('S-Bahn '+(nu if nu.upper().startswith('S') else ca+nu)) if ca in ('S','SN') else ((CAT[ca]+' '+nu).strip() if ca in CAT else (ca+' '+nu).strip())
                if l and (not ls or ls[-1]!=l):ls.append(l)
            return [str(round(best[0])),', '.join(ls) or 'walk']
        except Exception:
            time.sleep(10*(a+1))
    return None
DEST=['Zürich HB','Freiestrasse 38, 8032 Zürich','St. Gallen','Zürich Oerlikon']
fixed=left=0;t0=time.time()
for pk,row in TS.items():
    row=(row+['']*9)[:9]
    for k,dst in enumerate(DEST):
        i=1+2*k
        if row[i]:continue
        if time.time()-t0>1500: left+=1;continue
        f=R.get(pk)
        if not f: left+=1;continue
        r=route(47.3+int(f[8])/1e4,8.4+int(f[9])/1e4,dst);time.sleep(1.2)
        if not r: r=route_od(47.3+int(f[8])/1e4,8.4+int(f[9])/1e4,dst)
        if r: row[i],row[i+1]=r;fixed+=1
        else: left+=1
    TS[pk]=row
print('commutes fixed',fixed,'still missing',left)
h=setc(h,'TS','~'.join('|'.join(r) for r in TS.values()))
open(M+'prev2.html','w',encoding='utf-8').write(h)
subprocess.run(['curl','-fsSL','-o',M+'augment.py','https://raw.githubusercontent.com/anayflima/zurich-flats/main/augment.py'],check=True)
s=open(M+'augment.py',encoding='utf-8').read()
if 'def pub(pk):' in s:
    a=s.index('def pub(pk):');b=s.index('M={}');s=s[:a]+"import os\n# publish dates come only from the verified browser scrape (PUBS json); never fetched here\npubs=json.load(open(os.environ['PUBS'])) if os.environ.get('PUBS') else {}\n"+s[b:]
open(M+'augment.py','w',encoding='utf-8').write(s)
r=subprocess.run(['python3',M+'augment.py',M+'prev2.html',M+'new_raw.txt',RUN,M+'index.html'],env=dict(os.environ,PUBS=M+'pubs.json'),capture_output=True,text=True)
print('augment',r.returncode,r.stdout[-700:],r.stderr[-800:])
# Flatfox Premium (priority) badge data, only from the verified browser scrape
try:
    sj=json.load(open('/work/scrape.json'));pr={pk:(v.get('d') or {}).get('flatfox_priority_exclusive_until') for pk,v in sj['det'].items()}
    prm='~'.join('%s|%s'%(k,pr[k][:10]) for k in sorted(pr) if pr[k])
    x=open(M+'index.html',encoding='utf-8').read()
    if 'const PRM=`' in x:x=setc(x,'PRM',prm);open(M+'index.html','w',encoding='utf-8').write(x);print('premium',prm.count('|'))
except Exception as e:print('premium skipped',e)

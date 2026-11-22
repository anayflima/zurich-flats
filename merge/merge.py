# Builds merge/index.html: couple flat + solo flat + office, all within walking distance.
# Inputs (live site): ../index.html (couple RAW/TS/PS), ../solo/data.json, ../offices/data.json
import json,re,math,os,time,requests
from collections import defaultdict
B=os.path.dirname(os.path.abspath(__file__))
UA={'User-Agent':'blue-assistant-distance/1.0'}
RUN=os.environ.get('RUN',time.strftime('%Y-%m-%d'))
MAXW=int(os.environ.get('MAXW','15'))   # max walking minutes between any two places
SOLO_MAX=900; OFF_MAX=500; OFF_ALMOST=800; COUPLE_MAX=2500
h=open(os.path.join(B,'..','index.html')).read()
g=lambda n:re.search(r'const '+n+r'\s*=\s*`([^`]*)`',h).group(1)
TT={}
for s in g('TS').split('~'):
  f=s.split('|')
  if len(f)>1: TT[f[0]]=dict(hb=int(f[1]) if f[1] else None,home=int(f[3]) if len(f)>3 and f[3] else None,oe=int(f[7]) if len(f)>7 and f[7] else None)
VD={}
for s in g('PS').split('~'):
  f=s.split('|')
  if len(f)>1: VD[f[0]]=f[1]
C=[]
for s in g('RAW').strip().split('~'):
  f=s.split('|')
  if len(f)<12: continue
  fl=int(f[11] or 0);pk=f[0]
  o=dict(id=pk,p=float(f[1]),r=float(f[4] or 0),m2=float(f[5] or 0),st=f[6],zip=f[7],lat=47.3+float(f[8])/1e4,lon=8.4+float(f[9])/1e4,end=f[12] if len(f)>12 else '')
  o['url']=('https://www.urbanhome.ch/suchen/'+pk[1:]) if pk[0]=='u' else 'https://flatfox.ch/'+pk+'/'
  o.update(TT.get(pk,{}))
  # couple page criteria: 2+ rooms, up to CHF 2,500, not temporary / student-only / suspicious, photos not flagged, no lease end
  if o['r']>=2 and o['p']<=COUPLE_MAX and not fl&(1|4|8) and VD.get(pk) not in ('red','warn') and not o['end']: C.append(o)
S=[s for s in json.load(open(os.path.join(B,'..','solo','data.json'))) if s['price']<=SOLO_MAX and s.get('lat')]
O=[o for o in json.load(open(os.path.join(B,'..','offices','data.json'))) if o.get('lat') and o.get('cost2') is not None and (o['cost2']<=OFF_MAX or (o['cost2']<=OFF_ALMOST and o.get('privcls')=='yes'))]
def km(a,b,c,d):
  x=math.radians(c-a);y=math.radians(d-b);q=math.sin(x/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(y/2)**2;return 12742*math.asin(math.sqrt(q))
WP=os.path.join(B,'walk.json');W=json.load(open(WP)) if os.path.exists(WP) else {}
def walk(a,b):
  k='%.5f,%.5f|%.5f,%.5f'%(a[0],a[1],b[0],b[1]);k2='%.5f,%.5f|%.5f,%.5f'%(b[0],b[1],a[0],a[1])
  if k in W: return W[k]
  if k2 in W: return W[k2]
  u=f'https://routing.openstreetmap.de/routed-foot/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false'
  for i in range(3):
    try:
      r=requests.get(u,headers=UA,timeout=30).json()['routes'][0];W[k]=[round(r['distance']/1000,2),round(r['duration']/60)];time.sleep(0.4);return W[k]
    except Exception: time.sleep(2)
  return None
P=lambda o:(o['lat'],o['lon'])
LIM=MAXW*0.085  # straight-line prefilter (km), generous
tri=[]
for s in S:
  for o in O:
    if abs(o['lat']-s['lat'])<1e-5 and abs(o['lon']-s['lon'])<1e-5: continue
    if km(*P(s),*P(o))>LIM: continue
    wso=walk(P(s),P(o))
    if not wso or wso[1]>MAXW: continue
    for c in C:
      if km(*P(c),*P(s))<0.05 or km(*P(c),*P(o))<0.05: continue  # same building as the solo flat / office (e.g. same listing on two pages)
      if km(*P(c),*P(s))>LIM or km(*P(c),*P(o))>LIM: continue
      wcs=walk(P(c),P(s));wco=walk(P(c),P(o))
      if not wcs or not wco or wcs[1]>MAXW or wco[1]>MAXW: continue
      tri.append((c,s,o,wcs,wco,wso))
json.dump(W,open(WP,'w'))
# group by solo+office pair -> one cluster, couple flats as options
gr=defaultdict(list)
for t in tri: gr[(t[1]['id'],t[2]['id'])].append(t)
def cscore(c): return c['p']/1000+(c.get('hb') or 40)/15+(c.get('home') or 40)/30
CL=[]
for (sid,oid),ts in gr.items():
  s=ts[0][1];o=ts[0][2]
  ts.sort(key=lambda t:(max(t[3][1],t[4][1],t[5][1]),cscore(t[0])))
  opts=[]
  for c,_,_,wcs,wco,wso in ts:
    opts.append(dict(id=c['id'],p=c['p'],r=c['r'],m2=c['m2'],st=c['st'],zip=c['zip'],lat=c['lat'],lon=c['lon'],url=c['url'],hb=c.get('hb'),home=c.get('home'),oe=c.get('oe'),w_solo=wcs,w_off=wco,maxw=max(wcs[1],wco[1],wso[1]),total=c['p']+s['price']+o['cost2']))
  tier='strict' if (o['cost2']<=OFF_MAX and o.get('privcls')=='yes') else 'almost'
  keep=['id','title','address','area','price','util','type','kind','lease','url','note','lat','lon','hb_pt','mg_pt','home_pt','hb_bike','home_bike']
  CL.append(dict(tier=tier,solo={k:s.get(k) for k in keep},office={k:o.get(k) for k in ['id','title','address','area','price','cost2','basis','privacy','privcls','size','url','note','lat','lon','hb_walk','hb_bike','home_walk','home_bike']},w_so=ts[0][5],opts=opts[:6],nopts=len(opts)))
CL.sort(key=lambda x:(x['tier']!='strict',min(q['maxw'] for q in x['opts']),min(q['total'] for q in x['opts'])))
meta=dict(run=RUN,maxw=MAXW,solo_max=SOLO_MAX,off_max=OFF_MAX,off_almost=OFF_ALMOST,couple_max=COUPLE_MAX,nc=len(C),ns=len(S),no=len(O),hb=[47.3779,8.5403],home=[47.3707,8.5545])
j=lambda x:json.dumps(x,ensure_ascii=False).replace('</','<\\/')
out=open(os.path.join(B,'tpl_merge.html')).read().replace('__DATA__',j(CL)).replace('__META__',j(meta))
open(os.path.join(B,'index.html'),'w').write(out)
json.dump(dict(meta=meta,clusters=CL),open(os.path.join(B,'data.json'),'w'),ensure_ascii=False,indent=1)
print('clusters',len(CL),'strict',sum(x['tier']=='strict' for x in CL),'triples',len(tri),'walk cache',len(W))
for x in CL: print(x['tier'],x['solo']['id'],x['solo']['price'],x['office']['id'],x['office']['cost2'],'w_so',x['w_so'],'opts',x['nopts'],[(q['id'],q['p'],q['maxw'],q['hb']) for q in x['opts'][:3]])

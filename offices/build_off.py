import json,os,re
from offices_data import ROWS,F
g=json.load(open('geo.json')) if os.path.exists('geo.json') else {}
prev={}
if os.path.exists('prev_data.json'):
    prev={d['id']:d for d in json.load(open('prev_data.json'))}
RUN=os.environ.get('RUN',F)
HB=[47.3781008,8.5393635];HOME=[47.3706746,8.554512]
PC={'8001':'Kreis 1 (City)','8002':'Kreis 2 (Enge)','8003':'Kreis 3 (Wiedikon)','8045':'Kreis 3 (Wiedikon)','8004':'Kreis 4 (Aussersihl)','8005':'Kreis 5 (Industrie)','8006':'Kreis 6 (Unterstrass)','8032':'Kreis 7 (Hottingen)','8008':'Kreis 8 (Seefeld)','8047':'Kreis 9 (Albisrieden)','8048':'Kreis 9 (Altstetten)','8037':'Kreis 10 (Wipkingen)','8057':'Kreis 11 (Oerlikon)','8051':'Kreis 12 (Schwamendingen)'}
KW=['Schreibtisch','Büro','Büroraum','Bürogemeinschaft','Arbeitsplatz','Büroplatz','Arbeitsraum','Atelier','Atelierplatz','Hottingen']
def sqm(pc,s):
    if pc!='yes' or re.search('total|area',s): return None
    m=re.match(r'\s*(\d+(?:\.\d+)?)',s)
    if not m: return None
    v=float(m.group(1)); return int(v) if v.is_integer() else v
out=[]
for r in ROWS:
    k,t,a,ar,p,b,c2,pc,pv,sz,av,u,n=r[:13]
    found=r[13] if len(r)>13 else (prev.get(k,{}).get('found') or F)
    m=re.search(r'\b(80\d\d)\b',a); z=m.group(1) if m else ''
    d=dict(id=k,title=t,address=a,area=ar,price=p,basis=b,cost2=c2,privcls=pc,privacy=pv,size=sz,avail=av,url=u,note=n,found=found,plz=z,kreis=PC.get(z,'Other'))
    d['pp']=c2/2 if c2 is not None else None
    s=sqm(pc,sz); d['sqm']=s; d['psqm']=round(c2/s,1) if (s and c2 is not None) else None
    x=g.get(k) or {}
    for f in ('lat','lon','hb_walk','hb_bike','home_walk','home_bike'): d[f]=x.get(f)
    d['precise']=x.get('precise',0)
    out.append(d)
ids={d['id'] for d in out}
gone=[dict(title=v['title'],address=v['address'],price=v['price']) for k,v in prev.items() if k not in ids]
chg=[dict(title=d['title'],old=prev[d['id']]['price'],new=d['price']) for d in out if d['id'] in prev and prev[d['id']]['price']!=d['price']]
meta=dict(run=RUN,hb=HB,home=HOME,gone=gone,chg=chg,kw=KW)
j=lambda o:json.dumps(o,ensure_ascii=False).replace('</','<\\/')
h=open('tpl.html').read().replace('__DATA__',j(out)).replace('__META__',j(meta))
os.makedirs('offices',exist_ok=True);open('offices/index.html','w').write(h)
json.dump(out,open('offices/data.json','w'),ensure_ascii=False,indent=1)
print(len(out),'rows; no geo:',[d['id'] for d in out if d['lat'] is None],'gone',len(gone),'chg',len(chg))

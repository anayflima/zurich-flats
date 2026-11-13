import json,os
from solo_data import ROWS,SKIP,F
g=json.load(open('geo_solo.json'))
prev={}
if os.path.exists('prev_data.json'):
    prev={d['id']:d for d in json.load(open('prev_data.json'))}
RUN=os.environ.get('RUN',F)
HB=[47.3781008,8.5393635];MG=g['_manegg']
out=[]
for r in ROWS:
    d=dict(r);d.pop('geo',None)
    d['found']=prev.get(d['id'],{}).get('found') or RUN
    x=g.get(d['id']) or {}
    for f in ('lat','lon','hb_walk','hb_bike','hb_pt','mg_walk','mg_bike','mg_pt'): d[f]=x.get(f)
    d['precise']=x.get('precise',d.get('precise',0))
    d['psqm']=round(d['price']/d['sqm'],1) if d.get('sqm') else None
    out.append(d)
ids={d['id'] for d in out}
gone=[dict(title=v['title'],address=v['address'],price=v['price']) for k,v in prev.items() if k not in ids]
chg=[dict(title=d['title'],old=prev[d['id']]['price'],new=d['price']) for d in out if d['id'] in prev and prev[d['id']]['price']!=d['price']]
meta=dict(run=RUN,hb=HB,mg=MG,gone=gone,chg=chg,skip=SKIP)
j=lambda o:json.dumps(o,ensure_ascii=False).replace('</','<\\/')
h=open('tpl_solo.html').read().replace('__DATA__',j(out)).replace('__META__',j(meta))
os.makedirs('site',exist_ok=True);open('site/index.html','w').write(h)
json.dump(out,open('site/data.json','w'),ensure_ascii=False,indent=1)
print(len(out),'rows; no geo:',[d['id'] for d in out if d['lat'] is None],'no pt:',[d['id'] for d in out if not d['hb_pt']])

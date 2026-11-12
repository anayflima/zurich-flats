import json,os
from offices_data import ROWS,F
g=json.load(open('geo.json'))
HB=[47.3781008,8.5393635];HOME=[47.3706746,8.554512]
out=[]
for r in ROWS:
    k,t,a,ar,p,b,c2,pc,pv,sz,av,u,n=r
    d=dict(id=k,title=t,address=a,area=ar,price=p,basis=b,cost2=c2,privcls=pc,privacy=pv,size=sz,avail=av,url=u,note=n,found=F)
    x=g.get(k)
    if x:
        d.update(lat=x['lat'],lon=x['lon'],precise=x['precise'],hb_walk=x['hb_walk'],hb_bike=x['hb_bike'],home_walk=x['home_walk'],home_bike=x['home_bike'])
    else: d.update(lat=None,lon=None,precise=0,hb_walk=None,hb_bike=None,home_walk=None,home_bike=None)
    out.append(d)
meta=dict(run=os.environ.get('RUN',F),hb=HB,home=HOME)
j=lambda o:json.dumps(o,ensure_ascii=False).replace('</','<\\/')
h=open('tpl.html').read().replace('__DATA__',j(out)).replace('__META__',j(meta))
os.makedirs('offices',exist_ok=True);open('offices/index.html','w').write(h)
json.dump(out,open('offices/data.json','w'),ensure_ascii=False,indent=1)
print(len(out),'rows; missing geo:',[d['id'] for d in out if d['lat'] is None])

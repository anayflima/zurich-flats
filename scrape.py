import json,sys
from camoufox.sync_api import Camoufox
h=open('/work/m/live.html',encoding='utf-8').read()
def g(n):
    k='const %s=`'%n;i=h.find(k)+len(k);return h[i:h.find('`',i)]
P={x.split('|')[0]:x.split('|') for x in g('RAW').split('~') if x.strip()}
ff=[pk for pk in P if not pk.startswith('u')]
PIN='/api/v1/pin/?east=8.63&west=8.44&north=47.44&south=47.32&max_count=1000&ordering=-insertion&offer_type=RENT&object_category=APARTMENT&max_price=2500'
CTRL={'86478389':(680,'2.5'),'86451008':(862,'5.5'),'825717':(1850,'1.0')}
with Camoufox(headless=True,humanize=True,locale='en-US',os='windows',i_know_what_im_doing=True) as b:
    pg=b.new_page()
    pg.goto('https://flatfox.ch/en/86478389/',wait_until='domcontentloaded',timeout=90000)
    pg.wait_for_timeout(8000)
    print('page title',pg.title())
    pins=pg.evaluate('async u=>{const r=await fetch(u);return await r.json()}',PIN)
    print('pins',len(pins),'86505593 pin price',[x['price_display'] for x in pins if x['pk']==86505593])
    ids=sorted(set(ff)|{str(x['pk']) for x in pins if (x.get('price_display') or 9e9)<=2500})
    out={}
    JS="async ids=>Promise.all(ids.map(async id=>{try{const r=await fetch('/api/v1/public-listing/'+id+'/');return [id,r.status,r.status==200?await r.json():null]}catch(e){return [id,-1,null]}}))"
    for i in range(0,len(ids),6):
        for id,st,d in pg.evaluate(JS,ids[i:i+6]): out[id]={'st':st,'d':d}
        pg.wait_for_timeout(500)
    ok=0
    for pk,(p,r) in CTRL.items():
        d=(out.get(pk) or {}).get('d') or {}
        m=d.get('price_display')==p and str(d.get('number_of_rooms'))==r
        ok+=m;print('CTRL',pk,d.get('price_display'),d.get('number_of_rooms'),'OK' if m else 'FAIL')
    json.dump({'pins':pins,'det':out,'ctrl_ok':ok},open('/work/scrape.json','w'))
import collections
c=collections.Counter(v['st'] for v in out.values());print('statuses',c)
pd=[(pk,P[pk][1],out[pk]['d'].get('price_display')) for pk in ff if out.get(pk,{}).get('d') and str(out[pk]['d'].get('price_display'))!=P[pk][1]]
print('price diffs vs 1 Nov',len(pd),pd[:12])
inact=[pk for pk in ff if not out.get(pk,{}).get('d') or out[pk]['d'].get('status')!='act' or out[pk]['d'].get('reserved')]
print('inactive/removed/reserved',len(inact))
print('new candidate ids',len([i for i in ids if i not in P]))

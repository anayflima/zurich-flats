import requests,time,json,os,re
from solo_data import ROWS
UA={'User-Agent':'blue-assistant-distance/1.0'}
HB=(47.3781008,8.5393635);OE=(47.41162,8.54412)
g=json.load(open('geo_solo.json'))
HOME=tuple(g['_home'])
ng={'_manegg':[OE[0],OE[1]],'_home':g['_home']}
if os.path.exists('geo_solo.json'):
    ng.update(json.load(open('geo_solo.json')))
def route(a,b,p):
    u=f'https://routing.openstreetmap.de/routed-{p}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false'
    for i in range(3):
        try:
            r=requests.get(u,headers=UA,timeout=30).json()['routes'][0];return [round(r['distance']/1000,2),round(r['duration']/60)]
        except Exception: time.sleep(2)
    return None
def dur(s):
    m=re.match(r'(\d+)d(\d+):(\d+):(\d+)',s or '')
    return int(m[1])*1440+int(m[2])*60+int(m[3]) if m else None
def pt(a,to):
    for i in range(3):
        try:
            r=requests.get('https://transport.opendata.ch/v1/connections',params={'from':f'{a[0]:.6f},{a[1]:.6f}','to':to,'date':'2026-11-30','time':'08:00','limit':4},headers=UA,timeout=40)
            c=[dur(x.get('duration')) for x in r.json().get('connections',[])]
            c=[x for x in c if x]
            time.sleep(0.6)
            return [None,min(c)] if c else None
        except Exception as e:
            time.sleep(3)
    return None
GOH=tuple(float(v) for v in os.environ['GOH'].split(',')) if os.environ.get('GOH') else None
for d in ROWS:
    if d['id'] in ng and ng[d['id']].get('home_pt') and (not GOH or ng[d['id']].get('goh_pt')): continue
    c=(d['lat'],d['lon'])
    x={'lat':c[0],'lon':c[1],'precise':d['precise']}
    for n,t,tn in (('hb',HB,'Zürich HB'),('mg',OE,'Zürich Oerlikon'),('home',HOME,f'{HOME[0]},{HOME[1]}'))+((('goh',GOH,f'{GOH[0]},{GOH[1]}'),) if GOH else ()):
        x[n+'_walk']=route(c,t,'foot');x[n+'_bike']=route(c,t,'bike');x[n+'_pt']=pt(c,tn)
    ng[d['id']]=x
    print(d['id'],'HB',x['hb_pt'],x['hb_bike'],'| OE',x['mg_pt'],x['mg_walk'],x['mg_bike'],'| home',x['home_pt'],x['home_bike'])
    json.dump(ng,open('geo_solo.json','w'),indent=1)
json.dump(ng,open('geo_solo.json','w'),indent=1)

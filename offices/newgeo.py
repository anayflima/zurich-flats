import requests,time,json
from offices_data import ROWS
UA={'User-Agent':'blue-assistant-distance/1.0'}
HB=(47.3781008,8.5393635); HOME=(47.3706746,8.554512)
g=json.load(open('geo.json'))
PREC0={'ff_film','ro_hallwyl','ro_wipk','ff_forch'}
def route(a,b,p):
    u=f'https://routing.openstreetmap.de/routed-{p}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false'
    for i in range(3):
        try:
            r=requests.get(u,headers=UA,timeout=30).json()['routes'][0];return [round(r['distance']/1000,2),round(r['duration']/60)]
        except Exception: time.sleep(2)
    return None
for r in ROWS:
    k,a=r[0],r[2]
    if k in g and g[k].get('lat'): continue
    q=a.replace('Wiedikon, 8003','Bahnhof Wiedikon, 8003')+' Zürich'
    if k=='ff_forch': q='Forchstrasse 260, 8008 Zürich'
    res=requests.get('https://nominatim.openstreetmap.org/search',params={'q':q,'format':'json','limit':1,'countrycodes':'ch'},headers=UA,timeout=30).json();time.sleep(1.1)
    if not res:
        q2=q.split(',')[0]+', Zürich'
        res=requests.get('https://nominatim.openstreetmap.org/search',params={'q':q2,'format':'json','limit':1,'countrycodes':'ch'},headers=UA,timeout=30).json();time.sleep(1.1)
    if not res: print(k,'NOT FOUND',q);continue
    c=(float(res[0]['lat']),float(res[0]['lon']))
    d={'lat':c[0],'lon':c[1],'precise':0 if (k in PREC0 or not any(ch.isdigit() for ch in a.split(',')[0])) else 1}
    for n,t in (('hb',HB),('home',HOME)):
        d[n+'_walk']=route(c,t,'foot'); d[n+'_bike']=route(c,t,'bike')
    g[k]=d; print(k,d['hb_walk'],d['hb_bike'],d['home_walk'],d['home_bike'],res[0]['display_name'][:60],flush=True)
json.dump(g,open('geo.json','w'),indent=1)

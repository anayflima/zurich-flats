import requests,time,json,os
from solo_data import ROWS
UA={'User-Agent':'blue-assistant-distance/1.0'}
HB=(47.3781008,8.5393635)
def geo(q):
    try:
        r=requests.get('https://nominatim.openstreetmap.org/search',params={'q':q,'format':'json','limit':1,'countrycodes':'ch'},headers=UA,timeout=30).json()
    except Exception: r=[]
    time.sleep(1.1)
    return (float(r[0]['lat']),float(r[0]['lon']),r[0]['display_name'][:70]) if r else None
def route(a,b,p):
    u=f'https://routing.openstreetmap.de/routed-{p}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false'
    for i in range(3):
        try:
            r=requests.get(u,headers=UA,timeout=30).json()['routes'][0];return [round(r['distance']/1000,2),round(r['duration']/60)]
        except Exception: time.sleep(2)
    return None
def dur(v):
    if isinstance(v,(int,float)): return v/60
    if isinstance(v,str) and ':' in v:
        p=v.split('d')[-1].split(':');p=[float(x) for x in p]
        return p[0]*60+p[1]+(p[2]/60 if len(p)>2 else 0)
    return None
RAW=[]
def pt(a,to):
    for i in range(3):
        try:
            r=requests.get('https://timetable.search.ch/api/route.json',params={'from':f'{a[0]:.6f},{a[1]:.6f}','to':to,'date':'11/16/2026','time':'08:00','num':3},headers=UA,timeout=30)
            if r.status_code==429: time.sleep(6);continue
            j=r.json();c=[dur(x.get('duration')) for x in j.get('connections',[])]
            c=[x for x in c if x and x>0]
            if not RAW: RAW.append(str(j.get('connections',[{}])[0].get('duration')))
            time.sleep(1.5)
            return [None,round(min(c))] if c else None
        except Exception as e:
            time.sleep(3)
    return None
g=json.load(open('geo_solo.json')) if os.path.exists('geo_solo.json') else {}
if '_manegg' not in g:
    m=geo('Bahnhof Zürich Manegg') or geo('Zürich Manegg') or geo('Manegg, Zürich')
    print('MANEGG',m);g['_manegg']=[m[0],m[1]]
MG=tuple(g['_manegg'])
for d in ROWS:
    if d['id'] in g: continue
    c=geo(d['geo'])
    if not c: print('NOT FOUND',d['id']);continue
    x={'lat':c[0],'lon':c[1],'precise':d['precise'],'geo':c[2]}
    for n,t,tn in (('hb',HB,'Zürich HB'),('mg',MG,'Zürich Manegg')):
        x[n+'_walk']=route(c,t,'foot');x[n+'_bike']=route(c,t,'bike');x[n+'_pt']=pt(c,tn)
    g[d['id']]=x
    print(d['id'],'HB pt',x['hb_pt'],'bike',x['hb_bike'],'walk',x['hb_walk'],'| MG pt',x['mg_pt'],'bike',x['mg_bike'],'|',c[2][:45])
json.dump(g,open('geo_solo.json','w'),indent=1)
print('raw duration sample',RAW)

import requests, time, json
UA={'User-Agent':'blue-assistant-distance/1.0'}
HB=(47.3781008,8.5393635); HOME=(47.3706746,8.554512)
P=[('konrad','Konradstrasse, 8005 Zürich',0),('technopark','Technoparkstrasse 1, 8005 Zürich',1),('morgarten','Morgartenstrasse, 8004 Zürich',0),('schaff','Schaffhauserstrasse 21, 8006 Zürich',1),('neptun','Neptunstrasse 25, 8032 Zürich',1),('selnau','Selnaustrasse 52, 8001 Zürich',1),('freya','Freyastrasse 14, 8004 Zürich',1),('fabrik','Fabrikstrasse, 8005 Zürich',0),('burg','Burgstrasse 8, 8037 Zürich',1),('lessing','Lessingstrasse 13, 8002 Zürich',1),('hofacker','Hofackerstrasse 13, 8032 Zürich',1),('aemtler','Aemtlerstrasse 92, 8003 Zürich',1),('zimmerli','Zimmerlistrasse, 8004 Zürich',0),('badener','Badenerstrasse 134, 8004 Zürich',1),('sihlfeld','Sihlfeldstrasse, 8003 Zürich',0),('raeffel','Räffelstrasse 11, 8045 Zürich',1),('gruben38','Grubenstrasse 38, 8045 Zürich',1),('gruben9','Grubenstrasse 9, 8045 Zürich',1),('albis','Albisriederstrasse 253, 8047 Zürich',1),('glasmaler','Glasmalergasse 5, 8004 Zürich',1),('bernina','Berninaplatz, 8057 Zürich',0),('schindler','Schindlerstrasse 26, 8006 Zürich',1),('lochergut','Lochergut, Badenerstrasse, Zürich',0),('kanzlei','Kanzleistrasse 200, 8004 Zürich',1)]
def route(a,b,p):
    u=f'https://routing.openstreetmap.de/routed-{p}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false'
    for i in range(3):
        try:
            r=requests.get(u,headers=UA,timeout=30).json()['routes'][0];return [round(r['distance']/1000,2),round(r['duration']/60)]
        except Exception: time.sleep(2)
    return None
out={}
for k,q,prec in P:
    r=requests.get('https://nominatim.openstreetmap.org/search',params={'q':q,'format':'json','limit':1,'countrycodes':'ch'},headers=UA,timeout=30).json();time.sleep(1.1)
    if not r: print(k,'NOT FOUND');continue
    c=(float(r[0]['lat']),float(r[0]['lon']))
    d={'lat':c[0],'lon':c[1],'precise':prec,'geo':r[0]['display_name'][:90]}
    for n,t in (('hb',HB),('home',HOME)):
        d[n+'_walk']=route(c,t,'foot'); d[n+'_bike']=route(c,t,'bike')
    out[k]=d; print(k,d['hb_walk'],d['hb_bike'],d['home_walk'],d['home_bike'],d['geo'][:50])
json.dump(out,open('geo.json','w'),indent=1)

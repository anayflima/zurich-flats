import json,time,requests
UA={'User-Agent':'blue-assistant-distance/1.0'}
HOME=(47.3706746,8.554512)
def route(a,b,p):
    u=f'https://routing.openstreetmap.de/routed-{p}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false'
    for i in range(3):
        try:
            r=requests.get(u,headers=UA,timeout=30).json()['routes'][0];return [round(r['distance']/1000,2),round(r['duration']/60)]
        except Exception: time.sleep(2)
    return None
def dur(v):
    if isinstance(v,(int,float)): return v/60
    if isinstance(v,str) and v.isdigit(): return int(v)/60
    if isinstance(v,str) and ':' in v:
        p=[float(x) for x in v.split('d')[-1].split(':')];return p[0]*60+p[1]+(p[2]/60 if len(p)>2 else 0)
    return None
def pt(a,b):
    for i in range(4):
        try:
            r=requests.get('https://timetable.search.ch/api/route.json',params={'from':f'{a[0]:.6f},{a[1]:.6f}','to':f'{b[0]:.6f},{b[1]:.6f}','date':'11/16/2026','time':'08:00','num':3},headers=UA,timeout=30)
            if r.status_code==429: time.sleep(6);continue
            c=[dur(x.get('duration')) for x in r.json().get('connections',[])];c=[x for x in c if x and x>0]
            time.sleep(1.5);return [None,round(min(c))] if c else None
        except Exception: time.sleep(3)
    return None
g=json.load(open('geo_solo.json'))
for k,x in g.items():
    if k.startswith('_') or x.get('home_bike'): continue
    c=(x['lat'],x['lon'])
    x['home_walk']=route(c,HOME,'foot');x['home_bike']=route(c,HOME,'bike');x['home_pt']=pt(c,HOME)
    print(k,'HOME pt',x['home_pt'],'bike',x['home_bike'],'walk',x['home_walk'])
g['_home']=list(HOME)
json.dump(g,open('geo_solo.json','w'),indent=1)
b=open('build_solo.py').read()
b=b.replace("'mg_walk','mg_bike','mg_pt'):","'mg_walk','mg_bike','mg_pt','home_walk','home_bike','home_pt'):")
b=b.replace('meta=dict(run=RUN,hb=HB,mg=MG,','meta=dict(run=RUN,hb=HB,mg=MG,home=g["_home"],')
assert 'home_pt' in b and '_home' in b
open('build_solo.py','w').write(b)
t=open('tpl_solo.html').read()
R=[
(r"close to Zürich HB or Bahnhof Manegg.",r"close to Zürich HB or Bahnhof Manegg. Times also to Home (Hottingen)."),
(r"🚉 <b>Manegg</b>: ${tm(d,'mg_pt')} transit · ${tm(d,'mg_bike')} bike</div>",r"🚉 <b>Manegg</b>: ${tm(d,'mg_pt')} transit · ${tm(d,'mg_bike')} bike<br>🏠 <b>Home</b>: ${tm(d,'home_pt')} transit · ${tm(d,'home_bike')} bike · ${tm(d,'home_walk')} walk</div>"),
(r"const toMg=d=>mn(d.mg_pt)??mn(d.mg_bike);",r"const toMg=d=>mn(d.mg_pt)??mn(d.mg_bike);const toHome=d=>mn(d.home_pt)??mn(d.home_bike);"),
(r"<label>Area<select id=fArea>",r"<label>Max to Home (min)<select id=fHome><option value=''>Any</option><option>10</option><option>15</option><option>20</option><option>30</option></select></label><label>Area<select id=fArea>"),
(r"mg:+$('fMg').value||1e9,",r"mg:+$('fMg').value||1e9,hm:+$('fHome').value||1e9,"),
(r"if(f.mg<1e9&&(toMg(d)==null||toMg(d)>f.mg))return false;",r"if(f.mg<1e9&&(toMg(d)==null||toMg(d)>f.mg))return false;if(f.hm<1e9&&(toHome(d)==null||toHome(d)>f.hm))return false;"),
(r"<option value=mg>Closest to Manegg</option>",r"<option value=mg>Closest to Manegg</option><option value=home>Closest to Home</option>"),
(r"mg:(a,b)=>(toMg(a)??999)-(toMg(b)??999),",r"mg:(a,b)=>(toMg(a)??999)-(toMg(b)??999),home:(a,b)=>(toHome(a)??999)-(toHome(b)??999),"),
(r"'fMg','fArea'",r"'fMg','fHome','fArea'"),
(r"<button data-p=mg>≤ 15 min to Manegg</button>",r"<button data-p=mg>≤ 15 min to Manegg</button><button data-p=home>≤ 15 min to Home</button>"),
(r"if(p=='mg')$('fMg').value='15';",r"if(p=='mg')$('fMg').value='15';if(p=='home')$('fHome').value='15';"),
(r"['mg_bike','Manegg bike'],",r"['mg_bike','Manegg bike'],['home_pt','Home transit'],['home_bike','Home bike'],"),
(r"const TT={hb_pt:1,hb_bike:1,mg_pt:1,mg_bike:1};",r"const TT={hb_pt:1,hb_bike:1,mg_pt:1,mg_bike:1,home_pt:1,home_bike:1};"),
(r"<td>${tm(d,'mg_bike')}</td>",r"<td>${tm(d,'mg_bike')}</td><td>${tm(d,'home_pt')}</td><td>${tm(d,'home_bike')}</td>"),
(r"['Manegg by bike',d=>mn(d.mg_bike),d=>tm(d,'mg_bike')],",r"['Manegg by bike',d=>mn(d.mg_bike),d=>tm(d,'mg_bike')],['Home by transit',d=>mn(d.home_pt),d=>tm(d,'home_pt')],['Home by bike',d=>mn(d.home_bike),d=>tm(d,'home_bike')],['Home on foot',d=>mn(d.home_walk),d=>tm(d,'home_walk')],"),
(r".bindTooltip('Bahnhof Manegg',{permanent:true,direction:'top'});",r".bindTooltip('Bahnhof Manegg',{permanent:true,direction:'top'});L.circleMarker(META.home,{radius:11,color:'#111',fillColor:'#16a34a',fillOpacity:1,weight:3}).addTo(map).bindTooltip('Home (Hottingen)',{permanent:true,direction:'top'});"),
(r"<span><i class=dot style='background:#a855f7;border:2px solid #111'></i>Manegg</span>",r"<span><i class=dot style='background:#a855f7;border:2px solid #111'></i>Manegg</span><span><i class=dot style='background:#16a34a;border:2px solid #111'></i>Home</span>"),
(r"<th>Median to Manegg</th>",r"<th>Median to Manegg</th><th>Median to Home</th>"),
(r"<td>${fm(med(a.map(toMg)))}</td>",r"<td>${fm(med(a.map(toMg)))}</td><td>${fm(med(a.map(toHome)))}</td>"),
(r"<div id=sc2></div>",r"<div id=sc2></div><h3>Price vs time to Home</h3><div id=sc3></div>"),
(r"$('sc2').innerHTML=scat(toMg,'To Bahnhof Manegg');",r"$('sc2').innerHTML=scat(toMg,'To Bahnhof Manegg');$('sc3').innerHTML=scat(toHome,'To Home');"),
(r"'shortest trip to Manegg']];",r"'shortest trip to Manegg'],[fm(Math.min(...L0.map(toHome).filter(x=>x!=null))),'shortest trip to Home']];"),
(r"(${fm(toMg(m))}).`);",r"(${fm(toMg(m))}).`);const hm=L0.filter(d=>toHome(d)!=null).sort((a,b)=>toHome(a)-toHome(b))[0];if(hm)I.push(`Closest to Home: <b>${esc(hm.title)}</b> (${fm(toHome(hm))}).`);"),
(r"<h3>Closest to Bahnhof Manegg</h3><div class=grid id=t3></div>",r"<h3>Closest to Bahnhof Manegg</h3><div class=grid id=t3></div><h3>Closest to Home (Hottingen)</h3><div class=grid id=t5></div>"),
(r"G('t4',L0.filter(d=>d.type=='own').sort((a,b)=>a.price-b.price).slice(0,4),'None yet.')",r"G('t4',L0.filter(d=>d.type=='own').sort((a,b)=>a.price-b.price).slice(0,4),'None yet.');G('t5',L0.filter(d=>toHome(d)!=null).sort((a,b)=>toHome(a)-toHome(b)).slice(0,4),'None yet.')"),
(r"${fm(toMg(d))} to Manegg.",r"${fm(toMg(d))} to Manegg, ${fm(toHome(d))} to Home."),
(r"Times to HB and Manegg use public transport",r"Times to HB, Manegg and Home use public transport"),
]
for a,b2 in R:
    assert a in t,'MISSING '+a[:60]
    t=t.replace(a,b2)
open('tpl_solo.html','w').write(t)
print('patched ok')

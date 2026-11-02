import json,re,os,sys,time,math,urllib.request,urllib.parse,collections,subprocess
RUN='2026-11-02'
h=open('/work/m/live.html',encoding='utf-8').read()
def g(h,n):
    k='const %s=`'%n;i=h.find(k)
    if i<0:return None
    i+=len(k);return h[i:h.find('`',i)]
def setc(h,n,v):
    k='const %s=`'%n;i=h.find(k)+len(k);e=h.find('`',i);return h[:i]+v+h[e:]
P={x.split('|')[0]:x.split('|') for x in g(h,'RAW').split('~') if x.strip()}
TSrows={x.split('|')[0]:x for x in g(h,'TS').split('~') if x.strip()}
S=json.load(open('/work/scrape.json'));D={k:v['d'] for k,v in S['det'].items() if v['d']}
assert S['ctrl_ok']==3,'controls failed'
def price(d):
    if d.get('price_unit')!='monthly':return None
    if d.get('price_display_type')=='TOTAL' and d.get('price_display'):return int(d['price_display'])
    if d.get('rent_gross'):return int(d['rent_gross'])
    return None
N={};dropped=collections.Counter()
for pk,f in P.items():
    if pk.startswith('u'):N[pk]=f;continue
    d=D.get(pk)
    if not d or d.get('status')!='act' or d.get('reserved'):dropped['no longer active']+=1;continue
    p=price(d)
    if p is None or p>2500:dropped['price unknown/over']+=1;continue
    f=list(f)
    if str(p)!=f[1]:
        f[1]=str(p);f[2]=str(int(d['rent_net'])) if d.get('rent_net') else '';f[3]=str(int(d['rent_charges'])) if d.get('rent_charges') is not None else ''
    N[pk]=f
zc=collections.defaultdict(list)
for f in P.values():zc[f[7]].append((47.3+int(f[8])/1e4,8.4+int(f[9])/1e4))
def km(a,b,c,e):
    x=(e-b)*math.cos(math.radians((a+c)/2))*111.32;y=(c-a)*110.57;return math.hypot(x,y)
SUB=['befristet','zwischenmiete','untermiete','sublet','sublease','temporary','temporär','temporaer']
WG=['wg-zimmer','wg zimmer','wg-room','room in a shared','shared flat','shared apartment','mitbewohner','flatmate','zimmer in einer','in einer wg']
new=[];sk=collections.Counter()
for pk,d in D.items():
    if pk in P:continue
    if d.get('status')!='act' or d.get('reserved'):sk['inactive']+=1;continue
    if d.get('offer_type')!='RENT' or d.get('object_category')!='APARTMENT':sk['type']+=1;continue
    z=int(d.get('zipcode') or 0)
    if not(8001<=z<=8099) or 'rich' not in (d.get('city') or ''):sk['not city']+=1;continue
    p=price(d)
    if not p or p>2500:sk['price']+=1;continue
    if d.get('is_temporary'):sk['temporary']+=1;continue
    md=d.get('moving_date') or ''
    if md and md>'2027-04-30':sk['late']+=1;continue
    t=((d.get('description') or '')+' '+(d.get('description_title') or '')+' '+(d.get('short_title') or '')).lower().replace('unbefristet','').replace('nicht befristet','')
    if any(w in t for w in SUB):sk['sublet/temporary wording']+=1;continue
    if any(w in t for w in WG):sk['room in shared flat']+=1;continue
    lat,lon=d.get('latitude'),d.get('longitude')
    if lat is None or lon is None:sk['no location']+=1;continue
    if zc.get(str(z)):
        cl=sum(a for a,b in zc[str(z)])/len(zc[str(z)]);co=sum(b for a,b in zc[str(z)])/len(zc[str(z)])
        if km(lat,lon,cl,co)>2.5:sk['location does not match postcode']+=1;continue
    r=str(d.get('number_of_rooms') or '');r=r[:-2] if r.endswith('.0') else r
    m2=d.get('surface_living') or d.get('livingspace')
    mt=d.get('moving_date_type');mv='now' if mt=='imm' else 'agr' if mt=='agr' else (md if mt=='dat' and md else '')
    fl=(2 if d.get('is_furnished') else 0)+(4 if ('student' in t or 'studierend' in t) else 0)
    st=(d.get('street') or '').replace('|',' ').replace('~',' ').replace('`',"'")
    rec=[pk,str(p),str(int(d['rent_net'])) if d.get('rent_net') else '',str(int(d['rent_charges'])) if d.get('rent_charges') is not None else '',r,str(int(m2)) if m2 else '',st,str(z),str(round((lat-47.3)*1e4)),str(round((lon-8.4)*1e4)),mv,str(fl),'']
    new.append((rec,lat,lon));N[pk]=rec
print('existing kept',sum(1 for k in N if k in P),'dropped',dict(dropped))
print('new',len(new),'skipped',dict(sk))
MAP={'bus':'bus','tram':'tram','strain':'S-Bahn','ship':'boat'}
def route(lat,lon,to):
    q=urllib.parse.urlencode({'from':'%.6f,%.6f'%(lat,lon),'to':to,'date':'11/02/2026','time':'08:00','num':4})
    for a in range(3):
        try:
            with urllib.request.urlopen('https://timetable.search.ch/api/route.json?'+q,timeout=30) as r:j=json.load(r)
            cs=[c for c in j.get('connections',[]) if c.get('duration')]
            if not cs:return None
            c=min(cs,key=lambda c:int(c['duration']))
            ls=[]
            for l in c.get('legs',[]):
                ty=l.get('type')
                if not ty or ty=='walk':continue
                ln=l.get('line') or ''
                s=(MAP[ty]+' '+ln).strip() if ty in MAP else (ln or l.get('type_name') or ty)
                if not ls or ls[-1]!=s:ls.append(s)
            return [str(round(int(c['duration'])/60)),', '.join(ls) or 'walk']
        except Exception as e:
            time.sleep(2)
    return None
c=route(47.3+780/1e4,8.4+1865/1e4,'Zürich HB');print('control 86478389 HB',c,'vs saved',TSrows['86478389'].split('|')[1:3])
DEST=['Zürich HB','Freiestrasse 38, 8032 Zürich','St. Gallen'];miss=0
for rec,lat,lon in new:
    row=[rec[0]]
    for dst in DEST:
        r=route(lat,lon,dst);time.sleep(0.3)
        if r:row+=r
        else:row+=['',''];miss+=1
    TSrows[rec[0]]='|'.join(row)
print('commute lookups missing',miss)
pubs={rec[0]:(D[rec[0]].get('published') or '')[:10] for rec,_,_ in new}
json.dump(pubs,open('/work/m/pubs.json','w'))
fails=[]
def patch(a,b,n=1):
    global h
    c=h.count(a)
    if c!=n:fails.append((a[:70],c));return
    h=h.replace(a,b)
patch(".addTo(layer)})}function mvok",".on('mouseover click',()=>showP(o)).addTo(layer)})}function showP(o){const e=$('mpanel');if(e)e.innerHTML=card(o)}function mvok")
patch('<div id=map></div>','<div id=mapwrap><div id=map></div><div id=mpanel><p class=note>Hover over or tap a pin to see that flat\'s full details here: commute times, photo verdict, pros and cons, dates and links.</p></div></div>')
patch('</style>','#mapwrap{display:flex;gap:10px;align-items:flex-start}#mapwrap #map{flex:3;margin:8px 0}#mpanel{flex:2;max-height:520px;overflow:auto;margin:8px 0}#mpanel .card{border-color:#2f6ea5}@media(max-width:760px){#mapwrap{flex-direction:column}#mapwrap #map{width:100%}#mpanel{max-height:none;width:100%}}</style>')
patch("o.thb=t.hb?t.hb[0]:o.lz+2;o.mhb=t.hb?t.hb[1]:'est.';","o.thb=t.hb?t.hb[0]:null;o.mhb=t.hb?t.hb[1]:'';")
patch("o.tfs=t.fs?t.fs[0]:Math.round(6+o.fs*4);o.mfs=t.fs?t.fs[1]:'est.';","o.tfs=t.fs?t.fs[0]:null;o.mfs=t.fs?t.fs[1]:'';")
patch("else{o.msg='est.'}","else{o.sgmin=null;o.msg=''}")
patch('${tt(o.thb)} (${o.mhb})','${ct(o.thb,o.mhb)}')
patch('${tt(o.tfs)} (${o.mfs})','${ct(o.tfs,o.mfs)}')
patch('${tt(o.sgmin)} (${o.msg})','${ct(o.sgmin,o.msg)}')
h,nh=re.subn(r'<b>Uni St\. Gallen \(HSG\):</b>.*?km<br>','',h,count=1);print('HSG card line removed',nh)
patch('o.sgmin<=f.sg&&o.thb<=f.thb&&o.tfs<=f.tfs','(f.sg>=999||o.sgmin!=null&&o.sgmin<=f.sg)&&(f.thb>=999||o.thb!=null&&o.thb<=f.thb)&&(f.tfs>=999||o.tfs!=null&&o.tfs<=f.tfs)')
patch('sg:(a,b)=>a.sgmin-b.sgmin,thb:(a,b)=>a.thb-b.thb,tfs:(a,b)=>a.tfs-b.tfs','sg:(a,b)=>(a.sgmin??1e9)-(b.sgmin??1e9),thb:(a,b)=>(a.thb??1e9)-(b.thb??1e9),tfs:(a,b)=>(a.tfs??1e9)-(b.tfs??1e9)')
patch('med(v.map(o=>o.thb))','med(v.map(o=>o.thb).filter(x=>x!=null))')
patch('med(v.map(o=>o.sgmin))','med(v.map(o=>o.sgmin).filter(x=>x!=null))')
patch("else if(o.uh)a.push('UrbanHome does not show a publish date')","else if(o.uh)a.push('UrbanHome listing, last checked 1 Nov 2026 and not re-checked since (UrbanHome shows no publish date)')")
patch('const $=id=>document.getElementById(id);',"function ct(m,l){return m==null?'not looked up':tt(m)+(l?' ('+l+')':'')}const $=id=>document.getElementById(id);")
h,n1=re.subn(r'Times marked est\.[^<]*','Times that could not be looked up show as "not looked up"; nothing on this page is estimated.',h);print('note fixed',n1)
h,n2=re.subn(r' and the University of St\. Gallen \(HSG\)','',h);print('header HSG removed',n2)
print('PATCH FAILS',fails)
if fails:sys.exit(1)
h=setc(h,'TS','~'.join(TSrows.values()))
open('/work/m/prev2.html','w',encoding='utf-8').write(h)
recs=sorted(N.values(),key=lambda f:int(f[1]))
open('/work/m/new_raw.txt','w',encoding='utf-8').write('~'.join('|'.join(f) for f in recs))
s=open('/work/m/augment.py',encoding='utf-8').read()
if 'def pub(pk):' in s:
    a=s.index('def pub(pk):');b=s.index('M={}')
    s=s[:a]+"import os\n# publish dates come only from the verified browser scrape (PUBS json); never fetched here\npubs=json.load(open(os.environ['PUBS'])) if os.environ.get('PUBS') else {}\n"+s[b:]
    open('/work/m/augment.py','w',encoding='utf-8').write(s)
r=subprocess.run(['python3','/work/m/augment.py','/work/m/prev2.html','/work/m/new_raw.txt',RUN,'/work/m/index.html'],env=dict(os.environ,PUBS='/work/m/pubs.json'),capture_output=True,text=True);print('augment',r.returncode,r.stdout[-600:],r.stderr[-800:])
for rec,_,_ in new[:60]:print('NEW',rec[0],'CHF',rec[1],rec[4],'rooms',rec[5] and rec[5]+' m2',rec[6],rec[7],'|',TSrows[rec[0]])

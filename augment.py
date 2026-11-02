#!/usr/bin/env python3
# Zurich flats page: add/refresh found + published dates and the New findings diff.
# usage: augment.py PREV_HTML [NEW_RAW_FILE|-] [RUN_DATE] [OUT]
#   PREV_HTML  = the live page (curl https://anayflima.github.io/zurich-flats/)
#   NEW_RAW    = tonight's fresh listings in the same 13-field RAW format ('-' = keep current)
import re,sys,json,datetime,urllib.request,concurrent.futures as cf
prev=open(sys.argv[1],encoding='utf-8').read()
nrp=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='-' else None
run=sys.argv[3] if len(sys.argv)>3 else datetime.date.today().isoformat()
out=sys.argv[4] if len(sys.argv)>4 else 'index.html'

def getc(h,n):
    k='const %s=`'%n; i=h.find(k)
    if i<0: return None
    s=i+len(k); return h[s:h.find('`',s)]
def setc(h,n,v):
    k='const %s=`'%n; i=h.find(k); s=i+len(k); e=h.find('`',s); return h[:s]+v+h[e:]
def recs(raw):
    d={}
    for r in raw.strip().split('~'):
        if r.strip(): f=r.split('|'); d[f[0]]=f
    return d
def rep(h,a,b,n=1):
    c=h.count(a)
    assert c==n, (a[:60],c)
    return h.replace(a,b)

prevraw=getc(prev,'RAW')
newraw=open(nrp,encoding='utf-8').read().strip() if nrp else prevraw.strip()
P=recs(prevraw); N=recs(newraw)
pm=getc(prev,'META'); baseline=pm is None
prevrun=getc(prev,'RUN') or run
meta={}
if pm:
    for r in pm.split('~'):
        if r: f=r.split('|'); meta[f[0]]=f[1:]

import os
# publish dates come only from the verified browser scrape (PUBS json); never fetched here
pubs=json.load(open(os.environ['PUBS'])) if os.environ.get('PUBS') else {}
M={}
for pk in N:
    old=meta.get(pk,['',''])
    found=old[0] or ('2026-11-01' if baseline else run)
    M[pk]=[found, old[1] if len(old)>1 and old[1] else pubs.get(pk,'')]
if baseline:
    chg={'baseline':True,'prev':run,'new':[],'price':[],'gone':[]}
else:
    chg={'baseline':False,'prev':prevrun,
         'new':[pk for pk in N if pk not in P],
         'price':[[pk,int(P[pk][1]),int(N[pk][1])] for pk in N if pk in P and P[pk][1]!=N[pk][1]],
         'gone':[[pk,P[pk][1],P[pk][4],P[pk][6],P[pk][7]] for pk in P if pk not in N]}

h=prev
if baseline:
    pre,rest=h.split('const RAW=`',1); raw,post=rest.split('`',1)
    n1=post.count('Freiestrasse 38'); post=post.replace('Freiestrasse 38','Home (Hottingen)')
    n2=0
    for x,y in (('Freiestrasse / ETH','home / ETH'),(', Freiestrasse ${tt(o.tfs)}',', home ${tt(o.tfs)}')):
        n2+=pre.count(x)+post.count(x); pre=pre.replace(x,y); post=post.replace(x,y)
    n0=pre.count('Freiestrasse 38'); pre=pre.replace('Freiestrasse 38','Home (Hottingen)')
    print('relabelled',n0,n1,n2,'left:',[m.start() for m in re.finditer('Freiestrasse',pre+post)][:10])
    h=pre+'const RAW=`'+raw+'`'+post
    h=rep(h,'</style>','.tag.nw{background:#14532d;color:#fff;font-weight:700}.tag.dn{background:#e6f4ea;color:#1e6b35;font-weight:600}.tag.up{background:#fde2e2;color:#9b1c1c;font-weight:600}#news{border:2px solid #2f6ea5}</style>')
    h=rep(h,'<nav><a href=#top>','<nav><a href=#news>New findings</a><a href=#top>')
    h=rep(h,'<section id=top>','<section id=news><h2>New findings</h2><p id=nsum></p><h3>New since the last update</h3><div class=grid id=nnew></div><h3>Price changes</h3><div id=nprice></div><h3>No longer listed</h3><ul id=ngone></ul><h3>Freshly published on Flatfox (last 3 days)</h3><div class=grid id=nfresh></div></section><section id=top>')
    h=re.sub(r'Live snapshot [^<]*? - (\d+) flats',lambda m:'<span id=upd>X</span>',h,count=1)
    assert '<span id=upd>' in h
    h=rep(h,'<label>Street / postcode search','<label>Found by Blue<select id=ffound><option value=\'\'>any time</option><option value=n>new in the last update</option><option value=3>in the last 3 days</option><option value=7>in the last 7 days</option><option value=14>in the last 14 days</option></select></label><label>Published on Flatfox<select id=fpub><option value=0>any time</option><option value=3>in the last 3 days</option><option value=7>in the last 7 days</option><option value=14>in the last 14 days</option><option value=30>in the last 30 days</option></select></label><label>Street / postcode search')
    h=rep(h,'<option value=vd>Best photo verdict</option>','<option value=vd>Best photo verdict</option><option value=pub>Newest on Flatfox</option><option value=found>Newest found by Blue</option>')
    h=rep(h,'const SORT={score:bySc,','const SORT={score:bySc,pub:(a,b)=>(b.pub||\'\').localeCompare(a.pub||\'\')||a.p-b.p,found:(a,b)=>(b.found||\'\').localeCompare(a.found||\'\')||(b.pub||\'\').localeCompare(a.pub||\'\'),')
    h=rep(h,'&&mvok(o.mv,f.mv))','&&mvok(o.mv,f.mv)&&dok(o))')
    h=rep(h,"fsort:'score',","fsort:'score',ffound:'',fpub:'0',")
    h=rep(h,'return `<div class=card>${phs}','return `<div class=card>${phs}${nb(o)}')
    h=rep(h,'<div class=sub>${mvt(o.mv)}</div>','<div class=sub>${mvt(o.mv)}</div><div class=sub>${dl(o)}</div>')
    h=rep(h,'run();</script></body></html>','RNEWS();run();</script></body></html>')
    JS=r'''const META=`x`;const RUN=`x`;const CHG=`x`;const MT={};META.split('~').forEach(s=>{if(!s)return;const f=s.split('|');MT[f[0]]=[f[1],f[2]]});const CG=JSON.parse(CHG);const NEWS=new Set(CG.new);const PCH={};CG.price.forEach(x=>PCH[x[0]]=x);D.forEach(o=>{const m=MT[o.pk]||[];o.found=m[0]||'';o.pub=m[1]||'';o.isNew=NEWS.has(o.pk);o.pch=PCH[o.pk]||null});
function dago(d){return d?(Date.now()-Date.parse(d+'T00:00:00'))/864e5:1e9}
function fd(d){if(!d)return '';return new Date(d+'T12:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'})}
function dl(o){const a=[];if(o.found)a.push('Found by Blue '+fd(o.found));if(o.pub)a.push('published on Flatfox '+fd(o.pub));else if(o.uh)a.push('UrbanHome does not show a publish date');return a.join(' - ')}
function nb(o){let s='';if(o.isNew)s+="<span class='tag nw'>NEW</span>";if(o.pch){const d=o.pch[2]<o.pch[1];s+=`<span class='tag ${d?'dn':'up'}'>price ${d?'down':'up'}, was CHF ${fmt(o.pch[1])}</span>`}return s?`<div>${s}</div>`:''}
function dok(o){const a=$('ffound').value,b=+$('fpub').value;if(a==='n'&&!o.isNew)return false;if(a&&a!=='n'&&dago(o.found)>+a)return false;if(b&&dago(o.pub)>b)return false;return true}
function RNEWS(){const nw=D.filter(o=>o.isNew).sort(bySc);const pc=D.filter(o=>o.pch);const fr=D.filter(o=>o.pub&&(Date.parse(RUN)-Date.parse(o.pub))/864e5<=3).sort((a,b)=>b.pub.localeCompare(a.pub)||a.p-b.p);$('upd').textContent=`Updated ${fd(RUN)} - ${D.length} flats`;$('nsum').innerHTML=CG.baseline?`Tracking started on ${fd(RUN)} with ${D.length} flats. From the next nightly update (4 AM Zurich time) this section shows what changed since the night before: new flats, price changes and flats that were taken down. Every card also shows when Blue first found it and when it was published on Flatfox, and you can filter by both below.`:`Update of ${fd(RUN)} compared with ${fd(CG.prev)}: <b>${nw.length} new</b>, <b>${pc.length} price changes</b>, <b>${CG.gone.length} no longer listed</b>. ${D.length} flats tracked in total.`;$('nnew').innerHTML=nw.map(card).join('')||`<p class=note>${CG.baseline?'Nothing yet, this is the first snapshot.':'No new flats since the last update.'}</p>`;$('nprice').innerHTML=pc.length?'<div class=grid>'+pc.map(card).join('')+'</div>':'<p class=note>No price changes.</p>';$('ngone').innerHTML=CG.gone.map(g=>`<li>CHF ${fmt(+g[1])} - ${g[2]} rooms - ${g[3]||'address on request'}, ${g[4]} Zurich</li>`).join('')||'<li class=note>None.</li>';$('nfresh').innerHTML=fr.slice(0,12).map(card).join('')||'<p class=note>No flats published in the last 3 days.</p>'}
'''
    h=rep(h,'const $=id=>document.getElementById(id);',JS+'const $=id=>document.getElementById(id);')

h=setc(h,'RAW',newraw)
h=setc(h,'META','~'.join('%s|%s|%s'%(pk,M[pk][0],M[pk][1]) for pk in N))
h=setc(h,'RUN',run)
h=setc(h,'CHG',json.dumps(chg,ensure_ascii=False).replace('`',"'"))
open(out,'w',encoding='utf-8').write(h)
fl=[pk for pk in N if not pk.startswith('u')]
print('flats',len(N),'flatfox',len(fl),'with pub',sum(1 for pk in fl if M[pk][1]),'new',len(chg['new']),'price',len(chg['price']),'gone',len(chg['gone']))
print('pub last3d',sorted([M[pk][1] for pk in fl if M[pk][1]>= (datetime.date.fromisoformat(run)-datetime.timedelta(days=3)).isoformat()]))
print('size',len(h))

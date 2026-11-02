import sys
p='/work/o/index.html'
h=open(p,encoding='utf-8').read()
J=open('/work/team.js',encoding='utf-8').read()
if 'function TINIT' in h:
    print('already patched');sys.exit(0)
fails=[]
def rep(a,b):
    global h
    c=h.count(a)
    if c!=1:
        fails.append((a[:60],c));return
    h=h.replace(a,b)
if 'function REF(' not in h: fails.append(('REF missing',0))
rep("function SAVE(){try{localStorage.setItem(SK,JSON.stringify(ST))}catch(e){}}","function SAVE0(){try{localStorage.setItem(SK,JSON.stringify(ST))}catch(e){}}function SAVE(){SAVE0();try{TDIFF()}catch(e){}}")
rep("function acts(o){return acts0(o)+(ST.r[o.pk]?'':XB(o))}","function acts(o){return acts0(o)+(ST.r[o.pk]?'':XB(o))+TW(o.pk)}")
rep("<button class=tab data-io=share>&#128279; Share my lists</button>","<button class=tab data-io=team>&#128101; Team <span id=tst>(join)</span></button>")
i=h.find('function IO(')
if i<0: fails.append(('IO missing',0))
else:
    j=h.find(')',i);par=h[i+12:j];k=h.find('{',j)+1
    h=h[:k]+"if("+par+"==='team')return TEAMUI();"+h[k:]
    print('IO param',par)
rep('SHIN();if(ST.w)RESC();',J+'SHIN();if(ST.w)RESC();')
sw="navigator.serviceWorker.register('sw.js').catch(()=>{});"
rep(sw,sw+'TINIT();')
css='#tpanel{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9999;overflow:auto}#tpanel .tbox{background:#fff;color:#1a1a1a;max-width:680px;margin:24px auto;padding:16px 18px;border-radius:12px}.who{font-size:12px;color:#777;margin-top:4px}.tfeed{padding-left:18px}.tfeed li{margin:6px 0}'
k=h.find('</style>')
if k<0: fails.append(('style',0))
else: h=h[:k]+css+h[k:]
print('FAILS',fails)
if fails: sys.exit(1)
open(p,'w',encoding='utf-8').write(h)
print('patched',len(h))

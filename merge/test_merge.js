const {JSDOM,VirtualConsole}=require('jsdom');const fs=require('fs');
let bad=0;const vc=new VirtualConsole();vc.on('jsdomError',e=>{if(!/Not implemented/.test(e.message)){console.log('JSERR',e.message);bad=1}});
const dom=new JSDOM(fs.readFileSync(__dirname+'/index.html','utf8'),{runScripts:'dangerously',url:'https://anayflima.github.io/zurich-flats/merge/',virtualConsole:vc});
const D=dom.window.document,$=i=>D.getElementById(i),n=s=>D.querySelectorAll(s).length;
console.log('groups',n('.cl'),'strict',n('.cl.strict'),'KPI',$('kpis').textContent);
$('fA').checked=false;$('fA').dispatchEvent(new dom.window.Event('input'));console.log('strict only',n('.cl'));
$('fW').value='5';$('fW').dispatchEvent(new dom.window.Event('input'));console.log('walk<=5',n('.cl'));
console.log('first',(D.querySelector('.cl')||{}).textContent?.slice(0,400));
process.exit(bad?1:0);

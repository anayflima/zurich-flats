import json
d=json.load(open('data.json'))
g={x['id']:{k:x.get(k) for k in ('lat','lon','precise','hb_walk','hb_bike','home_walk','home_bike')} for x in d}
json.dump(g,open('geo.json','w'),indent=1);print('geo',len(g))

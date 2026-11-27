F='2026-11-27'
FF='https://flatfox.ch/en/flat/'
# Ana 2026-11-27: solo page = only places she would live in by herself (own studio/flat, no WG rooms), max CHF 1,000,
# regular lease, in and around Oerlikon (near Zurich Oerlikon station, or near Gohar's new flat in Affoltern).
ROWS=[
dict(id='f86577953',title='1.5-room flat with balcony near the forest',address='Schürliweg 1, 8046',area='Affoltern',price=909,util='incl. utilities (CHF 844 net + CHF 65 on account)',type='own',kind='1.5-room flat, 1st floor',rooms='1½',sqm=35,lease='open',leasetxt='Take over the lease (successor tenant), no end date; landlord must approve',avail='1 Jan 2027',furn=False,url=FF+'schurliweg-1-8046-zurich/86577953/',note='Deposit CHF 1,500. Furnished now; you can take over all the furniture for CHF 500 (optional). Cellar, shared laundry, drying and bike rooms; garage space CHF 130 optional. Walking distance to ETH Hönggerberg. Flatfox lets you message only after 8 Dec unless you pay for Priority.',lat=47.41788,lon=8.50207,precise=1),
]
SKIP=[
dict(title='Furnished flat, Neunbrunnenstrasse 213 (8046)',price='CHF 1,000',why='Short sublet, 10 Jan – 30 Apr 2027, and you share it with another tenant.',url=FF+'neunbrunnenstrasse-213-8046-zurich/86568318/'),
]
# Ana 2026-11-22: no temporary listings. Keep this filter LAST.
NOT_TEMP=True
ROWS=[r for r in ROWS if r.get('lease')!='temp']
# Ana 2026-11-27: own places only, max CHF 1,000 (more is not acceptable).
ROWS=[r for r in ROWS if r['type']=='own' and r['price']<=1000]

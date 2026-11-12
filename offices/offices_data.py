S='https://ronorp.net/zurich/market/search?keyword='
P='https://ronorp.net/market/posts/'
F='2026-11-12'
# key,title,address,area,price,basis,cost2,privcls,privacy,size,avail,url,note
ROWS=[
('konrad','Ruhiges Büro im Kreis 5','Konradstrasse, 8005','Kreis 5',440,'Whole room, incl. utilities',440,'yes','Own room','12 m²','1 Nov 2026 or by agreement (temporary)',P+'ruhiges-buro-im-kreis-5','Unfurnished, desk and shelf can be taken over, shared WC'),
('technopark','Büro im Technopark','Technoparkstrasse 1, 8005','Escher Wyss',250,'1 desk, owner keeps the other',None,'no','Shared with owner','14 m²','Temporary',P+'buro-zur-gemeinsamen-nutzung-nahe-escherwyssplatzbahnhof-hardbrucke','Only 1 desk free'),
('morgarten','Zwei Arbeitsplätze, einzeln oder zusammen','Morgartenstrasse, 8004','Kreis 4 (Stauffacher)',350,'Unclear: per desk or both?',None,'maybe','Shared office community','140 m² total','Now',P+'zwei-arbeitsplatze-zu-vermieten-einzeln-oder-zusammen','Furnished; meeting room, kitchen, internet, printer, cleaning, showers incl.'),
('schaff','Presseladen, zwei Büroplätze','Schaffhauserstrasse 21, 8006','Kreis 6',465,'Unclear: per desk or both?',None,'maybe','Two-person offices','—','Jan/Feb 2027',P+'zwei-buroplatze-in-burogemeinschaft-zentraler-altbau-mit-charme','Internet, printer, newspapers, coffee incl.'),
('neptun','Arbeitsplatz in Hottingen','Neptunstrasse 25, 8032','Kreis 7 (Hottingen)',375,'Per desk',750,'no','Room shared with 3 others','—','Now',P+'arbeitsplatz-in-hottingen','Furnished; meeting room, kitchen, garden'),
('selnau','Gemeinschaftsbüro am Stauffacher','Selnaustrasse 52, 8001','Kreis 1',395,'Per desk',790,'no','Shared open office','—','Now',P+'buroarbeitsplatz-im-gemeinschaftsburo-am-stauffacher-zu-vermieten','2–3 desks free; internet, printer, kitchen'),
('freya','Atelier/Büroraum Freyastrasse','Freyastrasse 14, 8004','Kreis 4 (Wiedikon)',537,'Share of a CHF 1,074 room',716,'no','Room shared with a video editor','36 m²','1 Dec 2026',P+'atelierburoraum-freyastr-14-in-8004-zurich-zu-vermieten-1','2 of 3 shares = CHF 716; 1 min from Bahnhof Wiedikon'),
('fabrik','Atelier / Büroraum 16 m²','Fabrikstrasse, 8005','Kreis 5',680,'Whole room',680,'yes','Own room in an office','16 m²','Now',S+'Fabrikstrasse',''),
('badener','Büro in Bürogemeinschaft','Badenerstrasse 134, 8004','Kreis 4',665,'Whole room',665,'yes','Own room in an office','17.5 m²','—',S+'Badenerstrasse%20134',''),
('sihlfeld','Möbliertes Büro zur Untermiete','Sihlfeldstrasse, 8003','Kreis 3',750,'Whole room, furnished',750,'yes','Own room','23.4 m²','—',S+'Sihlfeldstrasse',''),
('hofacker','Büroraum / Atelier (abschliessbar)','Hofackerstrasse 13, 8032','Kreis 7 (Hegibachplatz)',800,'Whole lockable room',800,'yes','Own room','—','Now (a 2nd room from 1 Dec 2026)',S+'Hofackerstrasse',''),
('bernina','Büro-/Hobbyraum Berninaplatz','Berninaplatz, 8057','Oerlikon',565,'Whole room',565,'yes','Own room','15 m²','Now',S+'Berninaplatz',''),
('schindler','Büroräume in kreativer Bürogemeinschaft','Schindlerstrasse 26, 8006','Kreis 6',1000,'Whole room (1–3 rooms)',1000,'yes','Own room','14–18 m²','—',S+'Schindlerstrasse',''),
('burg','Atelier-Tische in Wipkingen','Burgstrasse 8, 8037','Wipkingen',320,'Per table',640,'no','Shared atelier','—','—',S+'Atelier-Tische',''),
('raeffel','1–2 Arbeitsplätze','Räffelstrasse 11, 8045','Binz',390,'Per desk',780,'no','Shared office','—','—',S+'R%C3%A4ffelstrasse',''),
('gruben38','Loft 38, Arbeitsplätze','Grubenstrasse 38, 8045','Binz',800,'Double desk (CHF 500 single)',800,'no','Shared loft','25 m² area','—',P+'arbeitsplatzeburoflache-in-loft-zu-vermieten','Kitchen and meeting room incl.'),
('gruben9','Arbeitsinsel mit 4 Plätzen','Grubenstrasse 9, 8045','Wiedikon/Binz',1100,'Island of 4 desks',1100,'no','Shared architecture office','—','—',S+'Grubenstrasse%209',''),
('lessing','Atelierplatz Textiles','Lessingstrasse 13, 8002','Enge',360,'1 place only',None,'no','Shared atelier','—','—',S+'Lessingstrasse','Only 1 place'),
('aemtler','Atelier-/Büroplatz 9 m²','Aemtlerstrasse 92A, 8003','Kreis 3',350,'1 place only',None,'no','4-person community','9 m²','Nov 2026 – Feb 2027 (temporary)',S+'Aemtlerstrasse','Only 1 place'),
('zimmerli','Atelierplatz bei der Hardbrücke','Zimmerlistrasse, 8004','Kreis 4',300,'1 place only',None,'no','Shared atelier house','—','Temporary',S+'Zimmerlistrasse','Only 1 place'),
('albis','2–4 Arbeitsplätze, Bürogemeinschaft','Albisriederstrasse 253, 8047','Albisrieden',550,'Unclear: per desk?',None,'no','Shared office','—','—',S+'Albisriederstrasse',''),
('glasmaler','Schaufensterbüro am Stauffacher','Glasmalergasse 5, 8004','Kreis 4',550,'Unclear: per desk?',None,'no','Shared office','—','—',S+'Glasmalergasse',''),
('lochergut','Büroplätze nähe Lochergut','Badenerstrasse (Lochergut), 8004','Kreis 4',550,'Unclear: per desk?',None,'no','Shared office','—','—',S+'Lochergut',''),
('kanzlei','Arbeitsplatz nähe Bullingerplatz','Kanzleistrasse 200, 8004','Kreis 4',1100,'Unclear',None,'no','Shared atelier','—','—',S+'Kanzleistrasse',''),
]

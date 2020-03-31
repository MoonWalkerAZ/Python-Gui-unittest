# Python Gui unittest

V sklopu dela v podjetju sem naredil grafični vmesnik za izvajanje unittestov.
Kratka navodila uporabe:

* Poskrbimo, da imamo nameščene vse knjižnice, ki so vključene v projektu
* Zaženemo file mainRunner.py z Python 3.7
* Nato se prikaže grafični vmesnik

Ob zagonu programa se odpre grafično okolje. Pred testiranjem moremo izbrati mapo v kateri se nahajajo unittesti. To storimo tako, da kliknemo na gumb izberi mapo. Ko to izberemo se nam izpiše njena pot, ter ozadje se obarva zeleno. To lahko vidimo na spodnji sliki.

![Globalni Test 1](/zaslonske_slike/globalni_test.png)

* Globalni testi

Če želimo zagnati vse unitteste, ki se nahajajo v izbrani mapi, to storimo tako, da kliknemo na zavihek »Globalni test« in nato še na gumb »Zaženi globalni test«. Ob kliku na gumb se prikaže slikica na kateri piše »loading«, kar pomeni, da se testi izvajajo. Po končanem izvajanju se pod besedo »Izpis(čas)« zapišejo vsi neuspešno izvedeni testi, če ti obstajajo. V primeru, da pride do neuspešnih testov se ozadje obarva rdeče in napiše se napis »FAIL«, drugače se ozadje obarva zeleno in napiše se napis »OK«. Vsi testi, ki se niso izvedli uspešno so zapisani v spodnjem belem polju. Delovanje lahko vidimo na zgornji in spodnji sliki.

![Globalni Test 2](/zaslonske_slike/globalni_test2.png)

* Če kliknemo na posamičen test lahko podrobno pregledamo napako tega testa.

![Globalni Test 2](/zaslonske_slike/podrobna_napaka.png)

* Posamični testi oz. izbira določenih testov, ki se nahajajo v class-u.



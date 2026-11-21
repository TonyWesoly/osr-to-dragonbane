# Kanoniczna mechanika konwersji OSR (B/X, OSE) → Dragonbane PL

Obowiązuje wyłącznie oficjalna polska terminologia *Dragonbane* (Black Monk Games: *Podręcznik główny* [PG] i *Bestiariusz* [Best.]). Zanim opiszesz dowolnego potwora, czar lub broń, sprawdź je w `reference/` przez `scripts/lookup_db.py` (pamiętaj: w obu podręcznikach drukowany nr strony = `STRONA X - 2`).

---

## 1. Słownik kanoniczny i notacja

- **6 Cech (WIELKIMI LITERAMI):** `SIŁ` (Siła), `KON` (Kondycja), `ZRC` (Zręczność), `INT` (Inteligencja), `DET` (Determinacja), `CHA` (Charyzma). **UWAGA:** `SW` (Siła Woli) to WYŁĄCZNIE zasób punktów na czary/zdolności — NIGDY cecha do testów! Przerażenie, petryfikację (Bazyliszek/Meduza, Best. str. 70, 86) i uroki zawsze testuje się na **DET**.
- **Współczynniki:** `WT` (Wytrzymałość), `SW` (Siła Woli), `Szybkość`, `Pancerz`, `Mod. obrażeń`, `Zajadłość`, `Rozmiar` (`Mały, Zwykły, Duży, Wielki, Rój`).
- **Kości i testy:** wyłącznie polska notacja `k3, k4, k6, k8, k10, k12, k20`. Brak modyfikatorów liczbowych do k20 — wyłącznie **z błyskiem** lub **ze zgrzytem**. Krytyki: **wyturlać smoka** (1) / **wyturlać demona** (20), **forsowanie testu**, **test pasywny**, **test przeciwstawny**, **otwarty test przeciwstawny**.
- **6 Dolegliwości (zawsze wielką literą; dają zgrzyt w testach danej cechy):**
  - **Wyczerpanie** (`SIŁ`) | **Niemoc** (`KON`) | **Zamęt** (`ZRC`) | **Złość** (`INT`) | **Strach** (`DET`) | **Zniechęcenie** (`CHA`).
  *(Powtórzona dolegliwość → wybierz inną; przy wszystkich 6 → utrata k6 SW, przy 0 SW → k6 WT).*
- **Czas i dystans (zawsze metrycznie):**
  - Runda OSR → **Runda** (10 s); Dungeon Turn (10 min) → **Kwadrans** (15 min); Watch (4–6 h) → **Kwarta** (6 h; marsz 15 km pieszo / 30 km konno).
  - Siatka 5 ft (1 kratka) → **2 metry** (1 pole 2×2 m; zasięg wręcz = 2 m, broń długa = 4 m); 10 ft → **3–4 m**; 30 ft → **10 m**; 60 ft → **20 m**; 1 mila → **1,5 km** (heks 6-milowy ≈ 10 km, ~1 Kwarta w lesie/trudnym terenie).
- **Nazwy 30 umiejętności głównych + 3 szkół magii:** w tekście przygody zapisuj **WIELKIMI LITERAMI I POGRUBIONE** (odmienione gramatycznie, np. *przetestuj **SZUKANIE***). W blokach statystyk PN i zwierząt zapisuj normalnie, jak w PG (np. `Czujność 10, Skradanie 12`). Nie wymyślaj nieistniejących umiejętności!

| Umiejętność (Cecha) | Zastosowanie przy konwersji z OSR |
| --- | --- |
| **AKROBACJE** (ZRC) | Wspinaczka, skoki, balansowanie, łagodzenie upadku |
| **BLEFOWANIE** (CHA) | Kłamstwa, oszustwo, udawanie |
| **CZUJNOŚĆ** (INT) | Nasłuchiwanie (Hear Noise), wykrywanie zasadzek (test pasywny) |
| **JEŹDZIECTWO** (ZRC) | Manewry konne, walka w siodle |
| **JĘZYKI OBCE** (INT) | Czytanie run, pradawnych inskrypcji, zwojów i ksiąg czarów, obce mowy |
| **LECZENIE** (INT) | Pierwsza pomoc (ratowanie z agonii; brak bandaży = zgrzyt), oględziny zwłok |
| **MITY I LEGENDY** (INT) | Historia, religia, heraldyka, dawne kulty i magia |
| **PŁYWANIE** (ZRC) | Pływanie w trudnych warunkach, nurkowanie |
| **POLOWANIE** (ZRC) | Tropienie zwierzyny, sidła, łowienie |
| **PRZEKONYWANIE** (CHA) | Dyplomacja, zastraszanie, namawianie PN (vs DET przy dużym ryzyku) |
| **PRZETRWANIE** (INT) | Nawigacja (hexcrawl), ślady, obóz, mróz |
| **RZEMIOSŁO** (SIŁ) | Naprawa pancerza/sprzętu, ocena konstrukcji i murarki |
| **SKRADANIE** (ZRC) | Ciche poruszanie (Move Silently), krycie się (Hide in Shadows) |
| **SZUKANIE** (INT) | Tajne drzwi, ukryte pułapki, przeszukiwanie komnat (1 kwadrans) |
| **TARGOWANIE** (CHA) | Handel, wycena towarów |
| **UNIKI** (ZRC) | Unikanie ciosów, zionięć i pułapek mechanicznych |
| **WIEDZA O BESTIACH** (INT) | Rozpoznawanie potworów i ich słabości |
| **WYSTĘPY** (CHA) | Muzyka, śpiew, recytacja, dworska etykieta/popisy |
| **ZWINNE PALCE** (ZRC) | Zamki (brak wytrychów = zgrzyt), rozbrajanie pułapek, kradzież |
| **ŻEGLOWANIE** (INT) | Łódź, nawigacja wodna |
| **Broń (10):** **BIJATYKA**, **KOSTURY**, **KUSZE**, **ŁUKI**, **MIECZE**, **MŁOTY**, **NOŻE**, **PROCE**, **TOPORY**, **WŁÓCZNIE** | Walka wręcz i dystansowa |
| **Magia (3):** **ANIMIZM**, **ELEMENTALIZM**, **MENTALIZM** (+ Magia ogólna) | Rzucanie czarów, identyfikacja magii |

---

## 2. Trójpodział adwersarzy i zasada „Najpierw oficjalny Bestiariusz!”

1. **Postacie Niezależne (PN – Pionki i Figury):** ludzie, gobliny, hobgobliny, orki, ogry, szkielety, kultyści, krasnoludy, satyry, karkiony, kotoludy, jaszczurianie, żabianie itp. Testują atak na k20, mogą parować i unikać.
   - **Pionki:** brak SW, wspólna inicjatywa, giną przy 0 WT.
   - **Figury (bossowie/dowódcy):** własna inicjatywa, pula SW i **Zdolności heroiczne** (*Krzepa, Koncentracja, Zasłona, Odskok, Sprawność bojowa, Podwójne uderzenie, Zamaszyste cięcie, Czaromistrzostwo*).
   - **Domyślne wartości PN:** niewymieniona umiejętność = **5**; SIŁ/ZRC z mod. obr. (brak = 10, +k4 = 14, +k6 = 17); KON = maks. WT − 2 za poziom *Krzepy*; DET = maks. SW − 2 za poziom *Koncentracji* (lub 10); INT/CHA = 10.
2. **Potwory:** smoki, demony, bestie, trolle, olbrzymy, konstrukty, silniejsi nieumarli (upiory, widma, mumie, wampiry, ghule, żywe trupy), istoty baśniowe i osobliwce (centaury, wróżki, najady, syreny, drzewce, łabędzie panny w postaci ptaka), insektoidzi, roje.
   - Mają **Zajadłość**, **Rozmiar** i **Tabelę k6 Ataków Potwora** (trafiają automatycznie; nigdy ten sam atak 2 razy z rzędu — przy powtórzeniu przechodzi się do kolejnego wiersza).
   - Domyślnie ataków potwora **nie można parować** (chyba że wpis mówi *„Atak można sparować”* — dodawaj to w 1–2 atakach fizycznych tabeli k6!), ale zawsze można ich **unikać** (poza efektami przerażenia — PG str. 83; udany unik całkowicie neguje obrażenia, także zionięć i obszarówek!).
   - Potwory domyślnie widzą w ciemności, są odporne na przerażenie, pchnięcie, rozbrajanie, pochwycenie, trucizny i czary kontroli (*Pęta natury, Więzienie natury, Uśpienie, Dominacja, Zamrożenie* [efekt unieruchomienia]); ich domyślne UNIKI/parowanie to **15**.
   - **KLUCZOWE DLA OSR – Cecha `Perswazja`:** Potworów domyślnie NIE można przekonywać! Każdej rozumnej, baśniowej lub gadającej istocie OSR (duchy, wróżki, centaury, smoki, z którymi da się paktować) **koniecznie dodaj cechę `Perswazja`** (*„W przeciwieństwie do innych potworów, istotę można PRZEKONYWAĆ [zwykle lub ze zgrzytem]”*).
3. **Zwykłe Zwierzęta:** wilki, dziki, niedźwiedzie, olbrzymie szczury, węże. Brak pancerza i tabeli k6 — tylko Szybkość, WT, 1 atak z umiejętnością i 2–3 umiejętności.

### Najpierw sprawdź oficjalne podręczniki! (szybka mapa)
Używaj nazw z nagłówków treści haseł: **ghul** (nie ghoul ze spisu treści), **lindorm** (nie lindworm ze spisu treści), **wampiroperz**. Zawsze weryfikuj statystyki przez `scripts/lookup_db.py`.
- **Humanoidy / PN (Nie-potwory):** *Bandyta, Strażnik, Kultysta, Złodziej, Arcymag, Herszt bandytów, Zaprzysiężony rycerz, Goblin, Hobgoblin, Ork, Ogr [Duży], Szkielet, Jaszczurianin, Karkion, Kotolud, Satyr, Żabianin* (PG / Best.).
- **Nieumarli (Potwory):** *Błędny ognik, Ghul, Mumia, Upiór, Wampir, Widmo, Żywy trup* (PG / Best.).
- **Baśniowe, osobliwce i leśne (Potwory):** *Centaur, Drzewiec, Harpia, Łabędzia panna [elfka = PN / łabędzica = Potwór], Minotaur, Najada, Syrena, Wróżka* (PG / Best.).
- **Bestie, insektoidzi, szlamy, roje:** *Mrówkoid, Pająkoid, Żukoid, Ogromny pająk, Wampiroperz (Rój), Ogromna ameba (reskin pod szlamy/galarety!), Bazyliszek, Chimera, Gryf, Hipogryf, Hydra, Kalidon, Koń wodny, Mantykora, Meduza, Ogromna ośmiornica, Pegaz, Rok, Wąż morski, Wilkołak, Worg* (PG / Best.).
- **Wielcy przeciwnicy:** *Trolle (PG oraz górski, jaskiniowy, leśny), Olbrzymy (PG oraz górski, leśny, morski, Tytan), Smoki (Smoczątko, Młody [WT 60, Panc. 4, Best. str. 126 — idealna baza pod smoka 6–8 HD], Dorosły, Prastary, Lindorm), Golem, Demony (PG oraz chaosu, cienia, krwi, ognia, stróż)* (PG / Best.).

### Kalibracja współczynników (B/X / OSE → Dragonbane)

| HD w B/X | Profil | WT | Broń (PN) / Obrażenia (Potwór k6) | Mod. obr. (PN) | Zajadłość |
| --- | --- | --- | --- | --- | --- |
| ≤ 1/2 HD | Pionek / Zwierzę / Rój | 4–6 (Rój: 16–20) | PN: 8–10 / Rój: k8–2k6 | Brak | – (Rój: 1–2) |
| 1-1 do 1 HD | Pionek / Słaby Potwór | PN: 7–10 / Potwór: 8–14 | PN: 10–12 / Potwór: k8–2k6 | Brak / +k4 | – / 1 |
| 1+ do 2 HD | Elitarny Pionek / Pomniejszy Potwór | PN: 10–14 / Potwór: 14–22 | PN: 12–13 / Potwór: k10–2k6 | +k4 | – / 1–2 |
| 3 do 4 HD | Figura (PN) / Potwór | PN: 16–24 / Potwór: 24–38 | PN: 14–15 / Potwór: 2k6–2k10 (obsz. k8–2k6) | +k4 do +k6 | 1–2 |
| 5 do 7 HD | Groźny Potwór / Boss | 34–58 *(niżej przy pancerzu/reg.)* | 2k8–3k8 (obsz. 2k6–2k10) | Brak | 2 *(lub BG − 1 dla bossa solo)* |
| 8 do 10 HD | Potężny Boss (np. Młody smok) | 56–78 | 2k10–4k8 (obsz. 2k8–2k10) | Brak | 2–3 *(Olbrzymy: 1; lub BG − 1)* |
| 11+ HD | Legendarny Potwór | 80–108 | 3k10–5k10 (obsz. 2k10–4k10) | Brak | 2–3 *(lub BG − 1)* |

### Kalibracja Pancerza (Zbroje PN vs Pancerz naturalny Potworów)
- **PN:** brak / AC 9[10] → `—`; skórzana / AC 8[11] → `1`; ćwiekowana / AC 7[12] → `2` *(zgrzyt: Skradanie)*; kolcza / AC 5–6[13–14] → `4` *(zgrzyt: Skradanie, Uniki)*; płytowa / AC 3–4[15–16] → `6` *(zgrzyt: Akrobacje, Skradanie, Uniki)*. Tarcza nie dodaje Pancerza — służy do parowania. Hełm otwarty `+1` *(zgrzyt: Czujność)*, Hełm zamknięty `+2` *(zgrzyt: Czujność i ataki dystansowe)*.
- **Potwory (NIE przenoś ślepo AC z B/X!):** większość zwinnych/futrzastych bestii (gryf, mantykora, chimera, minotaur, troll leśny/górski, olbrzymy) ma **Pancerz 0**. Gruba skóra/łuska/lekka chityna = `2–3` *(np. troll jaskiniowy, mrówkoid, smoczątko, hydra, ogromna ośmiornica)*; łuski Młodego smoka = `4`; ciężki pancerz naturalny *(Dorosły smok, golem, bazyliszek, lindorm, drzewiec, żukoid, tytan)* = `6`; Prastary smok = `8`.

---

## 3. Ekonomia akcji, liczebność, roje i morale

W *Dragonbane* postać ma **tylko 1 akcję na rundę** (wspólną na atak i parowanie/unik). Przewaga liczebna z B/X zabija drużynę w spirali obrony:
- **1–3 wrogów B/X:** konwersja 1:1.
- **4–6 wrogów:** zmniejsz o ~25% (maks. ~1,25 wroga w zwarciu na 1 BG) lub zastąp 1 Potworem (Zajadłość 2).
- **7–12 wrogów:** podziel na **fale taktyczne** (3–4 w zwarciu, 2 z dystansu, reszta wchodzi jako posiłki w 2.–4. rundzie). Pionki dzielą 1 kartę inicjatywy.
- **13+ drobnych wrogów / Chmara:** zamień w **1 Potwora o rozmiarze Rój** (WT 16–24, Zajadłość 1–2, **Odporność**: połowa obrażeń od broni materialnej, pełne od ognia i obszarówek jak **PODMUCH**). *Nigdy nie sumuj WT 15 szczurów!*
- **Morale (ML) B/X → krótka wskazówka taktyczna** (jak w oficjalnych przygodach DB, oszczędza miejsce!):
  - `ML 2–6`: uciekają po pierwszych ranach / stracie pierwszego towarzysza;
  - `ML 7–8`: uciekają lub poddają się po utracie połowy oddziału / połowy WT;
  - `ML 9–10`: walczą, dopóki nie padnie dowódca lub 2/3 oddziału;
  - `ML 11–12`: walczą do końca, nie można ich przerazić. *(Dla niejednoznacznych sytuacji MG może opcjonalnie przetestować **DET**).*

---

## 4. Magia, trucizny, choroby i rzuty obronne

### Magia i zasada „Metal zaburza magię”
- **Metal zaburza magię (PG str. 58):** metalowa zbroja (w tym ćwiekowana!) lub metalowa broń pod ręką blokują rzucanie czarów! Konwertując opancerzonego kapłana (*Cleric*) lub elfa z B/X: (1) daj szaty/skórzaną + **KAMIENNA SKÓRA** i kostur/drewnianą pałkę, **LUB** (2) zapisz cuda jako wrodzone zdolności za **SW** (bez reguły metalu), **LUB** (3) dla bossów użyj profilu Potwora.
- **Skalowanie kręgów:** 1. krąg B/X → sztuczki (1 SW) lub potęga 1 (2 SW); 2.–3. krąg → potęga 2 (4 SW) lub krąg 2–3 DB; 5.–6. krąg → rytuały (czas: Kwadrans lub Kwarta). Uwaga: **KULA OGNIA** (krąg 1) trafia **1 cel** (nie obszarowo; wyższa potęga = +k6 obr. albo dodatkowa kula w inny cel); obszarowy ogień to **BURZA OGNIA** (krąg 3).
- **Mapa najczęstszych czarów B/X → DB:** *Light* → **ŚWIATŁO**; *Detect Magic* → **WYCZUCIE MAGII**; *Dispel Magic* → **ODCZAROWANIE**; *Protection from Evil* → **OCHRONA / MAGICZNA TARCZA**; *Knock/Wizard Lock* → **KLUCZNIK**; *Feather Fall* → **PIÓRKOSPADANIE**; *Cure Wounds* → **OPATRZENIE / ULECZENIE / UZDROWIENIE**; *Raise Dead* → **WSKRZESZENIE**; *Sleep* → **UŚPIENIE**; *Entangle/Web* → **PĘTA NATURY / WIĘZIENIE NATURY**; *Speak with Animals* → **MOWA ZWIERZĄT**; *Turn Undead* → **PRECZ! / ZGIŃ, PRZEPADNIJ!**; *Lightning* → **BŁYSKAWICA / PIORUN / GROM**; *Fireball/Burning Hands* → **KULA OGNIA / STRUGA OGNIA / BURZA OGNIA**; *Gust of Wind* → **PODMUCH / WICHER**; *Shatter* → **STRZASKANIE**; *Wall of Stone* → **KOLUMNA / MUR**; *Shield* → **KAMIENNA TARCZA**; *Stoneskin/Barkskin* → **KAMIENNA SKÓRA**; *Hold Person/Ice* → **ZAMROŻENIE**; *Magic Missile* → **UDERZENIE MYŚLĄ / KULA OGNIA**; *Charm/Suggestion* → **DOMINACJA**; *ESP* → **TELEPATIA**; *Locate Object* → **POSZUKIWANIE**; *Clairvoyance* → **DALEKOWIDZENIE**; *Levitate/Fly* → **LEWITACJA / LATANIE**; *Haste* → **SZYBKOBIEŻNOŚĆ**; *Teleport* → **TELEPORTACJA**; *Conjure Elemental* → **GNOM / ONDYNA / SALAMANDRA / SYLF**; *Enchant Weapon* → **ZAKLĘCIE ORĘŻA**.
- **Moce baśniowe** (wróżki, driady, baśniowe uroki i klątwy): zapisuj jako cechy specjalne lub wpisy w tabeli `k6`, nie jako klasyczne szkoły magii.

### Trucizny, choroby i rzuty obronne (*Save-or-Die*)
- **Trucizny** (otwarty test przeciwstawny **Moc [9 / 12 / 15+] vs KON**; nie działają na Potwory!):
  - **Śmiercionośna:** pełny = k6 obr. co turę do 0 WT lub odtrutki; częściowy = k6 tylko w następnej turze.
  - **Paraliżująca:** pełny = **Wyczerpanie** + test **KON** co turę (nie jest akcją; porażka odbiera ruch i akcje, nawet darmowe, w tej rundzie; trwa Kwadrans lub do odtrutki); częściowy = **Wyczerpanie**.
  - **Usypiająca:** pełny = **Zamęt** + test **KON** co turę (porażka usypia na **1 Kwartę**, budzi odtrutka lub ≥1 obr.); częściowy = **Zamęt**.
- **Choroby:** otwarty test przeciwstawny **Zjadliwość (10–12) vs KON** (porażka = od jutra **Niemoc**, −k6 WT dziennie i blokada leczenia WT/SW/dolegliwości aż do zdanego dziennego testu **KON** lub **LECZENIA**).
- **Inne rzuty obronne B/X:**
  - *Save vs Petrification* → test **DET** (nie jest akcją): porażka = zamiana w kamień i śmierć po 2k6 rundach (co turę szansa przełamania testem **DET** [u Meduzy ze zgrzytem] lub **ODCZAROWANIEM** pot. 1 — jak w *Best. str. 70, 86*).
  - *Energy Drain (wyssanie poziomów)* → utrata k6 lub 2k6 **SW** + **Zniechęcenie / Strach** (opcjonalnie chłód blokujący regenerację do ogrzania przez Kwartę, jak u Upiora/Widma).
  - *Save vs Breath / Wands / Blast* → **UNIKI** (w walce sukces całkowicie neguje atak potwora; przy pułapkach negacja lub połowa obrażeń).
  - *Save vs Spells / Charm / Fear* → test **DET** (dla grozy: test **DET** przeciw **przerażeniu** → Tabela Przerażenia k8).

---

## 5. Eksploracja lochów, podróże w dziczy, światło, pułapki i zasady OSR

- **Zachowaj sprawczość graczy OSR:** jeśli w oryginale gracz znajduje sekret/pułapkę bez rzutu dzięki dokładnemu opisowi — ZACHOWAJ TO (PG str. 34 wprost na to pozwala!). W przeciwnym razie test **SZUKANIA** (1 kwadrans).
- **Światło i brak infrawizji:** żaden grywalny ród w DB nie widzi w ciemności! Zamiast minut pochodni używaj kostki źródła światła rzucanej co Kwadrans: **świeca `k4`**, **pochodnia/kaganek `k6`**, **latarnia `k8`** (wynik `1` = gaśnie).
- **Światło słoneczne:** Nocarze (gobliny, hobgobliny, orki, ogry) w pełnym słońcu odnoszą k6 obr./Kwadrans i mają zgrzyt we wszystkich testach; Trolle tracą regenerację, odnoszą k6 obr./rundę i przy 0 WT zamieniają się w kamień.
- **Brak długiego odpoczynku w lochu:** w niebezpiecznych podziemiach nie można odbyć *Kwarty odpoczynku*; opuszczenie lochu uruchamia tabelę *Opuszczania strefy przygody* (k6: 1 tropienie/atak, 2 posiłki, 3 inni grabią skarb, 4–6 spokój). Zdarzenia losowe sprawdzaj co **Kwadrans** (w dziczy co **Kwartę**).
- **Pułapki a *Śmierć na miejscu*:** postacie w DB mają 10–18 WT, a cios schodzący do ujemnego maks. WT zabija natychmiast bez testów agonii! Kalibruj obrażenia pułapek na: lekkie `k6–k10`, standardowe `2k6–3k6`, śmiertelne `3k6–4k6` (+ ew. trucizna/dolegliwość), ZAWSZE zachowując wskazówki i dając ciężkozbrojnym w pułapkach fizycznych (głaz, podmuch) zamiennie test **KON/SIŁ** (bo kolczuga/płyta daje zgrzyt w UNIKACH).
- **Wyważanie przeszkód:** drewniane drzwi (Pancerz 3–5, 10–15 obr.), okute drzwi/skrzynia/kłódka (Pancerz 5–6, 20–25 obr.), żelazna krata (Pancerz 10, 30 obr.), masywna brama / drzwi-zagadka (Pancerz 12–25, 40–100 obr.) lub test **SIŁ**.
- **Inne pułapki adaptacji:** brak *Charakterów* (Alignment → konkretne typy: demony/nieumarli/nocarze lub frakcje); szlamy/kwas rób na wzór **Ogromnej ameby** (Best. str. 88: *Korozja* + *Kradzież* + *Wchłonięcie* ignorujące pancerz; trwałe niszczenie pancerza wyłącznie dla potworów jak Rdzawnik czy **Demon chaosu**, Best. str. 136); okaleczenia wyłącznie przez opcjonalne **Poważne urazy** (test KON po przeżyciu 0 WT).
- **Podróże na mapie dziczy (dopasowanie do skali mapy OSR):** baza z PG to **Podróż** (`PG str. 101`: `15 km/kwarta` pieszo, `30 km/kwarta` konno, maks. 2 kwarty/dzień lub 3 z **Wyczerpaniem**; *Przewodnik* testuje **PRZETRWANIE** co kwartę — bez mapy lub w trudnym terenie ze zgrzytem), **Tarapaty** i **Spotkania losowe** (`PG str. 102`: porażka Przewodnika → tabela k12; spotkanie raz na kwartę), **Obozowanie** i **Jedzenie na szlaku** (`PG str. 103`) oraz **Racje żywności / Głód** (`PG str. 54`: 1 racja/dzień). Procedurę zawsze dopasuj do realnej skali mapy modułu:

| Skala mapy OSR | Czas marszu / jednostka | Test **PRZETRWANIA** i spotkania losowe |
| --- | --- | --- |
| **Gęsta mapa lokalna / pointcrawl** *(1–5 km między punktami)* | Nie stosuj ślepo `15 km/kwarta`: licz przejścia w godzinach / blokach po `2–4 kwadranse` albo traktuj wyjście w dzicz jako 1 Kwartę eksploracji | **PRZETRWANIE** przy zejściu z traktu lub szukaniu ukrytych lokacji; spotkanie co `1–2 godz.` / przy zmianie strefy |
| **Małe heksy** *(1–3 mile / 1,5–5 km)* | Określ jasno liczbę heksów na Kwartę (trakt vs trudny teren) | Zdefiniuj częstotliwość testu **PRZETRWANIA** i spotkań (np. co Kwartę lub co określoną liczbę heksów) |
| **Klasyczne heksy 6-milowe** *(~10 km)* | `1 heks` w lesie/bezdrożach = `1 Kwarta` pieszo (po trakcie ~1,5 heksa, konno 2–3 heksy) | Standardowo: **PRZETRWANIE** i spotkanie losowe raz na Kwartę (`PG str. 101–102`) |
| **Skala regionalna** | Pełne zasady Podróży z `PG str. 101–103` bez zmian | Standardowo: Przewodnik, Tarapaty, Obozowanie i Racje (`PG str. 54, 101–103`) |

---

## 6. Ekonomia, skarby i przedmioty magiczne

Obowiązuje **standard srebra** (`1 złocisz [złoto] = 10 srebrników = 100 miedziaków`; `100–199 monet = ciężar 1`). W tekście przygody używaj kanonicznych nazw `złota / srebra / miedzi` (jak w PG). Ceny towarów i usług ZAWSZE bierz wprost z cennika *Dragonbane* (PG rozdz. 6: kolczuga 50 złota, płytówka 500 złota, eliksir zdrowia 50 złota, nocleg 1–5 srebra).

### Przelicznik skarbów B/X → Dragonbane (dobór dzielnika wg łącznej sumy `gp` w module)
Dobór dzielnika **nie zależy od poziomu modułu (*Basic* vs *Expert*)**, lecz od **łącznej sumy `gp` we wszystkich skarbach i nagrodach modułu**:

| Łączna suma `gp` w całym module | Dzielnik skarbów | Przelicznik bazowy |
| --- | --- | --- |
| **≤ 2 000 gp** | **1:10** | `1 gp → 1 srebro` *(0,1 złota; 10 gp → 1 złoto)* |
| **2 000–8 000 gp** | **1:20–1:25** | `20–25 gp → 1 złoto` *(1 gp → 4–5 miedzi)* |
| **8 000–30 000 gp** | **1:50** | `50 gp → 1 złoto` *(5 gp → 1 srebro; 1 gp → 2 miedzi)* |
| **> 30 000 gp** | **1:100** | `100 gp → 1 złoto` *(10 gp → 1 srebro; 1 gp → 1 miedź)* |

- **Test zdrowego rozsądku:** krótki loch powinien dawać łącznie ok. **50–150 złota** realnego łupu, a duży sandbox lub leże smoka ok. **200–500 złota**. Zawsze raportuj łączną sumę skarbów modułu w `conversion_map.md` do zatwierdzenia!
- **Klimat Obciążenia (OSR):** dla dużych kup monet wypłacaj wartość częściowo w **srebrze i miedzi** (`100–199 monet = ciężar 1`), aby zachować logistykę wynoszenia łupów z lochu. Przy dzielniku `1:10` obowiązuje schemat „Szczebel w dół”: `1 pp (5 gp) → 5 srebra`, `1 gp → 1 srebro`, `1 ep (0,5 gp) → 5 miedzi`, `1 sp → 1 miedź`, `1 cp → ÷10 miedzi lub graty`. Przy wyższych dzielnikach dziel wartości w `gp` przez wybrany dzielnik i zaokrąglaj do naturalnych kwot w złocie/srebrze.
- **Hybrydowe Karty Skarbów:**
  - W nowoczesnych modułach OSR **NIE zastępuj** ręcznie opisanych, klimatycznych skarbów autora losowymi kartami — przeliczaj je według powyższej tabeli dzielników (dobranej do łącznej sumy `gp` modułu)!
  - W klasycznych modułach B/X/AD&D generyczne wpisy typu *Treasure Type A–V* i anonimowe skrzynie zastępuj liczbą **Kart Skarbów** (1 karta mała skrytka / 2–3 mini-boss / 4–5 główny skarbiec), ale ZAWSZE zostawiaj i ręcznie konwertuj przedmioty kluczowe dla łamigłówek lochu (klucze, oliwa, broń magiczna przeciw konkretnemu potworowi, księgi czarów) oraz ciężkie skarby logistyczne.

### Przedmioty magiczne (ZAKAZ płaskich premii `+1/+2`!)
- **Broń magiczna `+1`:** **Broń mistrzowsko wykonana** (`SIŁ −2`, `Trwałość +3`, wartość ×10) + jest **magiczna** (omija odporności upiorów, widm, demonów, wilkołaków i istot baśniowych!) + opcjonalnie trwałe **ZAKLĘCIE ORĘŻA** potęgi 1 (*Smok* na `1–2`) lub drobna cecha fabularna (jak *Złobijca* w *Kopcu Witezia*).
- **Broń `+2/+3` / Pogromca (*Slayer/Bane*):** mistrzowsko wykonana + magiczna + **ZAKLĘCIE ORĘŻA** pot. 2–3 (*Smok* na `1–3/1–4`) LUB premia sytuacyjna przeciw 1 typowi istot (`+k6/+k8` obrażeń albo *błysk* przeciw smokom/nieumarłym/baśniowym).
- **Zbroja `+1`:** usuwa 1 zgrzyt (np. kolczuga bez zgrzytu w UNIKACH, jak *Pozłacana kolczuga* w *Kopcu Witezia*) albo daje `+1` Pancerza (maks. 7).
- **Mikstury:** *Potion of Healing* → **Eliksir zdrowia** (`2k6` WT, 50 złota). Inne mikstury → działanie czaru lub błysk na Kwadrans/Kwartę.
- **Zwoje i różdżki:** **Księga czarów** (nauka testem **JĘZYKÓW OBCYCH**) LUB przedmiot z **UMAGICZNIENIEM + NAŁADOWANIEM** (PG str. 62):
  - *Jednorazowy zwój:* **UMAGICZNIENIE** (znika po 1 użyciu) + utrwalone **NAŁADOWANIE** (by SW nie ulotniła się po 1 kwarcie).
  - *Wielorazowa różdżka:* utrwalone **UMAGICZNIENIE** + utrwalone **NAŁADOWANIE** (określona pula SW; po wyczerpaniu pęka/gaśnie lub wymaga ponownego **NAŁADOWANIA**).

---

## 7. Formaty bloków statystyk (z ochroną układu 1:1)

- **Inline PN (2–4 linijki, mieści się w tekście pokoju):**
  `**Nazwa PN:** Szybkość 10 | Mod. obr. SIŁ: +k4 | WT: 14 | Pancerz: 2 (ćwiekowana) | Umiejętności: Czujność 10, Skradanie 12, Uniki 10 | Broń: Miecz jednoręczny (12, 2k6). *Taktyka: uciekają, gdy padnie połowa.*` *(Dla Figur dopisz SW, Zdolności heroiczne i Czary; dla broni opartej na ZRC podaj `Mod. obr. ZRC`).*
- **Inline Zwykłe Zwierzę:**
  `**Olbrzymi szczur:** Szybkość 12 | WT: 5 | Atak: Kły (10, k6 + choroba zjadl. 10) | Umiejętności: Czujność 12, Skradanie 14, Uniki 12.`
- **Inline odsyłacz do Potwora (chroni strony przed rozlaniem!):**
  - Oficjalny z podręczników: `**Upiór** (*PG str. 97*; WT 38, Panc. 4 [kolcza], Zajadłość 2)` *(+ ew. lokalna modyfikacja)*.
  - Nowy potwór modułu: `**Nazwa Potwora** (*Dodatek: Bestiariusz, str. XX*; Zajadłość 2, Duży, Szyb. 24, Panc. 4, WT 60)`.
- **Pełna karta Nowego Potwora (do *Dodatku: Bestiariusz modułu*):** nagłówek, 1–2 zdania opisu, pasek parametrów (`Zajadłość, Rozmiar, Szybkość, Pancerz, WT`), Cechy specjalne (w tym **`Perswazja`**, jeśli dotyczy!), tabela `K6 | ATAK` z 6 zróżnicowanymi taktycznie atakami (pogrubiona nazwa z wykrzyknikiem, 1–2 ataki z dopiskiem *Atak można sparować*, 1 obszarowy, 1 kontrolujący/obalający, 1 przerażenie/dolegliwość, 1 unikalny atak z oryginału).

---

## 8. Checklista Audytu QA (Etap 4)

Przed zamknięciem modułu zweryfikuj KAŻDY punkt:
- [ ] Zero resztek OSR: żadnych `d4/d6/d20`, `ft`, `mil`, `AC`, `HD`, `HP`, `XP`, `lvl`, `ML`, `MV`, `TT`, `THAC0`, `Save vs...`, charakterów (*Lawful/Chaotic*), `gp/sp/cp/ep/pp`.
- [ ] Wszystkie umiejętności pochodzą ściśle z listy 30 umiejętności + 3 szkół magii; w tekście przygody są zapisane **WIELKIMI LITERAMI I POGRUBIONE**, a w blokach statystyk PN/zwierząt normalnie (jak w PG, np. `Czujność 10`).
- [ ] Wszystkie dolegliwości należą do kanonicznej szóstki (**Wyczerpanie, Niemoc, Zamęt, Złość, Strach, Zniechęcenie**).
- [ ] Zero mylenia **DET** z **SW** (wszystkie testy strachu, petryfikacji, uroków, woli = **DET**).
- [ ] Zero liczbowych modyfikatorów do rzutów k20 (tylko **z błyskiem / ze zgrzytem**).
- [ ] Żaden Potwór nie rzuca na trafienie; inteligentnym/baśniowym potworom dodano cechę **Perswazja**; opancerzeni klerycy/elfy uwzględniają zasadę **Metal zaburza magię** (PG str. 58).
- [ ] Zero broni/zbroi `+1/+2`; magiczna broń z oryginału zachowuje cechę *magiczna* tam, gdzie wymaga tego ekologia lochu.
- [ ] Wszystkie odsyłacze do `PG str.` / `Best. str.` podają **drukowane** numery stron (`STRONA X - 2`), a odsyłacze do Dodatku zgadzają się z finalną paginacją.
- [ ] Nazwy własne w całym dokumencie są w 100% zgodne z zatwierdzonym `glossary.md`.

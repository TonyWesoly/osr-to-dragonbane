# Tłumaczenie OSR, tryby DTP i Doradca Druku

## 1. Tłumaczenie i wierność intencji autora
- **Styl użytkowy OSR:** oddawaj rytm, zwięzłość i klimat konkretnego autora. Moduł OSR to narzędzie do szybkiego skanowania wzrokiem podczas sesji — nie dopisuj zbędnej „waty słownej”.
- **Naturalna polszczyzna:** wzoruj się na polskim przekładzie *Dragonbane* (T. Z. Majkowski: *Kopiec Witezia*, *Tonąca Wieża*). Unikaj kalek (*„przetestuj **SZUKANIE**”*, *„odnosi 2k6 obrażeń ciętych”*, *„ogarnia ją Strach”* zamiast *„wykonaj rzut...”*).
- **Rymowanki, inskrypcje i zagadki:** tłumacz twórczo z zachowaniem logiki wskazówek (zapisuj w `glossary.md`).
- **Korekta końcowa:** w Etapie 4 przeczytaj gotowy polski tekst **bez patrzenia na angielski oryginał**, aby wyłapać sztuczny szyk zdań.

## 2. Tryby DTP, mikroformatowanie i układ stron
- **Trzy tryby DTP (dobierane na Bramce #1 według mierzalnej jakości graficznej i ergonomii oryginału):**
  - **Tryb 1 — Wierny 1:1:** gdy oryginał ma już dopracowany, czytelny skład, spójną typografię i wyraźną hierarchię wizualną.
  - **Tryb 2 — Remaster DTP (paginacja 1:1):** gdy podział treści na strony ma sens, ale oprawa graficzna jest surowa lub prosta (np. płaskie szare bloki, słaba separacja nagłówków, brak marginesów grzbietowych lub brak tylnej okładki) — zachowujemy 1:1 treść stron, mapy i ilustracje, ale podnosimy typografię, ramki, tabele, hierarchię „control-panel” i tylną okładkę do poziomu wydawniczego w klimacie oryginału.
  - **Tryb 3 — Pełny Re-layout pod booklet:** gdy oryginał jest nieczytelny lub źle przystosowany do broszury (np. skrajnie ciasne wielokolumnowe rozkładówki, zgniecione/nieczytelne fonty, tekst nachodzący na grafiki, jednostronicowe lochy lub ulotki) — świadomie rezygnujemy z układu 1:1 i projektujemy wygodny, wielostronicowy booklet A5/A4 (wielokrotność 4), zachowując oryginalne ilustracje, mapy oraz klimat/paletę oryginału, ale zapewniając pełną czytelność przy stole.
- **Docelowy format strony w CSS `@page`:** od razu projektuj pod docelowy format europejski (**A5 `148×210 mm`** lub **A4 `210×297 mm`**) zamiast ślepo kopiować amerykańskie wymiary z PDF-a (np. US Digest `140×216 mm` jest o 6 mm wyższy niż A5 i nie zmieści się 2-up na arkuszu A4 w skali 100%!).
- **Mikroformatowanie autora (nie narzucaj układu z *Kopca Witezia*):** zachowuj oryginalne pogrubienia słów-kluczy, kursywy, zagnieżdżone listy, wcięcia oraz sposób wyrównania (justowanie tam, gdzie oryginał justuje; wyrównanie do lewej w wąskich kolumnach i listach). W Trybie 1 odtwarzaj 1:1 również tabele, ramki i kolumny; w Trybach 2–3 rozwijaj je według projektu zatwierdzonego na Bramce #2.
- **Polska typografia i dobór fontów:**
  - `<html lang="pl">` oraz włączone polskie dzielenie wyrazów (`hyphens: auto`), szczególnie w akapitach wyjustowanych.
  - Automatyczne twarde spacje (`&nbsp;`) oraz zamiana `...` na wielokropek (`…`) wstawiane **wyłącznie w węzłach tekstowych DOM** (`BeautifulSoup`/`lxml` — nigdy surowym regexem po kodzie HTML/CSS!) po polskich spójnikach jednoliterowych (`a, i, o, u, w, z, A, I, O, U, W, Z`), po `str.` oraz przed jednostkami i walutami (`m, km, WT, SW, złota, srebra, miedzi, zł`).
  - Polskie cudzysłowy `„...”`, półpauzy `–` (ze spacjami w wtrąceniach, bez spacji w zakresach `1–3`) oraz wielokropek `…`.
  - **Lokalne fonty w `reference/fonts/` + `@font-face`:** na podstawie `metrics.json` **najpierw sprawdź zweryfikowane kroje już obecne w `reference/fonts/`**; pobieraj nowe darmowe fonty (np. z Google Fonts / GitHuba) dopiero wtedy, gdy charakter, szerokość i klimat kolejnego modułu wymagają innego kroju. Dla każdego nowo pobieranego fontu **zawsze weryfikuj programowo (`fontTools`) komplet 18 polskich znaków** (`ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż`).
  - **Wielkie litery po dwukropku i polska ortografia podtytułów:** w hasłach punktowanych i opisach o strukturze **Etykieta:** treść (niezależnie od użytego w oryginale punktora, w tym w ramkach i blokach statystyk) zaczynaj zdanie po dwukropku **wielką literą** (np. **Reakcja:** Gdy postać wejdzie…, **Zamek:** Otwierany testem **ZWINNYCH PALCÓW**). W podtytułach i nagłówkach sekcji stosuj polską ortografię — bez angielskiego *Title Case* (wielką literą wyłącznie pierwsze słowo i nazwy własne).
- **Kontrola przepełnień:** nie ukrywaj przepełnienia przez `overflow: hidden` podczas budowania i Visual QA — przepełniona `.page` musi być jawnie wykrywana przez skrypt budujący (`--strict`).
- **Ochrona stron przed statblokami Dragonbane:** PN i zwierzęta wstawiaj kompaktowo inline (2–4 linijki); oficjalne potwory jako krótki odsyłacz z drukowaną stroną (`PG str. X` / `Best. str. Y`); nowe potwory (jeśli występują) jako 2-linijkowy pasek parametrów inline + pełna tabela `k6` w **Dodatku: Bestiariusz modułu**.
- **Radzenie sobie z puchnięciem polskiego tekstu (+15–25%):**
  Jeśli strona przelewa się w Visual QA, kieruj się rozsądnym priorytetem:
  1. Najpierw skondensuj zbyt rozwlekłą polszczyznę (bez utraty żadnej informacji!) i upewnij się, że żaden nowy potwór `k6` nie rozpycha pokoju.
  2. Następnie zastosuj delikatne, estetyczne korekty układu (dzielenie wyrazów, mikro-odstępy akapitów/ramek lub minimalna korekta skali ilustracji), oceniając efekt wzrokiem na lekkim podglądzie RGB JPEG (zgodnie z `GEMINI.md`).
  3. Jeśli wymaga tego cały moduł, skoryguj bazowy stopień pisma **jednolicie w całej książce** (NIGDY nie rób „jednej strony maczkiem”!).
  4. Jeśli czcionka główna musiałaby spaść poniżej `8,0 pt` (dla A5) lub `8,5 pt` (dla A4), nie ściskaj jej na siłę — zaprojektuj czytelny skład pod większy format druku.

## 3. Mapy, Dodatek i parzystość bookletu
- **Mapy wektorowe:** gdy mapa nie jest obrazkiem rastrowym, wytnij ją ze strony PDF przez `bbox` w 300–600 DPI (wyłącznie do osadzenia w PDF). Napisy angielskie obsługuj zgodnie z wyborem z Bramki #1 (czysta mapa + polska legenda albo przykrycie i polskie napisy w CSS `position: absolute`).
- **Parzystość stron, warunkowy Dodatek i okładki:**
  - W Trybach 1–2 zachowaj oryginalny układ lewych (parzystych) i prawych (nieparzystych) stron (w Trybie 3 projektuj rozkładówki od zera pod wielokrotność 4).
  - **Warunkowy *Dodatek: Bestiariusz modułu*:** dodawaj go tylko wtedy, gdy moduł zawiera nowe potwory z tabelami `k6` (nie wymuszaj go na siłę w prostych modułach opartych wyłącznie o PN, zwierzęta lub oficjalne wpisy z PG/Best.).
  - Ewentualny *Dodatek* oraz strony wyrównujące całość do **wielokrotności 4** wstawiaj **PRZED wewnętrzną tylną okładką** (jeśli ma mapę/tabelę okładkową) albo tuż przed tylną okładką — zawsze w **parzystej** liczbie stron, aby wewnętrzna tylna okładka pozostała stroną nieparzystą/prawą (`N−1`), a tylna okładka parzystą/lewą (`N`).
  - **Zakaz elementów jednorazowych do pisania po książeczce:** NIE umieszczaj w module pustych pól na notatki, kratek do zakreślania ani torów czasu do mazania ołówkiem. Strony wyrównujące do wielokrotności 4 wypełniaj wyłącznie **wielorazowymi pomocami dla MG przy stole**: zbiorczymi tabelami zdarzeń losowych ze wszystkich stref, ściągawką procedur *Dragonbane* (odpoczynek, dolegliwości, światło, ekonomia — a w modułach z mapą dziczy także **ramką „Procedura podróży na mapie”**: czas marszu na heks/odcinek, kiedy test **PRZETRWANIA**, częstotliwość spotkań losowych i odsyłacze do PG), indeksem przeciwników/skarbów/zagadek lub czystą mapą dla graczy.

## 4. Strategia kolorystyczna i warunkowa wersja czarno-biała (`--bw` + `style_bw.css`)
- **Dobór strategii i kiedy generować wariant `--bw`:**
  - **Moduły kolorowe:** zachowaj paletę oryginału, a w Etapie 4 generuj równolegle wysokokontrastowy wariant B&W (`<slug>_reading_bw.pdf`, `<slug>_booklet_bw.pdf`, identyczna paginacja) bez duplikowania HTML przez `scripts/build_pdf.py work/pages/ --bw --strict`.
  - **Moduły w 100% czarno-białe (brak kolorów referencyjnych):** nie dokładaj losowych kolorów na siłę — zamiast tego na **Bramce #1** zaproponuj wybór między:
    - **(a) Eleganckim remasterem czysto B&W:** wysoki kontrast w `style.css`, białe ramki, wyraźne czarne akcenty, bez dublowania plików `_bw.pdf`;
    - **(b) Stylem duotone:** czerń + 1 stonowany kolor akcentu dobrany tematycznie do klimatu modułu w `style.css` + równoległy wariant `--bw` (`_bw.pdf`).
  - **Kolorowa wyłącznie okładka (środek B&W):** generuj `_bw.pdf` tylko wtedy, gdy realnie poprawia czytelność lub oszczędność tonera.
- **Optymalizacja grafik (`work/assets_bw/`):** `build_pdf.py --bw` konwertuje kolorowe ilustracje do skali szarości z rozjaśnieniem cieni pod druk laserowy, wzmocnieniem kontrastu i ochroną czystej bieli winiet, zachowując ostrość map kreskowych i neutralizując kolory w inline SVG.
- **Uniwersalne zasady kontrastu dla `work/style_bw.css`:**
  - **Tekst, nagłówki i linie:** głęboka czerń (`#111`) zamiast bladych szarości; w kolorowych lub ciemnych belkach i nagłówkach sekcji dobierz jasne tło z ciemną linią/tekstem (lub wysoki kontrast negatywowy), aby napisy pozostały ostre na drukarce laserowej.
  - **Ramki, statbloki i tabele:** ramki informacyjne i statbloki na **czystym białym tle** z wyrazistym ciemnym obramowaniem (bez szarych teł/rastrów za tekstem); tabele z wysokim kontrastem nagłówków i subtelnym pasowaniem wierszy.
  - **Mapy i oznaczenia:** wyraźny, wysokokontrastowy rozdział numerów i znaczników od rysunku oraz kreskowania mapy (np. ciemny znacznik z białym opisem i jasną obwódką lub kontrast odwrotny, dobrany do stylu mapy).
  - **Okładki i ciemne ilustracje:** przy okładkach i stronach z ciężkim ciemnym tłem lub ilustracjami o głębokich cieniach zapewnij czytelność tytułu oraz oszczędny dla tonera kontrast (np. jasne tło z subtelną ramką i czarnym tekstem zamiast jasnych liter na ciemnej apli).
- **Visual QA B&W:** skontroluj na lekkich podglądach RGB JPEG (wg `GEMINI.md`) kluczowe strony: okładki, mapę, rozkładówkę z ilustracją oraz statbloki/kartę potwora.

## 5. Algorytm Doradcy Druku (`modules/<slug>/output/print_guide.md`)
Na koniec każdego modułu wygeneruj zwięzły raport z 5 elementami:
1. **Metryki:** wymiary oryginału (mm) vs wersja PL (mm), wybrany tryb DTP, finalna liczba stron (podzielna przez 4), faktyczny rozmiar fontu głównego i tabel w `pt` (zmierzony z finalnego PDF przez `impose_booklet.py inspect`) oraz potwierdzenie identycznej paginacji wersji kolorowej/duotone i B&W *(jeśli wygenerowano wariant B&W)*.
2. **Jednoznaczna rekomendacja formatu:**
   - **Booklet A5 (druk na A4 poziomo, złożony na pół):** domyślny wybór, gdy oryginał to A5 / US Digest, czcionka główna ma **≥ 8,0 pt** *(optymalnie ≥ 8,5 pt; przy 8,0–8,4 pt zaznacz, że skład jest zwarty)*, tabele **≥ 7,5 pt**, a objętość wynosi **≤ 64 str.**
   - **Booklet A4 (druk na A3 poziomo, złożony na pół — punkt druku):** zalecaj, gdy oryginał to gęsty A4 / US Letter (zmniejszenie na A5 zabija czytelność!) LUB gdy moduł A5 wymagał zejścia z fontem głównym poniżej **8,0 pt**.
   - **Alternatywa na domową drukarkę A4** (gdy zalecane jest A3 lub > 64 str.): druk dwustronny 1:1 z `<slug>_reading.pdf` (lub `<slug>_reading_bw.pdf`, jeśli dotyczy) z zachowaniem rozkładówek do wpięcia w skoroszyt albo podział na 2 cieńsze booklety.
3. **Warianty kosztowe druku (dopasowane do kolorystyki modułu, z nazwami plików i numerami stron bookletu):**
   - **Moduły kolorowe i styl duotone (3 warianty):**
     - **Wariant A — Pełny kolor:** cały booklet z `<slug>_booklet.pdf` (najwyższa wierność artystyczna, najwyższy koszt).
     - **Wariant B — Hybrydowy (okładka kolor + środek B&W — optymalny koszt/efekt):** arkusz 1 (str. 1–2 `<slug>_booklet.pdf`, 200–250 g/m²) w kolorze + arkusze 2–N (str. 3–2N `<slug>_booklet_bw.pdf`, 90–100 g/m²) w wysokokontrastowym B&W.
     - **Wariant C — Pełne B&W:** cały booklet z `<slug>_booklet_bw.pdf` (najniższy koszt w punkcie druku i idealny na drukarkę laserową).
   - **Moduły czysto B&W / z kolorową wyłącznie okładką:** przy wariancie czysto B&W podaj pojedynczy wariant (`<slug>_booklet.pdf`); przy kolorowej wyłącznie okładce — wariant hybrydowy (arkusz 1 w kolorze + środek B&W) oraz pełne B&W.
4. **Parametry fizyczne i marginesy:**
   - Booklet A5 (arkusz A4): strona `148×210 mm`, margines wewnętrzny (grzbiet) min. `12–14 mm`, zewnętrzny `10–12 mm`, papier środek `90–100 g/m²` matowy, okładka `200–250 g/m²` (z bigowaniem).
   - Booklet A4 (arkusz A3): strona `210×297 mm`, grzbiet min. `15–18 mm`, zewnętrzny `12–15 mm`, papier środek `100 g/m²`, okładka `200–250 g/m²`.
   - Druk domowy bez spadu: bezpieczny margines min. `8–10 mm` na białym tle.
   - Punkt druku przy grafice do krawędzi: `bleed: 3mm` wymaga wydruku na arkuszu z naddatkiem (**SRA4** dla A5 lub **SRA3** dla A4) i przycięcia z 3 stron na gilotynie (przy grubych zeszytach ≥ 32 str. dodatkowo prośba o korektę wypychania / obcinanie czoła).
5. **Ustawienia drukarki dla plików bookletu (`<slug>_booklet.pdf` oraz ew. `<slug>_booklet_bw.pdf`):** orientacja **Pozioma (Landscape)**, dwustronnie z **obrotem wzdłuż krótszej krawędzi (*Flip on short edge*)**, skala **100% / Rozmiar faktyczny**.

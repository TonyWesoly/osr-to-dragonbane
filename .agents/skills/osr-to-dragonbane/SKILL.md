---
name: osr-to-dragonbane
description: Tłumaczy moduły OSR z PDF na polski, konwertuje mechanikę na polską edycję Dragonbane (Black Monk Games), składa strony w modularnym HTML/CSS (1:1, Remaster DTP lub Re-layout pod booklet) z wizualną kontrolą na lekkich RGB JPEG (< 1 MB) oraz przygotowuje booklet do druku wraz z raportem Doradcy Druku.
---

# Elastyczna procedura konwersji OSR → Dragonbane PL

Ładuj pliki z `.agents/skills/osr-to-dragonbane/references/` wtedy, gdy są potrzebne:
- `references/01_mechanika_dragonbane_pl.md` — przy projektowaniu konwersji, statystyk, skarbów i audycie QA.
- `references/02_tlumaczenie_dtp_i_druk.md` — przy stylu tłumaczenia, typografii, składzie HTML/CSS, wariancie B&W i raporcie druku.

Wszystkie podglądy Visual QA generuj i otwieraj wyłącznie jako lekkie RGB JPEG zgodnie z niezmiennikiem z `GEMINI.md`.

---

## Gotowe narzędzia i zasoby (`.venv/bin/python scripts/`)
W `reference/` znajdują się już oczyszczone spisy treści (`podrecznik_glowny_spis.md`, `bestiariusz_spis.md`), wzorce (`style_samples/`) i zweryfikowane polskie fonty (`fonts/`). Do pracy służą gotowe narzędzia:
- **`scripts/extract_pdf.py`** (`extract`, `crop`) — metryki stron w mm, lekkie podglądy `pages_jpg/`, ekstrakcja stylizowanego tekstu i obrazów rastrowych oraz wycinanie map wektorowych przez `bbox` (300–600 DPI do PDF).
- **`scripts/lookup_db.py`** — punktowe wyszukiwanie w `reference/` z automatycznym przeliczeniem stron (`STRONA X - 2`; zakres treści merytorycznej: `podrecznik_glowny.md` do `STRONA 114` [bez indeksu `115`], `bestiariusz.md` do `STRONA 149` [bez indeksu `150` i reklam `151–155`]; opcjonalnie `--include-adventures`).
- **`scripts/build_pdf.py`** — skład HTML+CSS → PDF (`WeasyPrint` + `pyphen`) z pojedynczego pliku lub `work/pages/` (`--pages`), automatyczna polska typografia, wykrywanie przepełnień `.page` (`--strict`), tryb `--bw` (`work/style_bw.css` + `work/assets_bw/` bez duplikowania HTML) oraz podglądy/porównania JPEG (`--preview-dir`, `--compare-dir`, `--diff-dir`).
- **`scripts/impose_booklet.py`** (`impose`, `inspect`) — impozycja zeszytowa (wielokrotność 4, ochrona okładek) oraz pomiar realnych rozmiarów fontów w `pt` w finalnym PDF.

---

## Przekazywanie stanu między czatami (`modules/<slug>/work/PROGRESS.md`)
- **Start / wznowienie:** przy krótkim poleceniu typu `Rozpocznij moduł <slug>` lub `Kontynuuj moduł <slug>` najpierw sprawdź `modules/<slug>/work/PROGRESS.md`. Jeśli plik istnieje, od razu płynnie zrealizuj wskazany `Następny krok:` według poniższej procedury (bez ponownego pytania o wcześniejsze ustalenia); jeśli nie istnieje, zacznij od Etapu 1.
- **Automatyczna aktualizacja:** na końcu każdego etapu, po zatwierdzeniu Bramki #1/#2 oraz po każdej ukończonej partii Etapu 3 zaktualizuj krótki plik `modules/<slug>/work/PROGRESS.md`, zapisując: status bramek i etapów, zatwierdzone decyzje (tryb DTP i kolorystyka, fonty, dzielnik skarbów, podejście do map), listę gotowych plików `work/pages/pXX.html` oraz jedną linijkę `Następny krok: ...`.

---

## Etap 1: Ekstrakcja, Słownik i Mapa Konwersji → 🛑 BRAMKA AKCEPTACJI #1
Dla modułu w `modules/<slug>/input/`:
1. Wyekstrahuj zasoby, podglądy `pages_jpg/` i strukturę tekstu przez `scripts/extract_pdf.py` do `modules/<slug>/work/`. **Uwaga na fonty stylizowane/zagęszczone lub brak pełnej warstwy tekstowej:** gdy ekstrakcja/OCR potrafi pomylić znaki (np. `1d6` z `106`), weryfikuj wartości kości, liczb i nazw własnych wzrokiem na lekkich podglądach `pages_jpg/`.
2. Wczytaj `references/01_mechanika_dragonbane_pl.md` (oraz kryteria trybów DTP i modułów B&W z `references/02_tlumaczenie_dtp_i_druk.md`, sekcje 2 i 4) i przygotuj w `modules/<slug>/work/` zwięzły pakiet decyzyjny:
   - `analysis.md` — wymiary stron oryginału (mm), docelowy format europejski (A5 `148×210 mm` vs A4 `210×297 mm`), liczba stron, układ okładek/map, **ocena jakości graficznej i ergonomii oryginału** wraz z rekomendacją trybu DTP (**Tryb 1 / Tryb 2 / Tryb 3**; przy surowym lub nieczytelnym składzie przedstaw 1–2 krótkie propozycje koncepcji), **profil kolorystyczny** (kolorowy vs w 100% B&W — dla w pełni B&W zaproponuj wybór między czystym remasterem B&W a stylem duotone + `--bw`) oraz propozycja obsługi angielskich napisów na mapach (czysta mapa + legenda vs polskie etykiety w CSS).
   - `glossary.md` — polski tytuł, nazwy własne (lokacje, PN, frakcje, artefakty, zagadki) i ton autora.
   - `conversion_map.md` — lista przeciwników (podział: `[PN inline]`, `[Gotowy z PG/Best. + drukowany nr strony]`, `[Nowy potwór → skrót inline + tabela k6 w Dodatku]`), pułapek, czarów, przedmiotów magicznych, **łączne zestawienie skarbów po przeliczeniu** oraz — jeśli moduł zawiera mapę dziczy, heksy lub pointcrawl — proponowana **procedura podróży dopasowana do skali mapy** do zatwierdzenia na Bramce #1.
3. **Zatrzymaj się** i poproś użytkownika o zatwierdzenie pakietu, wybór podejścia do map oraz — gdy oryginał ma surowy/nieczytelny skład lub jest w 100% B&W — wybór **trybu DTP** i **strategii kolorystycznej**.

---

## Etap 2: Szablon CSS i próbna rozkładówka → 🛑 BRAMKA AKCEPTACJI #2
Wczytaj `references/02_tlumaczenie_dtp_i_druk.md`.
1. Obejrzyj kluczowe podglądy `pages_jpg/` oryginału. Sprawdź najpierw zweryfikowane fonty już obecne w `reference/fonts/` (nowe pobieraj tylko, gdy charakter modułu wymaga innego kroju) i przygotuj `modules/<slug>/work/style.css` zgodnie z trybem DTP i strategią kolorystyczną zatwierdzonymi na Bramce #1 (format strony pod booklet, kolumny, kolory, ramki, bezpieczne marginesy grzbietowe).
2. Przetłumacz i złóż **jedną typową rozkładówkę (2 strony)** (`sample_spread.html`), wyrenderuj lekkie podglądy RGB JPEG i pokaż użytkownikowi na **Bramce #2** do akceptacji wyglądu oraz stylu przekładu przed składaniem reszty zeszytu. W **Trybie 2 (Remaster DTP)** lub **Trybie 3 (Pełny Re-layout)** przedstaw tę rozkładówkę jako **projekt wizualny** z krótkim uzasadnieniem wyborów graficznych.

---

## Etap 3: Tłumaczenie, skład i Visual QA (modularnie, partiami po 8–12 stron na czat)
1. **Modularna struktura stron (`work/pages/`):** zapisuj każdą stronę zeszytu w osobnym pliku `modules/<slug>/work/pages/p01.html`, `p02.html`, … (numeracja stron PDF 1..N; przenieś tam również zatwierdzone strony z `sample_spread.html`).
2. **Podział na czaty (ochrona limitu mediów i jakości przekładu):** realizuj Etap 3 w partiach po **8–12 stron na jeden czat** (wewnątrz czatu składaj i sprawdzaj po 1–2 rozkładówki lub 3–4 strony graficzne/mapowe). Po zakończeniu bieżącej partii zaktualizuj `PROGRESS.md` i **zatrzymaj się z krótkim statusem postępu**, aby kolejną partię uruchomić w nowym czacie.
3. **Kontrola przepełnień i Visual QA:** po każdej porcji buduj PDF przez `scripts/build_pdf.py work/pages/ --strict` i sprawdzaj wizualnie każdą wygenerowaną stronę na podglądach JPEG (`compare_*.jpg` w Trybach 1–2 / `page_*.jpg` w Trybie 3), pilnując zgodności z wybranym trybem DTP, mikroformatowania i 0 przepełnień.
4. **Warunkowy Dodatek i wyrównanie do wielokrotności 4:** złóż **Dodatek: Bestiariusz modułu** (wzorowany na `reference/style_samples/`) tylko wtedy, gdy moduł zawiera nowe potwory z tabelami `k6`; nie dodawaj go na siłę w prostych modułach bez nowych potworów. Jeśli objętość wymaga wyrównania do wielokrotności 4, dołóż wielorazowe pomoce MG (bez elementów jednorazowych do pisania — szczegóły w `references/02_tlumaczenie_dtp_i_druk.md`), wstawiając dodane strony w parzystej liczbie **przed wewnętrzną tylną okładką**.

---

## Etap 4: Redakcja, Audyt QA, Wariant B&W, Booklet i Raport Druku (osobny czat)
> **Zasada higieny kontekstu:** Etap 4 uruchamiaj w **osobnym, świeżym czacie** po zakończeniu wszystkich plików w `work/pages/`.

1. **Przebieg redakcyjny:** przejrzyj cały polski tekst bez patrzenia na angielski oryginał, usuwając kalki i szlifując płynność oraz zwięzłość użytkową przy stole.
2. **Warunkowy wariant czarno-biały (`--bw`):** dla **modułów kolorowych i wariantu duotone** przygotuj `modules/<slug>/work/style_bw.css` (zasady w `references/02_tlumaczenie_dtp_i_druk.md`, sekcja 4) i zbuduj wariant B&W z `work/pages/`. Dla **modułów czysto B&W** nie duplikuj plików `_bw.pdf`.
3. **Audyt QA i Visual QA:** sprawdź całość z *Checklistą Audytu QA* (`references/01_mechanika_dragonbane_pl.md`, sekcja 8), wykonaj pełny build (`build_pdf.py work/pages/ --strict` oraz `--bw --strict`, jeśli dotyczy — z 0 przepełnień i identyczną paginacją wersji głównej oraz B&W) i skontroluj kluczowe strony wariantu B&W na podglądach JPEG.
4. **Finalne pliki w `modules/<slug>/output/`:**
   - `<slug>_reading.pdf` — wersja główna 1-up (ekran/tablet i kontrola),
   - `<slug>_booklet.pdf` — gotowa impozycja zeszytowa (`scripts/impose_booklet.py`),
   - `<slug>_reading_bw.pdf` i `<slug>_booklet_bw.pdf` — wysokokontrastowy wariant B&W o identycznej paginacji *(dla modułów kolorowych i wariantu duotone; przy czystym B&W nie duplikuj)*,
   - `print_guide.md` — raport Doradcy Druku wg sekcji 5 pliku `references/02_tlumaczenie_dtp_i_druk.md` (format, realny rozmiar czcionki w `pt`, dobór papieru, ustawienia drukarki i warianty kosztowe dopasowane do kolorystyki modułu).
5. Przedstaw użytkownikowi krótkie podsumowanie audytu QA oraz rekomendację z `print_guide.md`.

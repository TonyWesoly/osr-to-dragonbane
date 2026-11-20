# Warsztat: Tłumaczenie i konwersja modułów OSR na Dragonbane (PL)

Jesteś tłumaczem literackim RPG, projektantem mechaniki polskiej edycji **Dragonbane** (Black Monk Games, przekład T. Z. Majkowskiego) oraz inżynierem DTP. Przekształcasz PDF-y modułów OSR w gotowe do druku (w formie bookletu) polskie wersje na mechanice *Dragonbane*, domyślnie zachowując **układ stron 1:1** oraz oryginalne mikroformatowanie autora.

## Struktura katalogów projektu
- `.agents/skills/osr-to-dragonbane/` — procedura (`SKILL.md`) i wytyczne konwersji/DTP (`references/`).
- `reference/` — podręczniki referencyjne *Dragonbane PL* (`podrecznik_glowny.md`, `podrecznik_glowny_spis.md`, `bestiariusz.md`, `bestiariusz_spis.md`, `style_samples/`, `fonts/`).
- `scripts/` — gotowe narzędzia Pythona (`.venv`): `extract_pdf.py`, `lookup_db.py`, `build_pdf.py`, `impose_booklet.py`.
- `modules/<slug>/input/` — oryginalny PDF modułu OSR.
- `modules/<slug>/work/` — pliki robocze, wyekstrahowane zasoby, lekkie podglądy JPEG (`pages_jpg/`), modularne strony (`pages/p01.html…`), `style.css`, słownik, mapa konwersji oraz `PROGRESS.md` (przekazywanie stanu między czatami).
- `modules/<slug>/output/` — finalne PDF-y (`reading`, `booklet`) oraz `print_guide.md`.

## Procedura i materiały referencyjne
- Postępuj według `.agents/skills/osr-to-dragonbane/SKILL.md`.
- **Ochrona limitów i kontekstu:** NIGDY nie wczytuj w całości `reference/podrecznik_glowny.md` ani `reference/bestiariusz.md`. Przeszukuj je wyłącznie punktowo (`scripts/lookup_db.py` / grep / spisy treści).
- **Przesunięcie numeracji stron:** w obu plikach (`podrecznik_glowny.md` i `bestiariusz.md`) nagłówki `## STRONA X` są spójnie przesunięte o **+2** względem numerów drukowanych (`druk. str. = X - 2`; oba spisy treści podają już oba numery). W odsyłaczach dla MG (np. *PG str. 97*, *Best. str. 114*) ZAWSZE podawaj **drukowany** numer strony.

## Twarde niezmienniki (zawsze obowiązują)
1. **Oficjalna terminologia Dragonbane PL:** polskie kości (`k3–k20`), metry, `runda / kwadrans / kwarta`, wyłącznie modyfikatory **z błyskiem / ze zgrzytem**, 6 cech (`SIŁ, KON, ZRC, INT, DET, CHA` — nigdy `SW` jako cecha!) i 6 dolegliwości (`Wyczerpanie, Niemoc, Zamęt, Złość, Strach, Zniechęcenie`).
2. **Skład od nowa w HTML+CSS → PDF:** nigdy nie nadpisuj tekstu bezpośrednio w oryginalnym PDF-ie. Domyślnie każda strona odpowiada 1:1 oryginałowi i zachowuje jego pogrubienia, kursywy, wcięcia i justowanie; **furtka DTP:** przy surowym lub nieczytelnym oryginale dopuszczalny jest **Tryb 2 (Remaster DTP 1:1)** lub **Tryb 3 (Pełny Re-layout pod booklet)** — wyłącznie po wyborze użytkownika na Bramce #1 i akceptacji projektu wizualnego na Bramce #2 (definicje: `.agents/skills/osr-to-dragonbane/references/02_tlumaczenie_dtp_i_druk.md`).
3. **Ochrona rozkładówek i okładek:** w trybach z paginacją 1:1 zachowuj parzystość stron oryginału. Ewentualny *Dodatek: Bestiariusz modułu* i strony wyrównujące do wielokrotności 4 wstawiaj (zawsze w parzystej liczbie stron) **przed wewnętrzną tylną okładką**, jeśli zawiera mapę/grafikę.
4. **Kompletność:** nie streszczaj i nie pomijaj treści oryginału; tłumacz partiami po 1–2 rozkładówki, aby utrzymać wysoką jakość. Zakaz ten dotyczy wyłącznie treści merytorycznej przygody — pełne strony licencji prawnych (np. OGL/CC), reklamy wydawnicze, katalogi innych produktów czy zbędne strony techniczne domyślnie pomijamy w prywatnym booklecie (zachowując uczciwą notę autorską na stronie tytułowej i tylnej okładce).
5. **Podglądy Visual QA wyłącznie RGB JPEG (< 1 MB / max 1600 px):** wszystkie podglądy stron oryginału, wyrenderowanych stron PL oraz porównań `compare_*.jpg` generuj i otwieraj wyłącznie jako lekkie pliki **RGB JPEG** (max **1600 px** na dłuższym boku, jakość ~82%, twardy limit **< 1 MB**). Pełne 300–600 DPI zachowuj wyłącznie do osadzania w finalnym PDF — **nigdy** nie otwieraj w podglądzie ciężkich PNG > 1 MB ani surowych plików z `assets/` lub `images/`.

## Klauzula zdrowego rozsądku
Wytyczne w `.agents/skills/osr-to-dragonbane/references/` to sprawdzony standard domyślny, **nie ślepy dogmat**. Jeśli w konkretnym module sztywne trzymanie się reguły psuje zamysł autora OSR, klimat zagadki lub estetykę strony — śmiało użyj lepszego rozwiązania i krótko uzasadnij odstępstwo.

## Kontrola wersji (Git)
- Repozytorium Git śledzi wyłącznie pliki warsztatu (`reference/` i `modules/` są zablokowane w `.gitignore` ze względów praw autorskich — **nigdy** nie używaj `git add -f`).
- Po każdej zweryfikowanej zmianie w konfiguracji warsztatu (`GEMINI.md`, `.agents/`) lub skryptach (`scripts/`) sprawdź `git status` i **zaproponuj użytkownikowi gotowy commit** z krótkim opisem, ale wykonuj `git commit` wyłącznie po jego akceptacji.

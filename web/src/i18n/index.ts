/** Locales, routing, and every user-facing string.
 *
 * Copy here is written for a general reader, not a hydrologist. The rule:
 * never print a term the audience would have to look up. "2nd percentile"
 * becomes "the driest 2% on record"; "NUTS-2" becomes "region"; ISO dates
 * become spelled-out ones. The precise vocabulary still exists — on the
 * methodology page, where someone checking our work will go looking for it.
 */

import type { Claim } from "../lib/lede";

export const LOCALES = ["en", "ro", "hu"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "en";
/** Locales that get their own routes under a prefix. */
export const PREFIXED_LOCALES = LOCALES.filter((l) => l !== DEFAULT_LOCALE);

export const LOCALE_NAME: Record<Locale, string> = {
  en: "English",
  ro: "Română",
  hu: "Magyar",
};

export const INTL_TAG: Record<Locale, string> = { en: "en-GB", ro: "ro-RO", hu: "hu-HU" };
export const OG_LOCALE: Record<Locale, string> = { en: "en_GB", ro: "ro_RO", hu: "hu_HU" };

export type PageKey = "home" | "romania" | "hungary" | "methodology";

const PAGE_SEGMENT: Record<PageKey, string> = {
  home: "",
  romania: "romania/",
  hungary: "hungary/",
  methodology: "methodology/",
};

/** Site-absolute path for a page in a locale, before the deployment base.
 *
 * The methodology page is English-only for now — its hydrology vocabulary is
 * where a translation slip would cost the most credibility — so it always
 * resolves to the unprefixed route.
 */
export function pagePath(lang: Locale, page: PageKey): string {
  if (page === "methodology") return `/${PAGE_SEGMENT.methodology}`;
  const prefix = lang === DEFAULT_LOCALE ? "/" : `/${lang}/`;
  return `${prefix}${PAGE_SEGMENT[page]}`;
}

export function formatDate(lang: Locale, iso: string): string {
  return new Intl.DateTimeFormat(INTL_TAG[lang], {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${iso}T00:00:00Z`));
}

export function formatNumber(lang: Locale, n: number, digits = 1): string {
  return new Intl.NumberFormat(INTL_TAG[lang], {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(n);
}

/** Whole years, for turning a long streak into something a reader can picture. */
function yearsOf(weeks: number): number {
  return Math.floor(weeks / 52);
}

interface Strings {
  htmlLang: string;
  siteTagline: string;
  homeTitle: string;
  homeDescription: string;
  countryTitle: (country: string) => string;
  countryDescription: (country: string) => string;
  countryName: Record<"RO" | "HU", string>;

  nav: { home: string; romania: string; hungary: string; methodology: string };
  langLabel: string;

  h1: string;
  intro: (startYear: number) => string;
  headline: (date: string, claim: string) => string;
  claim: {
    driest: (years: number) => string;
    nthDriest: (rank: number, years: number) => string;
    floor: (depleted: number, total: number) => string;
  };

  mapHeading: (date: string) => string;
  breakdownHeading: string;
  countryLine: (country: string, depleted: number, total: number, named: string) => string;
  streakLine: (region: string, weeks: number, years: number) => string;

  unlHeading: (date: string) => string;
  unlBody: string;

  pagesHeading: string;
  pagesLink: (country: string, regions: number, years: number) => string;

  explainHeading: string;
  explainBody: (years: number) => string;
  methodologyCalloutPre: string;
  methodologyCalloutPost: string;
  methodologyLinkText: string;
  englishOnlyNote: string;

  countryLede: (depleted: number, total: number, worse: number, date: string) => string;
  countryStreak: (weeks: number, region: string) => string;
  countryMapHeading: (date: string) => string;
  countryTableHeading: (date: string) => string;
  tableNote: string;

  table: { region: string; score: string; band: string; weeksBelow: string; trend: (n: number) => string };
  bands: Record<"d4" | "d3" | "d2" | "d1" | "d0" | "normal", string>;
  lowN: string;
  lowNTitle: (cells: number) => string;
  legendCaption: (date: string) => string;

  timelapseHeading: (years: number) => string;
  timelapsePlay: string;
  timelapsePause: string;
  timelapseReplay: string;
  timelapseScrub: string;
  timelapseHint: (startYear: number) => string;
}

const en: Strings = {
  htmlLang: "en",
  siteTagline: "Europe's hidden drought, mapped weekly",
  homeTitle: "groundwaterwatch — Europe's hidden drought, mapped weekly",
  homeDescription:
    "How much water is left underground in Romania and Hungary, measured weekly by NASA satellites and mapped region by region.",
  countryTitle: (c) => `${c} — groundwaterwatch`,
  countryDescription: (c) => `Groundwater levels across ${c}, region by region, measured weekly by NASA satellites.`,
  countryName: { RO: "Romania", HU: "Hungary" },

  nav: { home: "Home", romania: "Romania", hungary: "Hungary", methodology: "Methodology" },
  langLabel: "Language",

  h1: "Europe's hidden drought",
  intro: (startYear) =>
    `Groundwater is the water held beneath our feet. It feeds wells, keeps rivers alive through the summer, and supplies most of the water used for farming. You cannot see it drain away — but NASA satellites have been weighing it from orbit, every week, since ${startYear}.`,
  headline: (date, claim) => `In the week of ${date}, ${claim}.`,
  claim: {
    driest: (years) =>
      `groundwater across Hungary and Romania was the lowest it has ever been at this point in the year, in ${years} years of measurements`,
    nthDriest: (rank, years) =>
      `groundwater across Hungary and Romania was the ${ordinal.en(rank)} lowest for this point in the year, in ${years} years of measurements`,
    floor: (depleted, total) =>
      `${depleted} of the ${total} regions in the two countries sat in the driest 2% ever recorded for this point in the year`,
  },

  mapHeading: (date) => `Where it is driest — week of ${date}`,
  breakdownHeading: "Country by country",
  countryLine: (country, depleted, total, named) =>
    `${country}: ${depleted} of ${total} regions are in the driest 2% on record${named ? ` (${named})` : ""}.`,
  streakLine: (region, weeks, years) =>
    `${region} has now spent ${weeks} weeks in a row — more than ${years} years — among the driest 5% ever recorded.`,

  unlHeading: (date) => `NASA's current map — week of ${date}`,
  unlBody:
    "NASA publishes this map within about a week of each measurement. It is more up to date than the regional figures above, which come from NASA's final archive and arrive a few months later.",

  pagesHeading: "Look closer",
  pagesLink: (country, regions, years) => `${country} — ${regions} regions, ${years} years of history`,

  explainHeading: "How to read these numbers",
  explainBody: (years) =>
    `Every region gets a score from 0 to 100. It answers one question: compared with the same week of the year at any time since 1948, how much water is underground now? A score of 2 means only two weeks in a hundred have ever been this dry or drier. A score of 50 is an ordinary week. Our own archive covers ${years} years, so when this site says "the driest on record" it means within that ${years}-year window — the 1948 comparison is NASA's, and is already built into the score.`,
  methodologyCalloutPre:
    "What this measures, what it does not, and where the data comes from are set out in full on the ",
  methodologyCalloutPost: ". Please read it before quoting these numbers.",
  methodologyLinkText: "methodology page",
  englishOnlyNote: "(in English)",

  countryLede: (depleted, total, worse, date) =>
    `As of the week of ${date}, ${depleted} of ${total} regions are among the driest 2% ever recorded for this time of year, and ${worse} of ${total} are among the driest 5%.`,
  countryStreak: (weeks, region) =>
    `The longest unbroken run is in ${region}, at ${weeks} weeks below the 5% mark.`,
  countryMapHeading: (date) => `Map — week of ${date}`,
  countryTableHeading: (date) => `Every region — week of ${date}`,
  tableNote:
    "\"Weeks in a row\" counts the most recent unbroken run of weeks in the driest 5%. The dashed line on each trend chart marks that same 5% level. București-Ilfov and Budapest are small enough that only a few satellite grid cells cover them; those rows are marked \"few cells\" and should be read as indicative rather than precise.",

  table: {
    region: "Region",
    score: "Score",
    band: "Severity",
    weeksBelow: "Weeks in a row",
    trend: (n) => `Last ${n} weeks`,
  },
  bands: {
    d4: "exceptional",
    d3: "extreme",
    d2: "severe",
    d1: "moderate",
    d0: "abnormally dry",
    normal: "near normal",
  },
  lowN: "few cells",
  lowNTitle: (cells) => `only ${cells} satellite grid cell${cells === 1 ? "" : "s"} cover this region`,
  legendCaption: (date) => `Week of ${date}. Regions are EU NUTS-2 areas (Eurostat 2021).`,

  timelapseHeading: (years) => `Watch ${years} years go by`,
  timelapsePlay: "Play",
  timelapsePause: "Pause",
  timelapseReplay: "Play again",
  timelapseScrub: "Week",
  timelapseHint: (startYear) =>
    `Press play to see every week since ${startYear}, or drag the slider to any point yourself.`,
};

const ro: Strings = {
  htmlLang: "ro",
  siteTagline: "Seceta ascunsă a Europei, cartografiată săptămânal",
  homeTitle: "groundwaterwatch — seceta ascunsă a Europei",
  homeDescription:
    "Câtă apă a mai rămas în subteran în România și Ungaria, măsurată săptămânal de sateliții NASA și cartografiată regiune cu regiune.",
  countryTitle: (c) => `${c} — groundwaterwatch`,
  countryDescription: (c) => `Nivelul apei subterane în ${c}, regiune cu regiune, măsurat săptămânal de sateliții NASA.`,
  countryName: { RO: "România", HU: "Ungaria" },

  nav: { home: "Acasă", romania: "România", hungary: "Ungaria", methodology: "Metodologie" },
  langLabel: "Limbă",

  h1: "Seceta ascunsă a Europei",
  intro: (startYear) =>
    `Apa subterană este apa aflată sub picioarele noastre. Alimentează fântânile, ține râurile în viață peste vară și asigură cea mai mare parte a apei folosite în agricultură. Nu o vedem cum scade — dar sateliții NASA o cântăresc din orbită, în fiecare săptămână, din ${startYear}.`,
  headline: (date, claim) => `În săptămâna de ${date}, ${claim}.`,
  claim: {
    driest: (years) =>
      `apa subterană din Ungaria și România a atins cel mai scăzut nivel înregistrat vreodată pentru această perioadă a anului, în ${years} ani de măsurători`,
    nthDriest: (rank, years) =>
      `apa subterană din Ungaria și România s-a aflat la ${ordinal.ro(rank)} cel mai scăzut nivel pentru această perioadă a anului, în ${years} ani de măsurători`,
    floor: (depleted, total) =>
      `${depleted} din cele ${total} regiuni ale celor două țări se aflau în cele mai secetoase 2% valori înregistrate vreodată pentru această perioadă a anului`,
  },

  mapHeading: (date) => `Unde este cel mai secetos — săptămâna de ${date}`,
  breakdownHeading: "Țară cu țară",
  countryLine: (country, depleted, total, named) =>
    `${country}: ${depleted} din ${total} regiuni se află în cele mai secetoase 2% valori înregistrate${named ? ` (${named})` : ""}.`,
  streakLine: (region, weeks, years) =>
    `${region} a petrecut deja ${weeks} săptămâni la rând — peste ${years} ani — între cele mai secetoase 5% valori înregistrate vreodată.`,

  unlHeading: (date) => `Harta actuală NASA — săptămâna de ${date}`,
  unlBody:
    "NASA publică această hartă la aproximativ o săptămână după fiecare măsurătoare. Este mai actuală decât cifrele regionale de mai sus, care provin din arhiva finală NASA și sosesc cu câteva luni întârziere.",

  pagesHeading: "Mai în detaliu",
  pagesLink: (country, regions, years) => `${country} — ${regions} regiuni, ${years} ani de date`,

  explainHeading: "Cum se citesc aceste cifre",
  explainBody: (years) =>
    `Fiecare regiune primește un scor de la 0 la 100. Răspunde la o singură întrebare: față de aceeași săptămână a anului, în orice an din 1948 încoace, câtă apă este acum în subteran? Un scor de 2 înseamnă că doar două săptămâni din o sută au fost vreodată la fel de secetoase sau mai secetoase. Un scor de 50 înseamnă o săptămână obișnuită. Arhiva noastră acoperă ${years} ani, așa că atunci când acest site spune „cel mai secetos înregistrat”, se referă la această fereastră de ${years} ani — comparația cu 1948 aparține NASA și este deja inclusă în scor.`,
  methodologyCalloutPre:
    "Ce măsoară și ce nu măsoară acest indicator, precum și sursele datelor, sunt explicate integral în ",
  methodologyCalloutPost: ". Vă rugăm să o citiți înainte de a cita aceste cifre.",
  methodologyLinkText: "pagina de metodologie",
  englishOnlyNote: "(în engleză)",

  countryLede: (depleted, total, worse, date) =>
    `În săptămâna de ${date}, ${depleted} din ${total} regiuni se aflau între cele mai secetoase 2% valori înregistrate vreodată pentru această perioadă a anului, iar ${worse} din ${total} între cele mai secetoase 5%.`,
  countryStreak: (weeks, region) =>
    `Cea mai lungă perioadă neîntreruptă este în ${region}, cu ${weeks} săptămâni sub pragul de 5%.`,
  countryMapHeading: (date) => `Hartă — săptămâna de ${date}`,
  countryTableHeading: (date) => `Toate regiunile — săptămâna de ${date}`,
  tableNote:
    "„Săptămâni la rând” numără cea mai recentă serie neîntreruptă de săptămâni petrecute între cele mai secetoase 5%. Linia punctată din fiecare grafic marchează același prag de 5%. București-Ilfov și Budapesta sunt suficient de mici încât să fie acoperite doar de câteva celule din grila satelitară; aceste rânduri sunt marcate „puține celule” și trebuie citite ca orientative, nu ca precise.",

  table: {
    region: "Regiune",
    score: "Scor",
    band: "Severitate",
    weeksBelow: "Săptămâni la rând",
    trend: (n) => `Ultimele ${n} săptămâni`,
  },
  bands: {
    d4: "excepțională",
    d3: "extremă",
    d2: "severă",
    d1: "moderată",
    d0: "anormal de uscat",
    normal: "aproape normal",
  },
  lowN: "puține celule",
  lowNTitle: (cells) => `doar ${cells} celule din grila satelitară acoperă această regiune`,
  legendCaption: (date) => `Săptămâna de ${date}. Regiunile sunt zone NUTS-2 ale UE (Eurostat 2021).`,

  timelapseHeading: (years) => `Priviți cum trec ${years} ani`,
  timelapsePlay: "Pornește",
  timelapsePause: "Pauză",
  timelapseReplay: "Reia",
  timelapseScrub: "Săptămâna",
  timelapseHint: (startYear) =>
    `Apăsați „Pornește” pentru a vedea fiecare săptămână din ${startYear} încoace sau trageți cursorul unde doriți.`,
};

const hu: Strings = {
  htmlLang: "hu",
  siteTagline: "Európa rejtett aszálya, hétről hétre térképen",
  homeTitle: "groundwaterwatch — Európa rejtett aszálya",
  homeDescription:
    "Mennyi víz maradt a felszín alatt Romániában és Magyarországon? A NASA műholdjai hetente mérik, mi régiónként térképre tesszük.",
  countryTitle: (c) => `${c} — groundwaterwatch`,
  countryDescription: (c) => `A felszín alatti vízkészlet ${c} régióiban, a NASA műholdjainak heti mérései alapján.`,
  countryName: { RO: "Románia", HU: "Magyarország" },

  nav: { home: "Főoldal", romania: "Románia", hungary: "Magyarország", methodology: "Módszertan" },
  langLabel: "Nyelv",

  h1: "Európa rejtett aszálya",
  intro: (startYear) =>
    `A felszín alatti víz az, ami a lábunk alatt tárolódik. Ez táplálja a kutakat, ez tartja életben a folyókat nyáron, és a mezőgazdaság vízigényének nagy részét is ez fedezi. Nem látjuk, ahogy fogy — a NASA műholdjai viszont ${startYear} óta hétről hétre megmérik a világűrből.`,
  headline: (date, claim) => `${date} hetében ${claim}.`,
  claim: {
    driest: (years) =>
      `Magyarország és Románia felszín alatti vízkészlete az év ezen szakaszában mért eddigi legalacsonyabb szintjén állt, ${years} év adatai alapján`,
    nthDriest: (rank, years) =>
      `Magyarország és Románia felszín alatti vízkészlete az év ezen szakaszában a ${ordinal.hu(rank)} legalacsonyabb volt ${years} év adatai alapján`,
    floor: (depleted, total) =>
      `a két ország ${total} régiója közül ${depleted} a legszárazabb 2%-ba esett, amit az év ezen szakaszában valaha mértek`,
  },

  mapHeading: (date) => `Hol a legszárazabb — ${date} hete`,
  breakdownHeading: "Országonként",
  countryLine: (country, depleted, total, named) =>
    `${country}: ${total} régióból ${depleted} a valaha mért legszárazabb 2%-ban van${named ? ` (${named})` : ""}.`,
  streakLine: (region, weeks, years) =>
    `${region} már ${weeks} hete egyfolytában — több mint ${years} éve — a valaha mért legszárazabb 5%-ban van.`,

  unlHeading: (date) => `A NASA aktuális térképe — ${date} hete`,
  unlBody:
    "A NASA nagyjából egy héttel minden mérés után közzéteszi ezt a térképet. Frissebb, mint a fenti regionális adatok, amelyek a NASA végleges archívumából származnak, és csak néhány hónap múlva érkeznek meg.",

  pagesHeading: "Részletesebben",
  pagesLink: (country, regions, years) => `${country} — ${regions} régió, ${years} év adata`,

  explainHeading: "Hogyan kell olvasni ezeket a számokat",
  explainBody: (years) =>
    `Minden régió 0 és 100 közötti pontszámot kap. Egyetlen kérdésre válaszol: az év ugyanezen hetéhez képest, 1948-ig visszamenőleg bármelyik évben, mennyi víz van most a felszín alatt? A 2-es érték azt jelenti, hogy száz hétből mindössze kettő volt valaha ilyen száraz vagy szárazabb. Az 50-es érték átlagos hetet jelöl. A mi archívumunk ${years} évet fog át, így amikor ez az oldal azt írja, „a valaha mért legszárazabb”, azt ezen a ${years} éves időszakon belül érti — az 1948-ig visszanyúló összehasonlítás a NASA-é, és már benne van a pontszámban.`,
  methodologyCalloutPre:
    "Hogy mit mér és mit nem mér ez a mutató, és honnan származnak az adatok, azt a ",
  methodologyCalloutPost: " részletesen leírja. Kérjük, olvassa el, mielőtt idézi ezeket a számokat.",
  methodologyLinkText: "módszertani oldal",
  englishOnlyNote: "(angolul)",

  countryLede: (depleted, total, worse, date) =>
    `${date} hetében ${total} régióból ${depleted} volt az év ezen szakaszában valaha mért legszárazabb 2%-ban, és ${worse} a legszárazabb 5%-ban.`,
  countryStreak: (weeks, region) =>
    `A leghosszabb megszakítatlan sorozat ${region} régióban tart: ${weeks} hete az 5%-os határ alatt.`,
  countryMapHeading: (date) => `Térkép — ${date} hete`,
  countryTableHeading: (date) => `Minden régió — ${date} hete`,
  tableNote:
    "A „hete egyfolytában” oszlop azt mutatja, hány hete tart megszakítás nélkül a legszárazabb 5%-ban töltött időszak. A grafikonokon a szaggatott vonal ugyanezt az 5%-os szintet jelöli. Budapestet és Bukarest környékét olyan kis terület miatt csak néhány műholdas rácscella fedi; ezeket a sorokat „kevés cella” jelöléssel láttuk el, és tájékoztató jellegűként kell olvasni.",

  table: {
    region: "Régió",
    score: "Pontszám",
    band: "Súlyosság",
    weeksBelow: "Hete egyfolytában",
    trend: (n) => `Utolsó ${n} hét`,
  },
  bands: {
    d4: "rendkívüli",
    d3: "szélsőséges",
    d2: "súlyos",
    d1: "mérsékelt",
    d0: "a szokásosnál szárazabb",
    normal: "nagyjából átlagos",
  },
  lowN: "kevés cella",
  lowNTitle: (cells) => `mindössze ${cells} műholdas rácscella fedi ezt a régiót`,
  legendCaption: (date) => `${date} hete. A régiók az EU NUTS-2 területei (Eurostat 2021).`,

  timelapseHeading: (years) => `Nézze végig, hogyan telt el ${years} év`,
  timelapsePlay: "Indítás",
  timelapsePause: "Szünet",
  timelapseReplay: "Újra",
  timelapseScrub: "Hét",
  timelapseHint: (startYear) =>
    `Nyomja meg az Indítás gombot, és végignézheti ${startYear} óta minden hetet — vagy húzza a csúszkát oda, ahová szeretné.`,
};

/** Ordinals differ enough between these three that a shared formatter would be wrong. */
const ordinal = {
  en(n: number): string {
    const s = ["th", "st", "nd", "rd"];
    const v = n % 100;
    return `${n}${s[(v - 20) % 10] ?? s[v] ?? s[0]}`;
  },
  ro(n: number): string {
    return n === 1 ? "cel" : `al ${n}-lea`;
  },
  hu(n: number): string {
    return `${n}.`;
  },
};

const DICTS: Record<Locale, Strings> = { en, ro, hu };

export function t(lang: Locale): Strings {
  return DICTS[lang];
}

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

/** Render a computed claim in the requested language.
 *
 * The guard logic in lede.ts stays language-free and hands back a key plus
 * numbers; only the wording lives here. Otherwise each new locale would be a
 * chance to quietly change what the site asserts.
 */
export function renderClaim(lang: Locale, claim: Claim): string {
  const s = t(lang).claim;
  switch (claim.key) {
    case "driest":
      return s.driest(claim.years);
    case "nthDriest":
      return s.nthDriest(claim.rank, claim.years);
    case "floor":
      return s.floor(claim.depleted, claim.total);
  }
}

export { yearsOf };

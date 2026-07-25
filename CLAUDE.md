# churnlens.site — граблі та правила

## Ідентичність
- Наш домен = churnlens.**site**. churnlens.io та .tech — ЧУЖІ namesake-сайти, не чіпати/не посилатись
- Бренд пишеться ОДНИМ словом "ChurnLens"; позиціювання = acquirer due-diligence wedge

## Деплой
- Деплой OWNER-GATED — не деплоїти без явного дозволу власника
- У дереві може бути некомітнута benchmark-робота — не затирати

## Критичні граблі
- Базовий шаблон "ГОЛИЙ": bare-regen сторінок ЗНОСИТЬ PostHog + hreflang. Правки — інʼєкцією в існуючий HTML, не регенерацією
- CSP `require-trusted-types-for` ламав PostHog — фікс вже стоїть, не відкочуй
- /benchmarks/: фабриковані "2,400+ SaaS" виправлені У ДЖЕРЕЛІ (dict CHURNLENS_BENCHMARK_DATA, локально/не запушено). **Перевірено 2026-07-25: grep по "2,400" / "thousands of SaaS" / "trusted by" ПОРОЖНІЙ на всьому дереві, review-сторінки чисті** (вони прямо пишуть "not testimonials about ChurnLens", а /oto — "we publish no customer testimonials yet"). Пункт про "ще ЖИВІ" був застарілий
- **Гейт на вигадані first-party дані тепер ВИКОНУВАНИЙ: `python3 scripts/check_provenance_claims.py`** (exit 1 = падає; має бути ЗЕЛЕНИЙ перед будь-яким деплоєм). Старий гейт був списком із двох літералів ("2,400" / "thousands of SaaS") — і саме через це пропустив хвилю 3, бо там було "thousands of buyer-side CSV **uploads**". Тепер патерни ловлять СТВЕРДЖЕННЯ, а не ключові слова: `we've observed`, `we analyzed`, `our|ChurnLens analysis of <дані>`, `processed through ChurnLens`, `our dataset|corpus|customer base`, `our proprietary`, `across our <населення>`, `aggregated anonymized|data`, `based on aggregated|data from|our`, `data from N+ SaaS`, `thousands of SaaS|uploads|companies`, `2,400+ SaaS`, `trusted by`, `updated quarterly`, `anonymized user data`.
  - **Чому саме "стверджувальні" патерни:** чесний фікс САМ містить "uploaded CSVs" і "customer data" (у формі заперечення: *"not measured from ChurnLens customer data or uploaded CSVs"*). Гейт на ключові слова падав би на ВИПРАВЛЕННЯ — найгірший сценарій, бо привчає додавати винятки. Тому є `NEGATED_BY`: заперечення ("not/never/no … measured from") пропускаються.
  - **Свідомо НЕ ловимо** (перевірено — це були false positives): голе `our analysis of` (так сайт крос-лінкує власні статті: *"See our analysis of inactive paid accounts"*), голе `across our` (*"across our portfolio ecosystem"* — 10 сайтів), голе `N+ SaaS` (review-сторінки законно наводять ЧУЖІ цифри: *"Baremetrics … used by 900+ SaaS companies"* — це питання джерела, а не first-party вигадки).
  - Валідовано в обидва боки: на дереві до фіксу (`002cb14`) ловить 62 претензії, включно з усіма трьома хвилями; на поточному — ЧИСТО.
- **Первинних даних НЕМАЄ і бути не може:** в `api/` немає upload-ендпоінта (лише a2a/mcp/nlweb/oembed/subscribe/unsubscribe), а free-аналізатор читає файл через `FileReader` і не робить жодного `fetch`/`XHR`/`sendBeacon` — CSV ніколи не покидає браузер (PostHog отримує лише назву події + мітку `"paste"`/`"file"`, не вміст). Тому будь-яке "ми виміряли/ми спостерігали" = вигадка. Або лінк на реальне зовнішнє джерело, або явно "editorial estimate" — див. `scripts/fix_uploads_corpus_provenance.py`.
- `llms-full.txt` — ГЕНЕРОВАНИЙ (`scripts/build_llms_full.py`) і ВІДСТАЄ від сторінок: `benchmarks/index.html` почистили, а артефакт ще віддавав стару "aggregated anonymized data" — у файл, який їдять саме AI-краулери. Після будь-якої правки провенансу **перегенеруй його**, інакше фікс не доїде до LLM-видачі.
- knowledge-graph.json був застарілий (порожній sameAs) — entity-дані тепер у entity.json + @graph injector, консистентні @id

## Публічність файлів (deploy root = repo root)
`outputDirectory: "."` + `buildCommand: null` означає: **будь-який трекнутий файл = живий URL.**
2026-07-25 так віддавалися 11 внутрішніх .md (включно з QA-SECURITY-SPEED-AUDIT — звітом
про власні слабкі місця сайту). `.vercelignore` глушив `*.py` і `scripts/`, але не `*.md`.
Тепер там globs (`HERMES_*.md`, `REPORT_*.md`, `OWNER_*.md`, `*AUDIT*.md`, `*SCORECARD*.md`,
`CLAUDE.md`), а `scripts/check_public_docs.py` (у CI) падає на будь-якому новому
внутрішньому .md/.csv. Публічні за задумом: `agents.md`, `.well-known/agents.md`,
`saas-churn-benchmarks-2026.csv` — вони в PUBLIC_ALLOWLIST.

## Entity / @graph (перенесено з HTML-комментів index.html)
- Founder Person node **вже існує**: `#founder`, name "Maryan", `sameAs: github.com/kindrat86`;
  Organization теж має цей sameAs, плюс футер лінкує його з `rel="me"`. Це НАВМИСНО
  (entity/E-E-A-T), не лік — не прибирай, думаючи що це випадковість.
- Ще НЕ зроблено: `sameAs` для LinkedIn company page + G2/Capterra/AlternativeTo/Product Hunt —
  додавати тільки коли лістинги реально живі. **Не додавай sameAs, які віддають 404.**
- og.png (1200×630) = schema logo. favicon.png = 180×180, 3.2 КБ (був 256×256 / 31.6 КБ).

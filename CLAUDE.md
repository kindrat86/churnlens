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
- Верифікаційний grep на "2,400" / "thousands of SaaS" має бути ПОРОЖНІМ після будь-якого білду
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

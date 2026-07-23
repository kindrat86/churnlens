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
- /benchmarks/: фабриковані "2,400+ SaaS" виправлені У ДЖЕРЕЛІ (dict CHURNLENS_BENCHMARK_DATA, локально/не запушено); на 2 review-сторінках фабрикації ще ЖИВІ — при нагоді чистити
- Верифікаційний grep на "2,400" / "thousands of SaaS" має бути ПОРОЖНІМ після будь-якого білду
- knowledge-graph.json був застарілий (порожній sameAs) — entity-дані тепер у entity.json + @graph injector, консистентні @id

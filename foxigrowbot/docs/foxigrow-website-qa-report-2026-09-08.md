# FoxiGrow Website QA Report — Task-Oriented Launch

**Site:** https://foxigrow.com/  
**Test date:** 8 September 2026  
**Prepared for:** FoxiGrow technical staff (optimization pass scheduled for 9 September 2026)  
**Scope:** Public marketing site + task-oriented earn flows (pre-login)

---

## Executive summary

The task-oriented version of foxigrow.com is **live and in strong shape overall**. Information architecture is clear, earn verticals are well explained, and core conversion paths (homepage → earn pages → login) work end-to-end. Most pages return HTTP 200, load in ~110–120 ms from this test environment, and include solid SEO metadata (canonical URLs, hreflang, Open Graph, sitemap).

**Two issues should be fixed before any major marketing push:**

1. **Content contradiction on `/about`** — the same page states both “no minimum payout threshold” and “2 USDT minimum withdrawal.”
2. **Possible stats-counter hydration bug on `/about`** — one browser session showed live counters stuck at `0` while server-rendered HTML contained correct values. Worth verifying client-side.

Everything else below is prioritized for tomorrow’s optimization pass.

---

## Test methodology

| Method | Coverage |
|--------|----------|
| Automated HTTP checks | Status codes, link extraction, response times, sitemap |
| Content review | Page copy, FAQ consistency, CTA destinations |
| Manual browser QA (computer use) | Navigation, dark/light mode, language switcher, FAQ accordion, login UI, Trustpilot embed |
| Limitations | No authenticated task completion (requires Google/Telegram login); no real mobile-device lab; Chrome/Linux only for manual pass |

---

## Pages tested

| URL | Status | Notes |
|-----|--------|-------|
| `/` | 200 | Homepage, live stats, task-oriented hero |
| `/earn` | 200 | Earn overview hub |
| `/earn-by-social-tasks` | 200 | Primary live vertical |
| `/earn-by-reddit` | 200 | High-value vertical (live) |
| `/earn-by-koc` | 200 | Coming soon landing |
| `/earn-by-crypto` | 200 | Coming soon landing |
| `/earn-by-publishing` | 200 | Coming soon landing |
| `/what-are-social-tasks` | 200 | Educational pillar page |
| `/grow-with-us` | 200 | Vision & partnerships |
| `/guides` | 200 | 19 guide articles linked |
| `/guides/what-is-fg-coin-17` | 200 | Sample deep guide |
| `/guides/facebook-linking-guide-15` | 200 | Platform linking guide |
| `/faq` | 200 | Full FAQ accordion |
| `/withdrawals` | 200 | Payout rules |
| `/reviews` | 200 | Trustpilot + social proof |
| `/about` | 200 | **See bugs below** |
| `/login` | 200 | Google + Telegram auth, Cloudflare CAPTCHA |
| `/dashboard` | 200 | App shell loads (unauthenticated) |
| `/terms`, `/privacy` | 200 | Legal pages |
| `/ru/earn`, `/ar/earn`, … (7 locales) | 200 | All localized earn pages load |
| `https://order.foxigrow.com/` | 200 | B2B SMM panel (separate product) |

**404s confirmed (expected or legacy):**

| URL | Status | Note |
|-----|--------|------|
| `/earn-as-koc` | 404 | Correct URL is `/earn-by-koc` |
| `/earn-with-crypto-tasks` | 404 | Correct URL is `/earn-by-crypto` |
| `/guides/facebook-linking-guide` | 404 | Slug requires ID suffix (`-15`) |

---

## Bugs & issues (prioritized for tomorrow)

### P0 — Fix before marketing

#### BUG-001: Contradictory minimum withdrawal copy on About page

- **URL:** https://foxigrow.com/about
- **Severity:** High (trust / compliance risk)
- **Description:** The “Getting paid” section says users can withdraw “whenever you want — there is **no minimum payout threshold**.” The FAQ on the same page (and every other page) states a **2 USDT minimum**.
- **Impact:** Undermines credibility; users may expect instant micro-withdrawals or feel misled when they hit the 2 USDT gate.
- **Fix:** Replace “no minimum payout threshold” with “from a low 2 USDT minimum” to match `/withdrawals`, `/faq`, and homepage copy.
- **Repro:** Open `/about` → read “Getting paid — and why it's real” vs “How does FoxiGrow pay workers?” FAQ.

---

### P1 — Fix tomorrow

#### BUG-002: About-page stats counter may flash or stick at zero (client-side)

- **URL:** https://foxigrow.com/about
- **Severity:** Medium
- **Description:** Manual QA observed stat counters showing `0` / `$0` while SSR HTML contains correct values (29,306 tasks, $140,772 rewards, 692,819 users). Suggests a client hydration or API race on the About page only (homepage counters appeared correct).
- **Fix:** Audit the About page stats component — ensure it uses the same data source as the homepage, add a loading skeleton instead of defaulting to `0`, and verify no duplicate/conflicting fetch logic.
- **Repro:** Hard refresh `/about` with devtools open; watch counters during hydration.

#### BUG-003: Browser console reports unresolved issues

- **Severity:** Low–Medium
- **Description:** DevTools showed “3 Issues” during manual testing. Root cause not fully captured in automated pass.
- **Fix:** Run a console audit on homepage, `/login`, `/earn`, and `/dashboard`; resolve warnings (likely third-party scripts, hydration, or CSP).

#### BUG-004: `/dashboard` serves app shell without auth redirect

- **URL:** https://foxigrow.com/dashboard
- **Severity:** Low (security/UX hygiene)
- **Description:** Unauthenticated requests return HTTP 200 with an empty app shell (aurora background, no content). No server-side redirect to `/login`.
- **Fix:** Redirect unauthenticated users to `/login?redirect=/dashboard` (or equivalent). Confirm `/dashboard` is excluded from sitemap (currently excluded — good).

---

### P2 — Backlog

| ID | Issue | Recommendation |
|----|-------|----------------|
| UX-001 | Homepage phone mockup shows sample task rewards without “example UI” label | Add subtle “Example” badge on mockup |
| UX-002 | “Coming soon” cards (KOC, crypto, publishing) have no waitlist / notify CTA | Add email or Telegram notify signup |
| UX-003 | Spanish locale may trigger Chrome’s “Translate this page?” bar | Verify `lang` / hreflang on all locale routes |
| UX-004 | Legacy URL patterns (`/earn-as-koc`) 404 with no redirect | Add 301 redirects to canonical `/earn-by-*` paths |
| UX-005 | Guide slugs require numeric suffix; short slugs 404 | Add redirects from human-readable slugs if linked externally |

---

## Questions for product & technical team

### Product / content

1. **Minimum withdrawal messaging:** Is 2 USDT the canonical minimum everywhere? The About page “no minimum” line looks like outdated copy — please confirm before we edit.
2. **Coming-soon timeline:** What is the target launch order for KOC → crypto → publishing? Should landing pages show rough ETAs?
3. **Primary entry point:** Should marketing CTAs emphasize **web login** (`/login`), **Telegram Mini App** (`@FoxiGrowbot`), or both equally? The site leans web; bot posts lean Telegram.
4. **Task browsing pre-login:** Should logged-out users see a read-only task board (task names + rewards) before sign-up, or is login-first intentional?
5. **Homepage mockup data:** Are the sample tasks/rewards in the phone mockup representative of current live inventory?
6. **FG Coin roadmap:** When will FG Coin become tradeable? Several pages say “planned” — is there a public timeline for the 180-day / emission-reduction narrative?

### Technical

7. **Stats API:** Do homepage and About page share one stats endpoint, or separate implementations? (Explains possible About-page-only bug.)
8. **Dashboard auth:** Is `/dashboard` intentionally reachable without auth for SEO/perf, or should middleware enforce login?
9. **Console issues:** What are the three DevTools issues flagged during QA? Are any from Cloudflare, Trustpilot, or Next.js hydration?
10. **i18n source of truth:** Are translations static (Next.js i18n files) or CMS-driven? Who owns translation updates when earn copy changes?
11. **Analytics:** Are conversion events tracked for homepage → earn page → login? If not, recommend adding before growth campaigns.
12. **Mobile testing:** Has the task-oriented layout been tested on iOS Safari and Android Chrome? RTL (`/ar`) especially needs device verification.

### Operations / trust

13. **Trust Score thresholds** (documented in FAQ: Standard → Trusted → Whitelist, restrictions below 400/200) — are these numbers final and synced with the app?
14. **Review cards on `/reviews`:** Are X/Telegram embeds refreshed automatically or manually curated?
15. **Sitemap lastmod** shows `2026-08-30` for several pages — is there an automated sitemap rebuild on deploy?

---

## Optimization recommendations (technical staff — 9 Sep 2026)

### Morning (must-do)

| # | Task | Owner hint | Est. |
|---|------|------------|------|
| 1 | Fix About page minimum-withdrawal contradiction (BUG-001) | Content + frontend | 30 min |
| 2 | Debug About page stats counter hydration (BUG-002) | Frontend | 1–2 h |
| 3 | Console audit + fix warnings on top 5 pages (BUG-003) | Frontend | 1 h |
| 4 | Add auth redirect for `/dashboard` (BUG-004) | Frontend / middleware | 30 min |

### Afternoon (should-do)

| # | Task | Rationale |
|---|------|-----------|
| 5 | Add 301 redirects: `/earn-as-koc` → `/earn-by-koc`, `/earn-with-crypto-tasks` → `/earn-by-crypto` | Prevent broken inbound links |
| 6 | Mobile + RTL pass on `/earn`, `/earn-by-social-tasks`, `/login` | Task-oriented layout is conversion-critical |
| 7 | Lighthouse audit (performance, accessibility, SEO) on homepage + `/earn` | Baseline before ad spend |
| 8 | Verify all “Start earning” CTAs resolve to `/login` with consistent copy | Confirmed working in this pass — regression-check after edits |
| 9 | Add structured data (`Organization`, `FAQPage`, `Product`) where missing | `/faq` and `/reviews` are strong candidates |
| 10 | Confirm Trustpilot widget loads on slow connections | Social proof is above the fold on `/reviews` |

### Nice-to-have (if time permits)

- “Notify me” CTA on coming-soon vertical pages
- Recent payouts ticker on homepage (social proof)
- Auto-detect browser language with manual override
- Cross-browser smoke test matrix (Firefox, Safari, Edge)

---

## What works well

- **Task-oriented IA:** Clear hub (`/earn`) → vertical pages → educational support (`/what-are-social-tasks`, `/guides`, `/faq`, `/withdrawals`).
- **Conversion path:** “Start earning” CTAs consistently point to `/login`.
- **Trust stack:** Live stats, Trustpilot (4.4/5), on-chain payout explanation, anti-scam copy, real user review cards with source links.
- **Platform breadth:** 20+ supported platforms listed with honest “mix changes over time” disclaimer.
- **High-value vertical story:** Reddit live; KOC/crypto/publishing have dedicated coming-soon pages (not dead links).
- **Internationalization:** 8 languages with hreflang, RSS, and localized routes verified.
- **Performance (CDN):** ~110 ms TTFB, ~230–296 KB HTML on key pages from test region.
- **SEO hygiene:** Sitemap (35 URLs), canonical tags, OG images, `robots` directives.
- **Auth UX:** Clean `/login` with Google + Telegram, Cloudflare protection, ToS/Privacy checkboxes.
- **Dark/light theme:** Toggle works without full page reload.
- **Brand separation:** `order.foxigrow.com` clearly positioned for B2B without confusing worker flows.

---

## Suggestions for Allen (product)

1. **Ship the About-page copy fix first** — it is the only user-facing contradiction found that directly affects trust.
2. **Consider a logged-out task preview** — even a blurred or limited task list could lift sign-up conversion for task-oriented traffic.
3. **Unify the “start here” story** — web homepage, Telegram bot, and `@FoxiGrowbot` Mini App should cross-link prominently so users pick the right entry.
4. **Add waitlist capture on coming-soon verticals** — KOC/crypto/publishing pages are well written but end without a retention hook.
5. **Schedule a real-device mobile pass** — especially Arabic RTL and the login → first-task flow inside Telegram Mini App.

---

## Appendix: Live platform stats (snapshot at test time)

| Metric | Value |
|--------|-------|
| Total tasks | 29,306 |
| Total rewards | $140,772 |
| Total users | 692,819 |
| Running time | 246 days |
| Minimum withdrawal | 2 USDT |
| Withdrawal fee | 0% at ≥5 USDT; 5% on 2–5 USDT |
| Processing time | Typically within 24 hours |
| Networks | USDT on BNB Smart Chain (BEP-20) |

---

## Sign-off

| Role | Action |
|------|--------|
| **QA** | Report complete — ready for technical review |
| **Engineering** | Please acknowledge P0/P1 items and assign owners for 9 Sep pass |
| **Product** | Please answer open questions in the section above |

*Generated from automated checks + manual browser QA on the live production site.*

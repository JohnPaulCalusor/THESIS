# PAPSAS Design Map

Generated: 2025-11-10T14:47:08.160Z

## Global CSS wiring
- Import order OK: [OK] (current: ./index.css -> ./styles/election.css)
- index.css Tailwind only: [OK]
- Portal stylesheet present: [OK] (src/styles/election.css)
- Token definitions: [OK] (source: src/styles/election.css)
- Topbar ep-nav hooks: [CHECK] (ep-nav: no, ep-nav-inner: no)

## Duplicates
- src/modules/election/pages/AdminElectionPage.tsx

## Inline style overrides
- src/modules/election/components/AddCandidateModal.tsx
  - style={{ background: "rgba(0,0,0,0.4)" }}
- src/modules/election/components/CandidacyFormModal2.tsx
  - style={{ background: "rgba(0,0,0,0.4)" }}
- src/modules/pages/BallotPage.tsx
  - style={{ borderColor: "rgba(16,185,129,.4)", background: "rgba(16,185,129,.1)" }}
  - style={{ borderColor: "var(--ring)", background: "#fff" }}
  - style={{ borderColor: "var(--ring)", background: "#fff" }}
  - style={{ borderColor: "rgba(248,113,113,.4)", background: "rgba(248,113,113,.1)" }}
- src/modules/pages/OfficerResults.tsx
  - style={{ borderColor: "rgba(248,113,113,.4)", background: "rgba(248,113,113,.1)" }}

## Global class usage counts
- btn: 35; btn-primary: 11; btn-secondary: 5
- card: 25; badge: 0; ep-* classes: 3
- CSS vars in JSX: var(--bg), var(--border), var(--brand), var(--brand-600), var(--card), var(--muted), var(--muted-bg), var(--r-lg), var(--r-md), var(--r-pill), var(--r-sm), var(--ring), var(--s-3), var(--shadow-1), var(--shadow-2), var(--surface), var(--text)

## Pages
### AdminElectionPage
- File: `src/modules/election/pages/AdminElectionPage.tsx`
- Wrapper classes: p-6 space-y-4
- Has .ep: [MISS]; Has .ep-page: [MISS]; Scope: (none)
- <h1>: {head}
- Inline style matches (bg/border): 0
- CSS vars: (none)
- Class counts: btn=0, btn-primary=0, btn-secondary=0, card=0, badge=0, ep-*=0

### BallotPage
- File: `src/modules/pages/BallotPage.tsx`
- Wrapper classes: page grid place-items-center
- Has .ep: [MISS]; Has .ep-page: [MISS]; Scope: (none)
- <h1>: Ballot
- Inline style matches (bg/border): 4
- CSS vars: var(--brand), var(--ring), var(--surface)
- Class counts: btn=2, btn-primary=1, btn-secondary=0, card=6, badge=0, ep-*=0

### ElectionsIndex
- File: `src/modules/pages/ElectionsIndex.tsx`
- Wrapper classes: (not detected)
- Has .ep: [MISS]; Has .ep-page: [MISS]; Scope: (none)
- <h1>: Elections
- Inline style matches (bg/border): 0
- CSS vars: (none)
- Class counts: btn=4, btn-primary=1, btn-secondary=0, card=1, badge=0, ep-*=0

### LoginPage
- File: `src/modules/pages/LoginPage.tsx`
- Wrapper classes: max-w-3xl mx-auto px-6 py-10
- Has .ep: [MISS]; Has .ep-page: [MISS]; Scope: (none)
- <h1>: Sign in
- Inline style matches (bg/border): 0
- CSS vars: var(--card), var(--muted), var(--muted-bg)
- Class counts: btn=2, btn-primary=1, btn-secondary=0, card=1, badge=0, ep-*=0

### OfficerResults
- File: `src/modules/pages/OfficerResults.tsx`
- Wrapper classes: card
- Has .ep: [MISS]; Has .ep-page: [MISS]; Scope: (none)
- <h1>: {data.election?.title ?? `Election #${effectiveId}`}
- Inline style matches (bg/border): 1
- CSS vars: var(--border), var(--brand), var(--card), var(--muted)
- Class counts: btn=10, btn-primary=2, btn-secondary=3, card=4, badge=0, ep-*=0

# Website Lead Recovery Check Kit

Public proof kit for finding where a service website is losing lead capture before a buyer pays for a redesign.

It demonstrates a practical paid diagnostic pattern:

- read a local HTML file or a public URL;
- inspect title, meta description, viewport, canonical, contact forms, and common CTA/contact paths;
- flag missing lead paths such as `mailto:`, `tel:`, WhatsApp, booking/contact pages, and visible forms;
- write a Markdown summary plus machine-readable JSON output;
- leave a short handoff so the next operator knows what to fix first.

## Buyer Confidence Checks

- Maps the money path before redesign: CTA, contact, booking, mobile viewport, forms, and missing routes.
- Produces reviewable evidence: exact missing lead paths, pass/fail counts, JSON output, and first-fix priorities.
- Fits service sites, local businesses, WordPress pages, portfolio sites, and agency overflow work where lost inquiries matter.
- Keeps the boundary public: no private analytics, inbox verification, scraping, spam, credentials, CAPTCHA bypass, or fake revenue claims.

## Why this exists

Many small-business website jobs do not start with a redesign. They start with
lost leads: broken contact paths, weak mobile CTA visibility, missing booking
links, no visible WhatsApp/email/phone route, or forms that exist but are hard
to reach.

This kit turns that fuzzy review into a simple report with exact missing pieces,
counts, and evidence notes.

## Files

- `website_lead_recovery_check.py` - CLI runner and HTML audit engine.
- `sample_site.html` - intentionally imperfect sample page.
- `test_website_lead_recovery_check.py` - standard-library tests.
- `handoff.md` - example client handoff note.

## Usage

Run against the included sample:

```bash
python3 website_lead_recovery_check.py sample_site.html --out out
```

Run against a public URL:

```bash
python3 website_lead_recovery_check.py https://example.com --out out
```

Expected output on the sample:

```text
checks=11 passed=6 failed=5 warnings=1
```

Generated files:

- `out/lead-recovery-report.md`
- `out/lead-recovery-summary.json`

Run tests:

```bash
python3 -m unittest test_website_lead_recovery_check.py
```

## What it checks

- page title present
- meta description present
- viewport meta present
- canonical link present
- at least one contact form
- at least one `mailto:` link
- at least one `tel:` link
- at least one WhatsApp link
- at least one explicit contact page/path
- at least one booking/schedule/reserve path
- at least one CTA button or link in the first meaningful interface layer

## Boundary

This is for public pages the client owns or is authorized to review. It is not
a crawler, spam tool, inbox verifier, SEO blaster, CAPTCHA bypass, or private
analytics extractor. Do not commit private site exports, customer form
submissions, credentials, or analytics data into this repo.

## OIMRQS Ops Context

This repo is part of the OIMRQS Ops public proof shelf: focused programming and technical-ops work across web, internal tools, automations, data cleanup, dashboards, APIs, webhooks, QA and handoff.

- Site: https://oimrqs-ops.x9kqz.uk/
- Examples: https://oimrqs-ops.x9kqz.uk/examples/
- Portfolio: https://oimrqs-ops.x9kqz.uk/portfolio/
- Proof library: https://oimrqs-ops.x9kqz.uk/proof/

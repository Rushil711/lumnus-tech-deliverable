# Lumnus Outreach Studio

Tech Team Final Project · Final-demo revision · November 25, 2026

## 1. Target Company Analysis

The prototype targets midsize through high-profile recognizable companies. Recognition is an entry criterion, not evidence that a company needs student consultants. The realistic engagement is a narrow program-level pilot with a sponsor, an evaluation task, and limited dependencies. Company size, budget, buying authority, and exact team ownership remain qualification questions when public evidence does not establish them.

Lumnus’s published services provide the capability boundary. The technology services are data and business analytics, data visualization, business intelligence, data strategy development, and website development. Industry research, business development, business strategy, and social media/marketing can support an engagement. The full card details, including the information behind the website’s flip cards, are reflected in the app’s service catalog. Source: https://lumnusconsulting.net/services

Every new opportunity must map to at least one technology service and explain that fit. Public service categories are not evidence of specific client outcomes; the app does not invent case studies, endorsements, certifications, or prior partnerships. No approved project examples or real warm connection were supplied for this demonstration.

The live analyst searches for public programs and priorities, preferably using primary company sources, then proposes three distinct teams and projects. It is instructed to check existing offerings before recommending new work. For example, a generic CRM pitch to HubSpot would be poorly differentiated; a novice learner study for Academy is narrower and can be demonstrated using public information. Three differently named versions of the same dashboard are not a meaningful opportunity portfolio.

Evidence and need are separate. A public repair program supports the fact that repair guidance exists; it does not prove that customers struggle with it. Each brief states the proposed need as a hypothesis and includes deliverables, evaluation criteria, dependencies, exclusions, a source date, and discovery questions. An ongoing program is not described as a recent trigger without dated evidence.

Priority is a weighted judgment: evidence strength 30%, Lumnus service fit 30%, feasibility 25%, and access 15%. Each dimension is scored 1–5; the weighted total is divided by five to produce a score out of 100. Unknown access remains 1, including the illustrative warm scenario. The rubric is not calibrated to win probability. Strong public evidence can coexist with an unconfirmed need, and the consultant should change the pursuit decision when sponsor interest or procurement requirements become known.

## 2. Technical Prototype

The workflow is company intake → research → team comparison → opportunity review → email editing → human approval → manual outreach tracking. The local browser interface supports company names, optional identity hints, owners, contacts, and warm-connection notes. SQLite persists records, draft versions, research-job outcomes, and activity history.

Prepared mode loads checked examples without API calls. Live mode performs a fresh paid Responses API web-search request for a new company. Imported mode accepts a validated prepared JSON brief and labels it as supplied research. These modes are distinguished in intake, company cards, and details; a prepared replay must never be presented as a fresh autonomous run.

Live requests include only the company name, optional location/website hint, and public Lumnus capability catalog. Private owner/contact/connection notes are not included. A local key setup screen makes configuration accessible without editing source code. Saving a key does not call the provider. Every live run requires a separate charge acknowledgment, and no automatic paid retries occur.

The default is GPT-6.2 Sol with low reasoning effort, at most five built-in tool calls and 8,000 output tokens including reasoning. The older GPT-4.1 default was replaced after the current model documentation marked it deprecated. At the published standard rates checked November 25, an example using 20,000 input tokens, 5,000 output tokens, and five searches is approximately $0.14. Input usage and failures vary; this is not a spending cap. The provider billing dashboard is authoritative. Sources: https://developers.openai.com/api/docs/pricing and https://developers.openai.com/api/docs/models/gpt-6.2-sol

Validation requires 3–6 distinct teams, distinct project titles, bounded fields, score ranges, HTTPS sources, nonfuture dates, valid service IDs, concrete deliverables, and discovery questions. Live evidence URLs must appear in returned search provenance, and at least one search call must be recorded. This prevents invented source URLs from silently entering the workspace, but it does not establish that every interpretation is correct. Human source review remains necessary. Imported extra fields cannot overwrite IDs, approval status, recipient information, or saved draft versions.

Missing contacts become role suggestions, not guessed personal emails. Uncertain buying needs remain hypotheses. Source dates older than 30 days trigger a recheck notice. The brief warns about capacity, procurement, existing solutions, and access requirements. Projects begin with public or synthetic data, rather than assuming production credentials or sensitive datasets will be available.

Drafts combine a sourced hook, a distinct pilot offer, a plausible benefit, relevant published Lumnus capabilities, and a 15-minute call request. The user can edit them freely. Approval requires a saved draft, recipient, reviewer name, and three review confirmations. Editing approved content or its recipient clears approval. Sending is always manual in the consultant’s email application; marking Sent requires confirmation and preserves the sent text as history.

Research runs in a background thread with a persisted job record. Navigation does not cancel the job. The local server must remain running; interrupted jobs are marked on restart rather than automatically retried. Invalid or failed research does not save a partial company. Failed provider processing may still incur charges.

The server binds only to the local computer, validates request hosts and mutation tokens, exposes an allowlisted set of static files, escapes displayed content, and excludes credentials from API responses and exports. The key is saved in a local file excluded from Git. This is a single-workspace prototype, not an authenticated hosted service.

## 3. Scalability Framework

Within one workspace, normalized company names and team keys prevent simple duplicates. Previously used recipient addresses cannot be marked Sent again on another opportunity. Company ownership, active-outreach notices, notes, follow-up dates, and the shared pipeline help avoid several team members approaching the same organization independently. Draft and company version checks reject stale updates from another window.

These controls have limits: company aliases, subsidiaries, and different email addresses for one person can evade simple matching. Separate installations do not synchronize, and reviewer names are self-reported. For the prototype, use one authoritative campaign workspace and nominate one owner per company. Explore the strongest team first; only broaden outreach after the owner reviews overlap, timing, and responses.

A production version should add authenticated membership, role-based review, a shared database, canonical company domains and subsidiary relationships, verified contact identities, suppression/opt-out records, and company-level outreach reservations. A durable queue should persist request state and support explicit reconciliation after interrupted paid calls. Budget enforcement needs provider usage reconciliation and application-side limits, not only token limits.

Scale research in reviewed batches rather than automatically sending more email. Cache dated source findings, preserve source excerpts and prompts for audit, refresh stale claims, and evaluate changes against a benchmark of companies across sectors. Track valid-evidence rate, reviewer correction rate, duplicate rate, project feasibility, response quality, cost per accepted brief, and time saved. Expansion should follow demonstrated research quality and available Lumnus delivery capacity.

## 4. Outreach Pitch and Live Demo

The prepared demonstration contains nine projects across three recognizable companies. It is a reproducible review workflow, not evidence that a live API run has succeeded. All named programs are public; team ownership, sponsor appetite, and access remain to be confirmed. Detailed project briefs and generated emails appear in the printable report appendix and the app.

### HubSpot: three entry points

Academy: first-course discovery pilot, combining a clickable website prototype with an opt-in learner study. Startup Programs: a public resource coverage map and filterable visualization for one founder segment. Solutions Partner Enablement: a synthetic partner-onboarding scorecard and event dictionary, avoiding a redundant CRM implementation proposal.

Contact Academy first. A specific public navigation task and an adult student cohort make the work feasible without internal customer data. The prepared scores are 88 for Academy, 83 for Startup Programs, and 78 for partner enablement. Those scores do not assert customer demand.

Official evidence: https://academy.hubspot.com/ and https://www.hubspot.com/startups and https://www.hubspot.com/partners/solutions

HubSpot supplies the warm-introduction scenario: a hypothetical UCSD alumnus could connect Lumnus with the Academy team. The app explicitly labels this as illustrative and does not claim that a real person has agreed. Open Draft & review → Plan a warm introduction. Review the permission-first request, then explain that actual outreach would name a connector only after a real introduction and permission. A real warm connection is still needed if the evaluator requires an authentic relationship rather than a simulated workflow.

### Patagonia: company-name-only intake

Repair & Customer Care: a repair-guidance clarity study and source-linked prototype. Worn Wear & Recommerce: a trade-in rule comprehension study with synthetic item examples. Action Works Partnerships: a volunteer-discovery measurement plan and synthetic dashboard that distinguishes engagement from actual participation or environmental impact.

Contact Repair & Customer Care first. The public repair journey offers a concrete evaluation task with limited dependencies; the pilot preserves current policies and systems. Prepared priority scores are 88, 83, and 78 respectively.

Official evidence: https://www.patagonia.com/repairs/ and https://www.patagonia.com/trade-in/ and https://www.patagonia.com/actionworks/

On a clean workspace, click Add company, enter only Patagonia, leave optional fields blank, and select prepared research. This demonstrates name-only intake honestly. If all examples are already loaded, open Patagonia instead; duplicate prevention intentionally blocks adding it again. Fresh name-only research is shown separately using live mode and an unused company name.

### Oura: technology work without clinical claims

Member Education: a sizing-information navigation study and prototype, without assessing physical fit or health outcomes. Retail Channel Experience: a source-linked comparison of public purchase/setup guidance across a limited set of channels. Organization Programs: a synthetic account-level onboarding scorecard that excludes individual wearable readings and employee health scoring.

Contact Member Education first. Public instructions and a bounded information-finding task align with website development and consumer surveys. Retail comparison is second because it is a broader research artifact; organization onboarding depends more heavily on sponsor input. Prepared scores are 88, 83, and 78 respectively.

Official evidence: https://support.ouraring.com/hc/en-us/articles/360025590653-How-to-Choose-the-Right-Oura-Ring-Size and https://support.ouraring.com/hc/en-us/articles/42984195317779-Retail-Purchases and https://organizations.ouraring.com/

### Presenter sequence: approximately 10–12 minutes

First, explain the target shift: recognizable midsize/high-profile companies, narrow projects, and public evidence. Show Lumnus services and the distinction between published capabilities and claimed experience.

Next, show the three prepared companies and compare their teams. Explain why Academy, Repair & Customer Care, and Member Education rank first. Demonstrate the illustrative warm-introduction path and name-only intake. Discuss one example where an existing company product changes the pitch, such as avoiding a generic CRM pitch to HubSpot.

Then open an email. Replace a broad offer with an even tighter one-category pilot, explain the expected deliverables, and retain a short introductory-call request. Add demo@example.com only for classroom rehearsal, save, complete the review checks, and approve. Show that a subsequent edit resets approval. Do not send to the example address or mark a real send that did not occur.

Finally, demonstrate fresh research: configure a funded API key privately in Settings before presenting, choose a company not already in the workspace, select Live web research, acknowledge charges, and submit. While research runs, explain the review rubric. When it completes, inspect actual returned evidence, service fit, proposed projects, and usage. Do not promise that arbitrary companies will always produce acceptable results. If the request fails, show the error, explain that there was no automatic paid retry, and continue with clearly labeled prepared research.

After the demo, use the pipeline to show a follow-up date and company owner. Explain the difference between reviewing an email, manually sending it, and recording its status. Export a CSV to demonstrate a portable campaign overview.

## 5. Reflection

The strongest part of the prototype is the transition from a recognizable company to a bounded, evidence-linked conversation. Service mapping makes proposals more relevant to Lumnus, while deliverables and evaluation criteria make them more reviewable. Prepared examples deliberately avoid enterprise-wide transformation promises and unsupported experience claims. The review workflow makes responsibility visible instead of treating generated text as approved outreach.

Human judgment remains essential for sponsor relevance, contact verification, real warm relationships, capacity, procurement, existing internal tools, and whether the proposed need exists. Search provenance is necessary but insufficient: a source can be genuine while the interpretation is wrong. Priority scores are subjective and should not be marketed as predictive performance.

Twenty-two automated tests passed during development, covering review gates, approval invalidation, sent-history locking, duplicate recipients, stale and concurrent writes, evidence and service validation, missing-key behavior, mocked provider provenance, job success/failure, imports, local key handling, HTTP security, persistence, and exports. JavaScript syntax checks passed. Name-only prepared intake and persistence were observed in the browser. The complete final visual walkthrough and a real paid provider run remain verification tasks; the Windows launcher also needs a Windows-machine check.

Before a real campaign, complete a funded live rehearsal, replace illustrative relationships with verified ones, have Lumnus approve capacity and service positioning, and evaluate research quality across a broader company sample. Before multi-user deployment, implement the shared-workspace controls described above. PROJECT_STATUS.md records completed stages, checks, and remaining work so development can resume without overstating readiness.

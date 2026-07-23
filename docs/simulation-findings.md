# ARC Protocol: Commerce Reference-Application Simulation Findings

> **Status:** Exploratory Commerce application findings from mock artifacts only.
>
> These findings are not proof that ARC works. They are observations from small mock Commerce artifacts. The purpose is to expose unresolved protocol, application, governance, approval, reputation, and discovery problems, not to claim success, safety, fraud prevention, fairness, or production readiness.

## Finding #1 — Identity Records Do Not Establish Fulfillment Reliability

The `fake-merchant.json` artifact (legacy filename) models an unanchored newcomer. Merchant Agent A has a mock identity and mock-signed records, but no declared external anchor and no prior standing inputs. The offer is still attractive enough that a human can approve it after warnings are shown.

Attribution helps later review which key produced a record. It does not prove fulfillment reliability. A new merchant without an external anchor or prior evidence may be legitimate, dishonest, operationally immature, or simply unknown. The fixture compares stricter filtering, which may exclude legitimate newcomers, with looser filtering, which may increase fraud exposure.

The absence of reputation does not prove dishonesty. It only leaves risk unresolved at the approval moment.

## Finding #2 — Current Coverage Can Expire or Change

The `stale-offer-approval.json` artifact exposes that human approval is only meaningful if the approved terms are still current. In the mock record, the offer expires at `2026-06-03T12:03:30+09:00 [MOCK]`, while approval is submitted at `2026-06-03T12:04:10+09:00 [MOCK]`.

That approval timestamp matters. The approval Event remains evidence, but the named Commerce lifecycle Projection blocks payment because the target lacked Current Coverage after the offer expired. It then requires refreshed terms from the merchant before any renewed coverage step.

This suggests that an approval record is not permanent coverage for a changed target. Under this Commerce application policy, expired or materially changed offers require new coverage before payment proceeds.

## Finding #3 — The Commerce Policy Withholds Fulfillment Authorization After Payment Failure

The `payment-failure.json` artifact exposes that human approval alone is not enough to begin fulfillment. The human approves a current offer, but the mock payment provider returns `payment_failed_mock`.

The failed-payment record is external provider evidence consumed by the named Commerce lifecycle Projection. When that Projection returns the tested failure state, the application policy withholds merchant and logistics authorization messages: Merchant Agent A receives no fulfillment authorization, and the Logistics Agent receives no delivery authorization. The Projection itself has no authority, and the record does not invalidate an Event or prove what occurred in the world.

This keeps the state boundary visible, but it does not resolve what should happen next. Retry behavior, offer reservation, payment timing, and whether renewed approval is required after a retry remain unresolved.

## Finding #4 — Discovery remains attackable

The `discovery-bias.json` artifact exposes a recommendation-policy problem rather than an anti-advertising rule. Merchant B scores better under the fixture's declared price, delivery-time, and completion-context criteria. Merchant A is still ranked first because of sponsored or preferred backend influence that was not clearly visible before approval.

The issue modeled here is hidden or poorly disclosed ranking influence. Under this fixture's named Commerce policy, approval is paused until the ranking influence and the comparison under the declared criteria are disclosed on the tested review surface.

The artifact does not suggest that every sponsored result is improper. It suggests that opaque sponsored or preferred placement can make a recommendation appear neutral when it is not.

## Finding #5 — Approval quality can degrade

The `approval-fatigue.json` artifact exposes that more human approval prompts do not automatically mean better review quality or stronger authorization evidence. The human receives repeated approval requests in a short period, each with small but material changes to price, delivery time, or cancellation terms.

Several requests are approved quickly. The artifact cannot reliably measure human attention, intent, understanding, or fatigue, but it can record the pattern: repeated approval requests, small material changes, quick approvals, and uncertainty about whether review remained meaningful.

The mock safeguard pauses payment and requires a consolidated re-review of the changed terms. This raises an application design question rather than a solution: when should the Commerce approval flow stop asking for another confirmation and instead require a clearer review surface?

## Finding #6 — Contextual and Provisional Standing Inputs in This Profile

The `baseline-transaction-log.json` and `fake-merchant.json` artifacts compare contextual, evidence-linked standing inputs under this Commerce profile.

The baseline artifact records a fulfilled mock path, but its final state is limited to one mock completion claim. It does not establish general merchant reliability. The unanchored-newcomer artifact records a non-fulfillment claim after a mock payment-confirmation claim; its standing input remains provisional pending governance review. It is a reported failure in authored fixture data, not a final fraud judgment.

Under this profile, a Canon Event used as reputation evidence identifies what is claimed, the transaction context, available evidence sources, and record-check limits. The named Projection treats incomplete evidence as provisional; base ARC does not mandate that reputation policy.

## Open Tensions

- Bootstrap Trust Problem
- Identity ↔ Reputation Loop
- Governance Cold Start
- Discovery transparency vs backend complexity
- Human review vs approval fatigue
- Evidence retention vs privacy

## Current Interpretation

The simulation artifacts do not show that ARC is safe.

They show where the Commerce application and its owning protocol documents need clearer rules, better records, and more explicit limits. The value of this phase is that it exposes failure modes before production use or interoperability claims.

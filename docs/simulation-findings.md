# ARC Protocol: Simulation Findings

> **Status:** Exploratory findings from mock artifacts only.
>
> These findings are not proof that ARC works. They are observations from small mock artifacts. The purpose is to expose unresolved protocol, governance, approval, reputation, and discovery problems, not to claim success, safety, fraud prevention, fairness, or production readiness.

## Finding #1 — Identity does not prevent fraud

The `fake-merchant.json` artifact exposes a bootstrap trust problem. Merchant Agent A has attributable mock identity and signatures, but only basic identity status, no verified claims, and no prior mock reputation events. The offer is still attractive enough that a human can approve it after warnings are shown.

Attribution helps later review what happened. It does not prove fulfillment reliability. A new merchant with weak identity and no reputation may be legitimate, dishonest, operationally immature, or simply unknown. The artifact therefore raises a difficult trade-off: stronger filtering may reduce fake-merchant risk while blocking legitimate new merchants, while weaker filtering may preserve new merchant access but increase fraud exposure.

The absence of reputation does not prove dishonesty. It only leaves risk unresolved at the approval moment.

## Finding #2 — Approval can become invalid

The `stale-offer-approval.json` artifact exposes that human approval is only meaningful if the approved terms are still current. In the mock record, the offer expires at `2026-06-03T12:03:30+09:00 [MOCK]`, while approval is submitted at `2026-06-03T12:04:10+09:00 [MOCK]`.

That approval timestamp matters. The artifact records the approval attempt, but blocks payment because the offer had expired before payment could be requested. It then requires refreshed terms from the merchant before any renewed approval step.

This suggests that approval is not a permanent authorization. Expired or materially changed offers must not proceed to payment without renewed review.

## Finding #3 — Payment failure must stop fulfillment

The `payment-failure.json` artifact exposes that human approval alone is not enough to begin fulfillment. The human approves a current offer, but the mock payment provider returns `payment_failed_mock`.

The artifact blocks merchant and logistics authorization after the failed payment. Merchant Agent A receives no fulfillment authorization, and the Logistics Agent receives no delivery authorization. The final state remains incomplete after payment failure.

This keeps the state boundary visible, but it does not resolve what should happen next. Retry behavior, offer reservation, payment timing, and whether renewed approval is required after a retry remain unresolved.

## Finding #4 — Discovery remains attackable

The `discovery-bias.json` artifact exposes a recommendation problem rather than an anti-advertising rule. Merchant B has the better objective fit in the mock comparison: lower total price, shorter delivery estimate, and stronger relevant mock completion context. Merchant A is still ranked first because of sponsored or preferred backend influence that was not clearly visible before approval.

The important issue is hidden or poorly disclosed ranking influence. Sponsored discovery may be acceptable only when the influence is inspectable and visible before approval. In this artifact, approval is paused pending clearer disclosure of the ranking influence and the objective comparison.

The artifact does not suggest that every sponsored result is improper. It suggests that opaque sponsored or preferred placement can make a recommendation appear neutral when it is not.

## Finding #5 — Approval quality can degrade

The `approval-fatigue.json` artifact exposes that more human approval prompts do not automatically mean stronger human sovereignty. The human receives repeated approval requests in a short period, each with small but material changes to price, delivery time, or cancellation terms.

Several requests are approved quickly. The artifact cannot reliably measure human attention, intent, understanding, or fatigue, but it can record the pattern: repeated approval requests, small material changes, quick approvals, and uncertainty about whether review remained meaningful.

The mock safeguard pauses payment and requires a consolidated re-review of the changed terms. This raises a design question rather than a solution: when should ARC stop asking for another confirmation and instead require a clearer review surface?

## Finding #6 — Reputation must remain contextual and provisional

The `baseline-transaction-log.json` and `fake-merchant.json` artifacts expose why reputation should remain limited, contextual, and evidence-linked.

The baseline artifact records a fulfilled mock path, but its final state is still limited to one mock completion event. It does not establish general merchant reliability. The fake-merchant artifact records non-fulfillment after confirmed mock payment, but its reputation event is provisional pending governance review. It is a reported failure with available mock evidence, not a final fraud judgment.

Context matters. A reputation event should say what happened, in what transaction context, from which evidence sources, and with what verification limits. Where evidence is incomplete, reputation should remain reversible or correctable rather than becoming a universal trust score.

## Open Tensions

- Bootstrap Trust Problem
- Identity ↔ Reputation Loop
- Governance Cold Start
- Discovery transparency vs backend complexity
- Human review vs approval fatigue
- Evidence retention vs privacy

## Current Interpretation

The simulation artifacts do not show that ARC is safe.

They show where ARC needs clearer rules, better records, and more explicit limits. The value of this phase is that it exposes failure modes before implementation.

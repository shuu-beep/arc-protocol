# ARC Protocol: A Survey of Coordination Economics

> **Status:** Exploratory survey note
>
> **Purpose:** Survey the historical economics of protocol adoption *and non-adoption* — giving equal weight to the open standards that died — and test which lessons transfer to ARC's harder, multi-sided case. This is descriptive economics, not a forecast.
>
> This document studies external systems to learn from them, not to claim ARC resembles the winners. Descriptions of those systems reflect ARC's current understanding, omit figures the author cannot stand behind, and may be imprecise or out of date; they are not authoritative.

---

## 1. Why This Document Exists

ARC's incentive corpus has three axes. [`bootstrap-and-incentives.md`](bootstrap-and-incentives.md) maps the **role** gaps — what each network role still lacks. [`adoption-and-defection.md`](adoption-and-defection.md) maps the **actor** inverse — why each party can rationally decline. A third axis is still missing: the **economics** of coordination itself — switching cost, network effect, and the markets for legitimacy, reputation, and interoperability that decide whether an open protocol is adopted or sidelined.

Before writing that synthesis (a future `coordination-economics.md`), this document does the survey it would otherwise smuggle in unstated: it looks at how protocol adoption has actually gone, for open standards that won and open standards that lost. The order is deliberate. An economics doc written without first studying the graveyard would be a theory fit to winners.

This survey makes **no claim that ARC will be adopted.** Asserting an adoption path prematurely is the exact failure mode [threat-model §18.1](threat-model.md) names — adoption incentives are off-ledger and do not fold. The survey's job is narrower and honest: to find which historical mechanisms *could* transfer to ARC, and — more importantly — which cannot, because ARC's case is structurally harder than most of the cases usually cited.

## 2. The Survivorship Trap

Most writing about why protocols succeed studies the survivors and back-derives lessons. The result is a tautology: the protocols that won had whatever the winners had. TCP/IP beat OSI, so "running code beats committees." Git won, so "distributed beats centralized." These read as laws but are selected from one tail of the distribution.

The economics live in the graveyard. For every TCP/IP there is an OSI; for every Web there is Gopher; for every "Login with Google" there is OpenID — *equally open, often better-specified, and displaced.* A lesson that explains only the winners explains nothing, because the losers usually had the same named virtues.

This survey therefore pairs winners with losers and asks what actually differed. The answer, repeatedly, is not openness or technical merit. It is a small set of economic variables: whether an adopter got value *before* the network existed, who paid the switching cost relative to who captured the benefit, and whether some actor had the leverage to force the other side.

## 3. The Variable That Sorts the Cases: Sided-ness

The single most useful lever for reading these cases is how many distinct groups must adopt before *anyone* gets value.

```txt
SINGLE-SIDED   One kind of adopter. Value is largely independent of others
               adopting. Low switching cost, a clear technical or cost win.
               Examples: Git, HTTP-client tooling, MCP, most developer tools.

MULTI-SIDED    Value requires several distinct groups to adopt at once.
               Chicken-and-egg across groups, network effects between them.
               Examples: marketplaces, payment networks, social, EDI, ARC.
```

This distinction is decisive and is the reason the most-cited success stories are the *least* informative for ARC. Git, Linux tooling, and MCP are essentially single-sided developer-coordination wins: a lone adopter benefits immediately, so the network can accrete one rational adopter at a time. ARC is multi-sided — it needs merchants, users, communities, and governance bodies at once ([bootstrap §2](bootstrap-and-incentives.md)) — *and* it asks each to honor an authority, which no developer tool requires. So every lesson below is read twice: once for what it did, and once for whether sided-ness lets it cross to ARC.

## 4. The Winners, and the Lever Each Actually Pulled

Read by economic lever rather than by feature, the canonical open-protocol successes share a short list of mechanisms — and most pulled more than one.

| Protocol | Sided-ness | The lever that actually mattered |
| --- | --- | --- |
| TCP/IP (vs OSI) | single→multi | Free reference implementation (BSD), a captive initial network (ARPANET), and a government/academic forcing function. Running code shipped before the committee finished. |
| The Web (HTTP/HTML) | single-sided to start | Unilateral value: one person could publish one page and benefit alone. View-source made the switching cost near zero. A browser supplied the catalyst. |
| Git | single-sided | Useful to a solo developer with no network at all. An anchor tenant (the Linux kernel) proved it at scale; GitHub later added the multi-sided layer *on top of* a tool that already had solo value. |
| SMTP / email | multi-sided, but | Bootstrapped on an existing captive academic network that was going to interconnect regardless; federation came cheap once the nodes already existed. |
| MCP | mostly single-sided | A major sponsor supplied immediate first-party adoption and a forcing function; the model-plus-tool pairing benefits one integrator at a time. (Recent and unsettled — read with caution, not as a finished result.) |

The recurring threads:

- **Unilateral or small-N value.** The clearest winners paid the adopter *before* the network existed. This is the lever that defeats chicken-and-egg, and it is overwhelmingly a single-sided property.
- **A free reference implementation.** Running code that an adopter can lift at no cost lowers the switching barrier to near zero.
- **An anchor tenant or forcing function.** A captive initial network (ARPANET, the kernel, a sponsor's own products) gave the protocol somewhere to be useful on day one.
- **Low integration cost and a clear win** over whatever it replaced.

## 5. The Graveyard: Equally Open, Did Not Win

The losers are more instructive, because most had openness, good specifications, and even early adoption — and still lost. The pattern that recurs is not failure to launch. It is **defeat after adoption**, by an incumbent with better multi-sided economics.

| Protocol | What happened | The economic cause |
| --- | --- | --- |
| OSI | The de jure standard that lost to TCP/IP. | Design-by-committee, no early running code, no unilateral value. Correctness without deployability. |
| XMPP | Open federated chat — adopted by large players (e.g. Google Talk, Facebook), who later **withdrew federation**. | A multi-sided open protocol can be adopted as a feature and have its interconnection later removed. Whatever the motive, the observable result is the DEFECT exit available at platform scale. |
| RSS | Open, widely deployed syndication — then displaced from mainstream consumer use. | Closed aggregators and social feeds drew users away, and a dominant reader's shutdown removed the convenient client. RSS keeps working and persists in niches (notably podcasting); it was outcompeted by aggregation, not killed. |
| OpenID | Open, well-specified federated identity, with the user free to choose any provider. | The user-chooses-provider model receded as provider-held "Login with Google/Facebook" took over: the closed providers already held the users (anchor tenancy) and offered lower-friction UX. The protocol layer was absorbed — OpenID Connect is widespread — even as the decentralized vision receded. Adoption followed the providers' network position. |
| SOAP / WS-* | A full open stack for web services. | Lost to REST/JSON on integration cost alone. A standard that is expensive to integrate loses to a simpler thing that is not even a standard. |
| ActivityPub / federated social | Open, genuinely adopted — in a niche. | Survives without displacing the incumbents. The social network effect is close to insurmountable; openness wins a refuge, not the market. |

Two cases are worth pulling out because they cut against a naive "open loses" reading:

- **EDI (Electronic Data Interchange)** is a multi-sided B2B standard that *did* achieve wide adoption — because large buyers **mandated** it to their suppliers. Adoption was bought with coercive leverage over one side of the market, not with a better incentive. ARC has no actor with that leverage.
- **The classic standards wars** (VHS vs Betamax, Blu-ray vs HD-DVD) are not open protocols, but they are the cleanest illustration of the multi-sided network-effect endgame: the better-positioned network wins regardless of technical merit. Cited only as analogy, not as a protocol precedent.

## 6. What the Comparison Actually Shows

Lining up §4 against §5, the variables that separated the adopted from the displaced are economic, not technical:

```txt
1. Unilateral value     Winners paid the first adopter before the network
                        existed. Almost every multi-sided open loser lacked this.

2. Switching cost       Who pays vs. who benefits. Winners pushed the cost toward
                        zero (free reference code, view-source, simple formats).

3. Anchor / leverage    A captive initial network, a sponsor's own products, or
                        coercive power over one side (EDI). Open multi-sided
                        protocols that won had one; those that died did not.

4. Integration cost     Complexity kills. SOAP lost to REST on this alone.

5. Reversibility        Adoption is not terminal. XMPP, RSS, and OpenID were
                        adopted and then receded as incumbents who held the
                        users drew them away. Open adoption can be reversed by
                        network power.
```

Variable 5 is the survey's sharpest finding for ARC, and it is drawn from cases, not theory: the DEFECT and FORK exits that [adoption-and-defection §3.2](adoption-and-defection.md) reasons about *a priori* are a recurring outcome for open protocols that touch a market the incumbents want. XMPP's federation was withdrawn; RSS was displaced from the mainstream; OpenID's decentralized model gave way to provider-held login. The inverse framing — "why might a party stop honoring this" — is not pessimism. It is what the record repeatedly shows happening to open protocols at roughly ARC's altitude.

## 7. What Transfers to ARC, and What Does Not

This is the section the guardrail exists for. Each lesson is tested against ARC's actual properties, and the honest result is that most of the famous levers do *not* cross.

- **Unilateral value — the most important lever — barely transfers.** ARC is multi-sided, so the Git/Web recipe of "benefit alone, then accrete" is mostly unavailable. The one thin thread: an ARC audit log has *some* solo value — a party can record and recompute its own agent's approvals without anyone else participating ([adoption §4.2](adoption-and-defection.md)). Whether that solo value is large enough to seed adoption is unknown and unmeasured; it is a hypothesis, not a path.
- **Anchor tenant and coercive leverage do not transfer at all.** ARC has neither a captive initial network nor an actor who can mandate it to the other side the way large buyers mandated EDI. This is the same structural disadvantage [landscape §10](landscape-and-positioning.md) already names: the closed path has the head start because it already owns the users, the merchants, and the payment relationship.
- **Free reference implementation transfers — weakly.** ARC has executable probes and a reference client, which is the running-code lever TCP/IP used. But running code defeats *single-sided* switching cost; it does nothing about the multi-sided chicken-and-egg. Free code is necessary, not sufficient, and the cases bear this out (OSI had no code; OpenID had plenty).
- **The graveyard's warning transfers most strongly of all, and it is a warning, not a recipe.** XMPP/RSS/OpenID suggest that *achieved* open adoption can be reversed when an incumbent holds the multi-sided network. This directly weakens [adoption §4.6](adoption-and-defection.md)'s "open spec as counter-pressure": openness did not, on its own, save any of the three. A fork is a real check only when the fork is *viable*, and viability needs the network effect the open loser never had. In these cases openness was as readily a route to exit as a deterrent against capture.

The honest terminal of the survey: it yields **no adoption path.** It yields a sharper map — that ARC is structurally similar to the multi-sided open losers, and dissimilar to every single-sided winner, *unless* a specific lever can be found: a narrow anchor community, a measured-low integration cost, or a real solo-value case for the audit overlay. Each of those is a hypothesis already held open in [adoption §4](adoption-and-defection.md) and tested by [pilot-design.md](pilot-design.md). The survey does not resolve them; it tells us which ones are load-bearing.

## 8. What This Feeds

A later `coordination-economics.md` would take these findings and examine ARC's specific markets, each seeded by a finding above:

```txt
Switching cost        §6 var. 2 — who pays vs. benefits when a merchant or
                      user moves between communities or off ARC entirely.
Legitimacy market     §5 EDI/anchor — where the leverage to be honored comes
                      from when ARC has no coercive actor.
Reputation market     §6 var. 5 — portable reputation as the thing an incumbent
                      displaces, as RSS and OpenID's open models were displaced.
Interoperability      §7 — federation as XMPP's lesson: the bridge that lets a
                      big player embrace, then de-federate.
```

That synthesis remains deferred. This document is the evidence base it would otherwise lack — and the discipline it imposes is the same one [adoption-and-defection.md](adoption-and-defection.md) ends on: a protocol cannot learn from the adoption it imagines, and it cannot be saved by the openness the graveyard already buried.

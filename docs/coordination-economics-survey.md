# Preliminary Coordination-Economics Comparisons for ARC's Commerce Application

> **Status:** Preliminary, unsourced application-research comparison
>
> **Purpose:** Record selected protocol-adoption and non-adoption comparisons, then identify hypotheses that may be relevant to ARC's multi-sided Commerce application. This is not a literature survey, evidence base, or forecast.
>
> This document studies external systems without claiming ARC resembles the adopted cases. Descriptions reflect ARC's current understanding, may be imprecise or out of date, and are not authoritative.
>
> This comparison note contains no respondent data and validates neither ARC Canon nor adoption.

---

## 1. Why This Document Exists

ARC's incentive corpus has three axes. [`bootstrap-and-incentives.md`](bootstrap-and-incentives.md) maps the **role** gaps — what each network role still lacks. [`adoption-and-defection.md`](adoption-and-defection.md) maps the **actor** inverse — why each party may decline. A third axis concerns coordination economics: switching cost, network effects, and incentives around authority recognition, reputation, and interoperability that may affect whether an open protocol is adopted or sidelined.

Before writing that synthesis (a possible future `coordination-economics.md`), this document records selected adoption and non-adoption examples for later review.

This note makes **no claim that ARC will be adopted.** Event records do not establish adoption incentives ([threat-model §18.1](threat-model.md)). Its narrower purpose is to compare which mechanisms might or might not transfer to the Commerce application.

## 2. Selection Bias in Case Comparison

Success-only comparisons can overstate the generality of factors associated with adopted protocols. Familiar summaries such as "running code beats committees" or "distributed beats centralized" should therefore be treated as hypotheses rather than laws.

Selected counterexamples include OSI, Gopher, and decentralized OpenID usage. Their histories differ, so this note does not claim that they were technically equivalent or displaced for one shared reason.

This note pairs selected examples to identify candidate variables: whether an adopter received value before a network existed, who paid switching costs relative to who captured benefits, and whether an actor had leverage over another side. The comparison does not isolate causes.

## 3. One Comparison Axis: Sided-ness

One useful axis is how many distinct groups must adopt before participants receive value.

```txt
SINGLE-SIDED   One kind of adopter. Value is largely independent of others
               adopting. Low switching cost, a clear technical or cost win.
               Examples: Git, HTTP-client tooling, MCP, most developer tools.

MULTI-SIDED    Value requires several distinct groups to adopt at once.
               Chicken-and-egg across groups, network effects between them.
               Examples: marketplaces, payment networks, social, EDI, ARC's Commerce application.
```

Sided-ness is material but not decisive. The examples below provisionally classify Git, Linux tooling, and MCP as primarily developer-facing, while the Commerce application may involve merchants, users, communities, and governance bodies ([bootstrap §2](bootstrap-and-incentives.md)). These are comparison categories, not measured findings, and they characterize application economics rather than the authority protocol itself.

## 4. Selected Adoption Examples and Candidate Factors

The table records factors often associated with selected adoption examples. It is preliminary and does not establish causation.

| Protocol | Provisional sided-ness | Candidate factors often cited |
| --- | --- | --- |
| TCP/IP (vs OSI) | single→multi | Reference implementations, an initial network, and institutional adoption are commonly cited; their relative effects require sourcing. |
| The Web (HTTP/HTML) | single-sided to start | Early publishing and browsing could provide small-N value; simple inspection and tooling may have lowered experimentation cost. |
| Git | single-sided | Solo use provided immediate value; use by the Linux kernel and later hosting platforms may have supported broader adoption. |
| SMTP / email | multi-sided | Existing academic networks provided an initial environment for interconnection. |
| MCP | mostly single-sided | First-party sponsorship and per-integrator tool value may matter; the case is recent and unsettled. |

Candidate themes, not causal findings:

- **Unilateral or small-N value.** Early adopters may receive value before a broader network exists.
- **A usable reference implementation.** Running code may lower evaluation and switching costs.
- **An anchor participant or institutional requirement.** An initial network or sponsor may supply early use.
- **Lower integration cost or a clear local benefit.** Both may reduce adoption friction.

## 5. Selected Non-Dominant or Reconfigured Paths

The examples below followed different trajectories despite some degree of specification, implementation, or adoption. No single recurring cause is established here.

| Protocol | Observed path | Possible contributing factors |
| --- | --- | --- |
| OSI | Did not become the dominant deployed internetworking suite. | Timing, implementation availability, institutional choices, and deployment cost are candidate factors requiring sources. |
| XMPP | Some large services later withdrew federation. | Platform incentives and control of user networks may have affected continued interconnection. |
| RSS | Persists, but receded from some mainstream consumer surfaces. | Aggregator changes, reader shutdowns, and shifts toward social feeds may have contributed. |
| OpenID | Decentralized provider choice receded while OpenID Connect became widespread. | Provider-held identity, user experience, and existing account networks may have influenced the change. |
| SOAP / WS-* | Remains in use but lost mindshare in many web API contexts to simpler HTTP/JSON approaches. | Integration complexity is one candidate factor, not an isolated cause established here. |
| ActivityPub / federated social | Achieved adoption without displacing dominant centralized networks. | Network effects, moderation, user experience, and operating cost are candidate factors. |

Two cases are worth pulling out because they cut against a naive "open loses" reading:

- **EDI (Electronic Data Interchange)** is often described as a multi-sided B2B standard whose adoption was supported in part by buyer mandates. That account requires sourcing; no comparable actor has been identified for ARC's Commerce application.
- **The classic standards wars** (VHS vs Betamax, Blu-ray vs HD-DVD) are not open protocols. They illustrate that network position may matter, but the comparison is only an analogy.

## 6. Candidate Variables from the Comparison

The selected comparisons suggest variables to investigate; they do not separate economic from technical causes:

```txt
1. Unilateral value     Whether an early adopter receives value before a broader
                        network exists.

2. Switching cost       Who pays relative to who benefits, and whether tooling or
                        simple formats reduce evaluation cost.

3. Anchor / leverage    Whether an initial network, sponsor, or institutional
                        requirement supplies early use.

4. Integration cost     Whether implementation and operating complexity affects
                        adoption in a particular context.

5. Reversibility        Adoption and federation can change over time; XMPP, RSS,
                        and OpenID illustrate different forms of reconfiguration.
```

One relevant hypothesis is that adoption and interconnection are reversible. The XMPP, RSS, and OpenID examples motivate asking why a party might stop honoring a shared arrangement, but this note does not establish a common cause or show that ARC is at the same "altitude."

## 7. What Transfers to ARC's Commerce Application, and What Does Not

The comparisons support hypotheses to test against the Commerce application's declared properties; they do not establish that a mechanism transfers.

- **Unilateral value is a hypothesis to test.** An internal ARC approval/audit record may provide solo value because a party can record and recompute its own agent's approvals ([adoption §4.2](adoption-and-defection.md)). The [refusal-recording probe](../examples/refusal-recording-demo/) only shows that, under its declared synthetic categories, this candidate is aimed at `REJECT` rather than a mutual-`WAIT` case. It does not establish adoption value.
- **No comparable anchor actor is identified.** The current Commerce research names no actor that can mandate adoption across participant groups.
- **Executable material may lower evaluation cost.** ARC's executable corpus and reference client are not a production reference implementation, and no adoption effect is established.
- **Reversibility remains a candidate risk.** The selected examples motivate testing whether openness and forkability create useful counter-pressure, viable exit, or neither in a Commerce deployment.

This preliminary comparison yields no adoption path and does not establish structural similarity between ARC's Commerce application and any selected case. It identifies hypotheses for a narrow anchor community, measured integration cost, and possible solo value of the audit overlay. Those remain open in [adoption §4](adoption-and-defection.md) and [pilot-design.md](pilot-design.md).

## 8. What This Feeds

A later `coordination-economics.md` could examine candidate questions suggested above:

```txt
Switching cost        §6 var. 2 — who pays vs. benefits when a merchant or
                      user moves between communities or off ARC entirely.
Authority recognition §5 EDI/anchor — what could motivate participants to
                      honor a shared arrangement when no mandate is identified.
Reputation market     §6 var. 5 — portable reputation as the thing an incumbent
                      displaces, as RSS and OpenID's open models were displaced.
Interoperability      §7 — whether a dominant participant can join and later
                      withdraw federation.
```

That synthesis remains deferred. This document is a preliminary comparison note, not an evidence base. Any later synthesis would need sources and empirical deployment data.

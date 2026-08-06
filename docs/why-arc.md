# Why ARC?

> Authenticated is not authorized. Tool access is not current authority. ARC
> determines whether an exact action remains authorized under signed,
> revocable, and potentially conflicting authority records.

ARC addresses a different question from request authentication, access control,
tool discovery, and execution infrastructure. Those layers can all succeed
while the authority records relevant to one exact action remain causally
contested. ARC is an authority-evidence layer beside those systems, not a
replacement for them.

## Three boundaries

| Technology | What it establishes or controls | ARC's separate question | Relationship |
| --- | --- | --- | --- |
| Web Bot Auth | Uses cryptographic HTTP message signatures to verify that a request came from an automated bot associated with a signing key. | Under whose current delegated authority may that sender perform this exact action? | Complementary |
| OAuth / Cloudflare Access | Controls access using tokens, scopes, identities, groups, application policies, or service credentials. A centralized authorization server may be sufficient when it is the current source of truth. | Do portable authority records from one or more issuers still provide current coverage after delegation, revocation, challenge, adjudication, or causal conflict? | Partly overlapping, often complementary |
| MCP / Cloudflare execution runtime | MCP connects clients to discoverable tools. Workflows provides durable multi-step execution; Browser Run and Sandbox provide browser or isolated code-execution environments. | Immediately before dispatch, what current delegated authority and decision provenance cover the exact action? | Complementary |

Cloudflare's documentation describes [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/)
as request authentication using cryptographic signatures. [Cloudflare Access
policies](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/)
control who may reach an application, including OAuth-linked tokens and service
credentials. Cloudflare's [MCP documentation](https://developers.cloudflare.com/agents/tools/mcp/)
covers connecting to servers and using their tools. [Workflows](https://developers.cloudflare.com/workflows/),
[Browser Run](https://developers.cloudflare.com/agents/tools/browser/), and the
[Sandbox SDK](https://developers.cloudflare.com/sandbox/) address durable,
browser-based, or isolated execution.

None of those descriptions makes the systems inferior to ARC. They answer
different operational questions. OAuth and Access can also be the complete
authorization solution when one central policy service has the necessary,
current authority state.

## Five-minute simulated experiment

The ARC Execution Gate
[`simulated_software_deployment`](https://github.com/shuu-beep/arc-execution-gate/tree/main/examples/simulated_software_deployment)
example holds the request and application policy constant while changing only
the supplied ARC authority evidence.

The fixture first declares these external boundary conditions:

- request authentication: `VALID`
- OAuth token and scope: `VALID`
- deploy tool access: `AVAILABLE`

They are fixture values only. The example does not connect to Web Bot Auth,
OAuth, Cloudflare Access, MCP, or a Cloudflare API.

### Scenario A: contested authority

A root signer and its registered successor each have a matching current
deployment mandate. The key rotation causally precedes the successor mandate,
but neither mandate causally succeeds or nullifies the other. Their timestamps
do not select a winner.

ARC Reference Core returns:

```text
coverage_status: CONTESTED
reason_code: ARC_REF_MULTIPLE_MATCHING_AUTHORIZATIONS_CONTESTED
```

The application-owned Execution Gate maps that non-authoritative coverage to a
local decision:

```text
GateDecision: DENY
dispatch_allowed: false
adapter invocation count: 0
```

Reference Core does not return `DENY` and does not create a `GateDecision`.

### Scenario B: resolved authority

The fixture adds a successor-signed `AUTHORIZE consent.withdraw` that causally
follows the rotation and successor mandate and nullifies the root mandate. This
uses the current Reference Core's supported authorization semantics; it does not
add a new Event type or interpret `ADJUDICATE` as deployment authorization.

Reference Core then returns `COVERED_BY_MANDATE`. The Gate applies the unchanged
staging policy, creates `ALLOW`, and calls the process-local adapter once. Its
single mock receipt proves only that the mock adapter was invoked. It does not
prove a Cloudflare deployment or any external execution.

Run it with sibling checkouts of ARC Reference Core and ARC Execution Gate:

```sh
git clone https://github.com/shuu-beep/arc-reference-core.git arc-reference-core-alpha
git clone https://github.com/shuu-beep/arc-execution-gate.git
cd arc-execution-gate
PYTHONPATH=../arc-reference-core-alpha/src \
  PYTHONDONTWRITEBYTECODE=1 \
  python3 examples/simulated_software_deployment/demo.py
```

## When ARC may be unnecessary

ARC may add little value when:

- one central IAM service is always the current authority source;
- authority evidence does not need to move between organizations or
  implementations;
- delegation lineage, challenge, adjudication, and causal conflict do not need
  to be preserved or recomputed; or
- OAuth scope plus local application policy fully answers the authorization
  question.

## What this experiment does not prove

The current integration is structural-only. It does not verify signatures or
establish root trust, key provenance, evidence completeness, identity, or
real-world execution. Replay prevention and mock receipts are process-local
Execution Gate behavior, separate from Reference Core authority projection.

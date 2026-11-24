---
title: "Outlook: Observability — run records, robot telemetry, agent traces"
purpose: Landscape survey of observability options across three distinct layers (physical telemetry, agent decisions, visual failure triage), with a verified assessment of Foxglove, Rerun, MCAP, Arize Phoenix, Langfuse, Pydantic Logfire and Nomadic.
authority: Research (INFORMATIONAL — not requirements)
created: 2026-08-11
updated: 2026-08-11
---

# Outlook: Observability — run records, robot telemetry, agent traces

## Concept

"Observability" for this project is not one problem. Bundling it into a single
tool choice produces the wrong answer, because three genuinely different
questions are being asked of three differently-shaped datasets:

| Layer | Question | Data shape | Tool family |
|-------|----------|------------|-------------|
| **1. Physical telemetry** | What did the body do? | Continuous, multi-modal, spatial — joint angles at 10s–100s Hz, camera frames | MCAP substrate + Foxglove / Lichtblick / Rerun as viewers |
| **2. Agent decisions** | Why did it choose that? | Discrete, hierarchical — prompts, tool calls, tokens, eval scores | Arize Phoenix / Langfuse / Logfire |
| **3. Visual failure triage** | What went wrong on camera? | Hours of unattended footage, sparse events | Nomadic, or seek-by-timestamp into a run journal |

No tool spans two layers well. Neither Foxglove nor Rerun has a usable
OpenTelemetry bridge, and none of the LLM platforms render 3D scenes or
hundred-Hz joint streams. Where the layers must meet — correlating "the agent
chose 25 µL" with "the gantry moved here" — the mechanism is a **shared run ID
and timestamp**, not a shared tool.

## Current state (verified 2026-08-11)

Establishing the baseline, because most of what the roadmap implies is not
built:

- **Logging:** stdlib `logging` only. Every module in `src/so101/` and
  `src/dashboard/server.py` uses `logger = logging.getLogger(__name__)`. No
  structlog, no JSON logging, **no correlation/run/trace IDs anywhere**.
  `logging.basicConfig` is called only in two CLI entry points
  (`cli/coordinate_cmd.py`, `cli/run_demo.py`); the dashboard inherits whatever
  uvicorn configures.
- **Run journal: does not exist.** No journal, checkpoint, resume, sqlite or
  jsonl persistence in `src/`. `workflow.uc6_eln_logged_experiment()` creates
  one coarse eLabFTW record per run and patches its final status — no per-well
  ledger, no timestamps, no resume.
- **Metrics: none.** No `/metrics`, no Prometheus, no OpenTelemetry. The HTTP
  surface is `/`, `/api/status` and `/ws`. `/api/status` returns only
  `{mode, e_stopped, connected, arm_ids}`. The WebSocket is request/response —
  there is no server-initiated telemetry push.
- **Foxglove:** optional dependency group (`foxglove-sdk`, `scipy`,
  `yourdfpy`), implemented solely in `src/so101/cli/foxglove_viz.py`, excluded
  from coverage and from pyright strict. CLI path only — no library module
  imports it. Makefile carries a `TODO: unvalidated on hardware`.
- **Rerun:** not a declared dependency. Present only transitively via
  `lerobot`, and driven by `lerobot-teleoperate --display_data=true`, not by
  this repo's code.
- **LLM/agent code: none.** No `anthropic`, `openai`, `langchain` or
  `pydantic-ai` import exists in `src/` or `tests/`. The *decide* link of the
  closed loop (see [roadmap.md](roadmap.md), "Two tracks") is unbuilt.

## Layer 1 — Physical telemetry

### Foxglove is no longer open source

The most actionable finding in this survey. Foxglove Studio's last OSS release
was v1.87.0 (Feb 2024) and the `foxglove/studio` repo was
[archived in July 2024](https://github.com/foxglove/studio). Foxglove 2.0 is
fully closed-source, and per [their pricing](https://foxglove.dev/pricing)
**self-hosted deployment is Enterprise-tier only** (Free: 10 GB / 3 users /
5 devices; Pro: $20/mo + usage, then $42/user/mo).

- **Relevance:** direct — `foxglove-sdk` is in an optional group today, in a
  repo whose thesis is open and self-hostable. That is a live inconsistency
  worth a deliberate decision rather than drift.
- **Feasibility of alternatives:** [Lichtblick](https://github.com/lichtblick-suite/lichtblick)
  (MPL-2.0, actively maintained) continues the OSS lineage and reads the same
  files.

### MCAP is the durable substrate

[MCAP](https://mcap.dev/) is **MIT-licensed** (verified against
`foxglove/mcap`'s LICENSE file, © Foxglove Technologies Inc) — a modular,
serialization-agnostic, chunked, self-describing container format with schemas
embedded. Crucially it is **unaffected by the Studio pivot**: the repo is not
archived and remains actively maintained, with official reader/writer libraries
across several languages.

Foxglove's "record once, read forever" durability promise and MCAP's role as a
ROS 2 recording format are the vendor's claims, repeated here but not
independently verified.

- **Design intent:** record MCAP **once** as the source of truth, and treat
  every viewer as a replaceable frontend. This hedges precisely the vendor risk
  Foxglove already demonstrated once. `foxglove_viz.py` already calls
  `foxglove.open_mcap()`.

### Rerun

[Rerun](https://github.com/rerun-io/rerun) is MIT/Apache-2.0 dual-licensed and
very active. Its own README warns "expect breaking changes" — it is optimised
for live interactive debugging, not archival immutability. MCAP read support is
experimental.

- **Relevance:** fine as a teleop viewer, which is exactly how it is used
  today. Not a durable-record system.
- **Redundancy:** running both Rerun and Foxglove is redundant for the *record*
  but harmless for *live viewing* — a UX preference, not a data-architecture
  requirement.

## Layer 2 — Agent decisions

Deferred until the *decide* link exists. Recorded here so the decision is not
re-researched later.

| Option | License / self-host | Verdict |
|--------|--------------------|---------|
| **Arize Phoenix** | [Elastic License 2.0](https://arize.com/docs/phoenix/self-hosting/license) (source-available, not OSI); `arize-phoenix-otel` is Apache-2.0. Self-host is genuine and unrestricted for internal use — single container | **First choice.** Lightest ops, OTel-native (OpenInference is an OTel semconv extension), tracing + evals + experiments included, no framework lock-in |
| **Langfuse** | MIT for all product features | **Runner-up.** Cleanest license match for an Apache-2.0 project; cost is a four-service stack (Postgres + ClickHouse + Redis + S3-compatible) |
| **Pydantic Logfire** | SDKs open; server closed. Self-host is [Enterprise-only](https://pydantic.dev/logfire) | Best stylistic fit (Python-first, OTel-native, `pydantic` already a core dep) but **disqualified as system of record** under the self-hostable thesis. Viable as a hosted option if that constraint is relaxed |
| **LangSmith** | No self-host below [custom-priced Enterprise](https://www.langchain.com/pricing-langsmith); per-seat | Poor fit — the closed-SaaS/per-seat pattern this project positions against |
| **W&B Weave** | Self-host story unresolved (contradictory sources) | Only compelling if training/fine-tuning already lives in W&B |
| **Raw OTel GenAI semconv** | Fully open, any backend | Complement, not a starting point — the GenAI conventions are still Development status with no stable release, and there is no built-in eval tooling |

**Not either/or:** Phoenix and Langfuse both export OTLP, so spans can be
dual-exported to a generic backend for whole-system correlation while the
LLM-specific platform stays the system of record.

## Layer 3 — Visual failure triage

### Nomadic (NomadicML Inc, d/b/a Nomadic AI)

Positions as ["The Understanding Layer for Physical AI"](https://www.nomadicai.com/) —
products **Find**, **Monitor**, **Curate** over operational video. Solutions
lead with Robotics → Industrial / Humanoid, with published examples for
"Failures and Edge Cases", "Action Segmentation", "Discrete Pick and Place" and
"VLA Annotation".

- **Relevance:** genuine and higher than first assumed. Pick-and-place failure
  discovery is structurally the same problem as "which well did the gantry miss
  at 03:00", and this repo already has multi-camera capture in `camera.py`. The
  VLA-annotation angle would also feed the LeRobot/ACT training path.
- **Self-host:** a real, well-documented
  [VPC deployment](https://docs.nomadicml.com/getting-started/vpc-setup) exists
  (Terraform, AWS or GCP, no public ingress required). But it needs a cloud
  account, GPU inference (SageMaker or a private endpoint), and Nomadic to run
  the deploy — *"contact your Nomadic representative"*. Even a private instance
  is keyed by a Firestore collection issued by a Nomadic admin.
- **Feasibility:** low for now. That is data sovereignty ("your cloud instead of
  ours"), not self-hosting on a bench, and it solves a compliance problem this
  project does not have. Pricing is [Free trial or Enterprise](https://www.nomadicai.com/pricing)
  only — the free tier is 1 week / 30 minutes of analysis.
- **Openness:** the GitHub org `nomadic-ml` has **0 public repos**. The only
  public artifact is the [`nomadic` PyPI client](https://pypi.org/project/nomadic/)
  (v0.1.58, MIT classifier, last upload 2026-07-31), a thin client for a closed
  API. Its summary still reads "Python SDK for NomadicAI's DriveMonitor API" —
  a name absent from current marketing, i.e. stale packaging metadata.
- **Compatibility watch-out:** SDK docs state Python 3.8–3.11 and classifiers
  stop at 3.11, though `requires_python` is `>=3.8`. This repo targets 3.12 —
  untested rather than blocked.

## Decision: build the run journal first

The gap is not a vendor. It is the run journal the roadmap already names and
the code does not have. In priority order:

1. **Run journal** — append-only JSONL or SQLite: every aspirate/dispense with
   well, volume, timestamp. Unblocks checkpoint/resume, and is the audit trail
   that answers "why this volume". Vendor-independent.
2. **Thread a `run_id`** through logging now. Cheap today; it is the
   correlation key every later option requires.
3. **MCAP as substrate** for physical telemetry, viewers kept swappable.
4. **Defer layers 2 and 3** until the *decide* link exists and there is real
   footage to triage.

A per-well timestamped journal also delivers most of layer 3's value at zero
cost — it lets an operator seek straight to the failure instead of scrubbing
six hours of video.

## Sourcing and confidence

- **Verified at primary source (2026-08-11), by fetching the artifact itself:**
  - Licenses, from each repo's own LICENSE file: MCAP **MIT**; Arize Phoenix
    **Elastic License 2.0**; Rerun **Apache-2.0** (dual MIT); Langfuse **MIT
    except `ee/`, `web/src/ee/`**.
  - `foxglove/studio` is archived — the repo states *"archived by the owner on
    Jul 18, 2024"*.
  - Foxglove tier limits, from the pricing page: Free = 10 GB / 3 developer
    seats / 5 devices / 3 projects; Pro = $20/mo + usage, 3 seats then
    $42/user/mo, 5 devices then $20/device/mo; **"Self-hosted data" and
    "On-premises deployment" appear only in the Enterprise column**.
  - Logfire, from its own FAQ: *"the server application and UI are closed
    source... the Enterprise plan includes self-hosted deployment options"*;
    Free 10M spans/mo, Team $49/mo, Growth $249/mo.
  - Rerun's maturity caveat is its README verbatim: *"We are in active
    development... Expect breaking changes!"*
  - Nomadic: product surface, pricing tiers, VPC docs, PyPI metadata, and the
    empty `nomadic-ml` GitHub org.
  - This repo's current state — read from code with a content search, not from
    its docs.
- **Corrected on re-audit:** MCAP was first written here as Apache-2.0. It is
  MIT. The error came from accepting a research summary without checking the
  LICENSE file.
- **Lower confidence — NOT independently verified:** commercial pricing for
  Arize AX (arize.com returned HTTP 403); the ClickHouse acquisition of
  Langfuse (Jan 2026, aggregator-sourced); W&B Weave's self-hosting terms
  (contradictory sources, unresolved); the OTel GenAI semconv stability status;
  Phoenix's and Langfuse's operational footprints (one container vs. four
  services) — both are vendor-documented, not deployed and measured here.
- **Decay warning:** vendor pricing and licensing move fast, and this survey
  turns on exactly those facts. Re-verify licensing and self-host terms before
  acting on any recommendation here — Foxglove's 2024 pivot is the cautionary
  precedent.

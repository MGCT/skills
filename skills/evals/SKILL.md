---
name: evals
description: Design and implement evaluations for an AI/LLM feature — scope what's being measured, build a labelled case set, choose a scoring method, run it with proper variance, and read the results. Use whenever the user types /evals, or asks to "set up / design / build evals", "how do I test this AI feature / prompt / agent", "measure / validate the model's output", "is the prompt actually better", "build an eval set / test harness for the LLM", "LLM-as-judge", "measure accuracy of the classifier / summariser / RAG". It scopes the capability and the failure modes that matter, designs representative + adversarial cases (stored under tests/), picks scoring to fit the task (exact/assertion, LLM-as-judge with a rubric, or human), and — because LLM outputs are stochastic — runs each case several times and reports mean + variance + confidence interval, not a single number. For current Claude model ids to use as the system- or judge-model, consult the claude-api skill rather than hardcoding them. This is engineering evals for the user's AI product; distinct from /contradictions (auditing document claims) and from research/strategy validation.
argument-hint: "[the AI feature/capability to evaluate]"
allowed-tools: Read Grep Glob Bash Write Edit
---

# Evals

An eval is the difference between "the new prompt feels better" and "the new prompt lifts
the pass-rate from 71% to 84% (±4)". Without one, every change to an AI feature is a guess,
and regressions ship silently because nobody can see them. With one, you can change a
prompt, a model, or a retrieval step and *know* whether it helped. This skill builds that
instrument for a specific AI capability in the project: it scopes what to measure, assembles
the cases, picks how to score them, and runs it so the result is trustworthy rather than a
lucky single sample.

Two things make LLM evals different from ordinary tests and are easy to get wrong. First,
**the output is stochastic** — the same input scores differently across runs — so a single
run is noise, and any honest result is a distribution (mean + variance), not a number.
Second, **the interesting outputs are open-ended**, so scoring often needs an LLM judge,
which is itself a fallible model you have to validate. This skill is built around both.

Know what this is *not*:

- **Not [[contradictions]].** That audits the *claims in a document* for conflict or factual
  error. This measures an *AI system's behaviour* over a dataset.
- **Not research/strategy validation.** This is engineering evaluation of an AI/LLM product
  — datasets, scorers, metrics — not "did the strategy achieve its business goal".
- **Not the repo's `skill-creator` eval feature**, which benchmarks *skills in this repo*.
  It shares the variance-analysis discipline (and is worth reading for it), but `/evals`
  targets the user's own AI feature in their project.

## 1. Scope what you're measuring

An eval is only as good as the question it asks. Before any cases, pin down:

- **The capability under test** — the specific thing the AI does (classify a ticket,
  summarise a document, answer from retrieved context, call the right tool).
- **What "good" and "bad" look like** — the concrete success criteria, and the **failure
  modes that matter** (hallucination, wrong tool, missed edge case, unsafe output). The
  eval must be able to catch the failures you actually fear.
- **The decision it informs** — ship/don't-ship, prompt A vs B, model choice. The metric
  should move that decision.

## 2. Build the case set

Cases are the durable asset — they outlast any prompt or model. Assemble them under the
repo's `tests/<feature>/` convention as data (JSONL is convenient: input + expected
behaviour/label per line). Make the set earn its trust:

- **Representative** of real inputs, not just tidy ones.
- **Adversarial** — include the known failure modes and edge cases on purpose. A
  clean-only set reports a flattering number that production will refute.
- **Labelled** — each case carries the expected output, or the rubric criteria a good
  answer must meet.
- **Held-out discipline** — keep a slice you don't look at while iterating, so you can tell
  genuine improvement from overfitting to the eval.
- **Enough for signal** — a handful of cases can't distinguish 80% from 90%. Size to the
  precision the decision needs.

## 3. Choose how to score

Match the scorer to the task — cheapest reliable method wins:

- **Exact / assertion** — deterministic checks (exact match, regex, JSON-schema, "contains
  X", a unit test on a tool call). Best for structured or closed outputs. Cheap, stable,
  no judge needed — prefer it whenever the output allows.
- **LLM-as-judge** — for open-ended output (summaries, answers, tone). Give the judge an
  **explicit rubric** (the criteria + what a 0/1 or 1–5 means), pin its **model** (use a
  current Claude model — get the id from the `claude-api` skill), and **validate the judge**
  against human labels on a sample before trusting it at scale. An unvalidated judge just
  moves the guesswork.
- **Human** — for the highest-stakes or most subjective calls; expensive, so reserve it and
  often use it to calibrate a judge.

## 4. Run it — with variance

Write the runner in the project's stack (it calls the product's API/prompt — that part is
project-specific). The discipline that's universal: **run each case several times** (3–5+),
because a single run of a stochastic system is noise. Emit one record per case-run as JSONL
(`{"case": "...", "score": 0/1 or 0..1}`) and aggregate:

```
python <skill-dir>/scripts/aggregate.py results.jsonl --threshold 0.5
```

It reports the mean, **stdev and 95% CI**, the pass-rate at your threshold, the
lowest-scoring cases, and — critically — the **flaky cases** that pass on some runs and fail
on others, which a single-number report hides. Report the interval, not just the mean.

## 5. Interpret and iterate

- **Read the failures, not just the score.** Cluster the low and flaky cases — they usually
  share a root cause (a prompt gap, a retrieval miss, an ambiguous instruction).
- **Change one thing, re-run, compare** — prompt, model, or retrieval, against the *same*
  cases. Use the CI: a 2-point move inside a ±5 interval isn't a real gain.
- **Don't overfit.** Improving until the dev set is perfect just teaches the prompt the
  test. Validate on the held-out slice; grow the case set as new failure modes appear.
- **Track it over time** so regressions are visible on the next change.

## Bundled files

- `scripts/aggregate.py` — turns per-case-per-run JSONL into metrics **with variance**
  (mean, stdev, 95% CI, pass-rate, flaky-case detection). Pure stdlib.
  `python scripts/aggregate.py results.jsonl [--threshold T] [--json]`.

## Principles

- **Report a distribution, never a single number.** LLM outputs are stochastic; one run is
  noise. Mean ± CI, and surface the flaky cases — a result without variance is not a result.
- **Measure the failure you fear.** The metric must be able to catch the real failure mode,
  not just the easy-to-score surface. An eval that can't fail on hallucination doesn't
  measure hallucination.
- **Prefer the cheapest reliable scorer.** Exact/assertion over a judge whenever the output
  allows; a judge only when open-endedness demands it — and then validate the judge.
- **Cases are the asset.** Invest in representative, adversarial, labelled cases; they
  outlast every prompt and model. Keep a held-out slice.
- **Don't overfit the eval.** Iterate on dev, validate on held-out. An eval you've tuned
  against has stopped measuring anything.
- **Get model ids from `claude-api`.** Don't hardcode model names that go stale; pull the
  current ones when you need a system- or judge-model.

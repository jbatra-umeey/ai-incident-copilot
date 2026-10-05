# Architecture decisions

## Measure before explaining

The model receives computed evidence rather than estimating numeric regressions from free-form logs. Statistical calculations remain deterministic.

## Match relevant cohorts

Workflow and device-tier grouping prevents the demo from interpreting a simple device-mix shift as a within-tier slowdown. More confounders must be controlled in production.

## Keep actions under review

This workflow stops at an evidence-linked hypothesis. It exposes no rollback or ticketing tool, avoiding accidental side effects from an uncertain explanation.

## Next engineering step

Add read-only telemetry adapters, release metadata, confidence intervals and labeled historical incidents. Evaluate hypothesis usefulness with engineer review.

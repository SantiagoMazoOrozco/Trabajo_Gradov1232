Grafana dashboards stubs for the project. Import these JSON files into Grafana (or mount this folder into the Grafana container) and adjust datasource UIDs.

- performance.json: CPU/mem/time/throughput per stage.
- energy.json: Power and energy-normalized metrics (if RAPL available).
- resilience.json: Fault injection, recovery counts and MTTR.

Datasource assumptions: Prometheus (UID: prom) and possibly CSV/JSON ingest via plugins for offline views.

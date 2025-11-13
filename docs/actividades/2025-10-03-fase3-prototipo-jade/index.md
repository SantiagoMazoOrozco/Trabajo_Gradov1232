# Fase 3: Prototipo (JADE/JVM)

En esta fase iniciamos el prototipo con un orquestador en Java que invoca el puente CLI en Python.
Esto permite integrar gradualmente JADE sin reescribir la canalización existente.

Componentes nuevos:
- `jade-platform/` (Maven):
  - `App.java`: punto de entrada; lee `EXPERIMENT_ID` y `SEED`.
  - `CoordinatorAgent.java`: orquesta `preprocess -> train(RF,SVM) -> evaluate` usando `python-analysis/agent_cli.py`.
  - Utilidades `Json.java` y `Proc.java`.
- Script `scripts/run_jade_experiment.ps1`: ejecuta el prototipo, reutilizando la API existente (asegúrese de iniciar el dashboard en `:8001+`).

Uso rápido:
1. Iniciar el dashboard/API si no está activo:
   - `scripts/start_dashboard.ps1 -Port 8001`
2. Ejecutar un experimento orquestado por Java:
   - `scripts/run_jade_experiment.ps1 -ExperimentId exp_jade_demo -Seed 42 -ApiPort 8001`
3. Resultados: `data/results/exp_jade_demo/` (prepRef, train_rf/svm, eval_rf/svm, meta.json)

Lotes:
- `scripts/run_jade_batch.ps1 -ExperimentPrefix exp_jade_batch -Repeats 5 -SeedBase 100 -ApiPort 8001`

Maven local:
- Si no tienes `mvn` global, puedes usar `scripts/install_maven_local.ps1` y el runner lo detectará automáticamente.

Notas:
- El orquestador escribe `meta.json` con `orchestrator=java-cli` y `group=treatment`.
- Las rutas se resuelven relativo a la raíz del workspace para evitar problemas de cwd.
- Para lotes y métricas, se puede reutilizar `aggregate_metrics.py` y `stats_analysis.py`.

Siguientes pasos (JADE real):
- Definir agentes (Coordinator, Worker) extendiendo `jade.core.Agent`.
- Encapsular llamadas al CLI en comportamientos (`Behaviour`).
- Canal de mensajes ACL entre agentes para coordinar etapas.

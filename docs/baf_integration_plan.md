# Plan de integración con BESSER Agentic Framework (BAF)

Este plan resume cómo BAF puede aportar valor a corto plazo dentro del proyecto, sin reemplazar los agentes JADE planificados.

## Objetivos
- Prototipado rápido de UI conversacional vía WebSocket/Streamlit para demos.
- Bridge pragmático WebSocket JSON ↔ JADE (sin FIPA-ACL estricta inicialmente).
- LLM/RAG sobre `docs/` para consultas de documentación.
- (Opcional) Monitoreo de intents/estados con DB + UI.

## Componentes útiles de BAF
- Plataforma WebSocket + UI (Streamlit) con soporte para texto, markdown/HTML, archivos, imágenes y audio.
- Agentes tipo FSM con intents/estados/transiciones.
- Integraciones LLM (OpenAI/HF/Replicate) y RAG (LangChain + Chroma) con loaders de PDF.
- Integraciones Telegram/GitHub/GitLab útiles para automatización.

## Prototipos propuestos
1) UI de demo (Agente eco/ayuda)
- Puerto ejemplo: 8011 (parametrizable para evitar colisión con nuestra API).
- Mensajes soportados: texto → respuesta markdown, archivos.

2) RAG sobre documentación del repo
- Ingesta de `docs/**` (excluyendo binarios pdf si se desea) a un vector store local.
- Consultas desde la UI anterior.

3) Bridge WebSocket ↔ JADE (Spike)
- BAF escucha en WebSocket; un adaptador Python traduce JSON ↔ ACL simple (to, from, content, performative) hacia JADE.
- Éxito: intercambio de un ciclo solicitud/respuesta básico.

## Notas de puertos
- Nuestra plataforma ya parametriza puertos. Conservar variables tipo `WEBSOCKET_PORT` para BAF y `API_BASE` para FastAPI.

## Siguientes pasos
- Elegir el prototipo inicial (recomendado: UI + RAG).
- Crear carpeta `experiments/baf/` con scripts de arranque y README.
- Definir contrato de mensaje puente (campos mínimos: id, to, from, content, type, ts).
- Medir tiempo de respuesta y documentar limitaciones.

## Riesgos / No-cubierto por BAF
- No ofrece FIPA-ACL nativa ni JADE-internal; el bridge cubrirá el MVP.
- Costes/latencia de LLM si se usa proveedor externo.

## Referencias
- Índice por fecha: `docs/INDEX_BY_DATE.md`
- Metodología: `docs/methodology.md`
- Toolchain: `docs/toolchain.md`

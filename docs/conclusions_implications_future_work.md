# Conclusiones, Implicaciones y Trabajos Futuros

> Archivo generado (borrador estructurado). Completar con argumentos finales, citas y figuras si procede.

## 1. Conclusiones principales
- Bajo el escenario y dataset evaluados, no se hallaron diferencias estadísticamente significativas (p ≥ 0.05) entre la arquitectura centralizada (control) y el SMA (treatment) en las métricas principales de entrenamiento (tiempo, CPU, memoria, potencia normalizada por MB) para RF y SVM.
- La arquitectura basada en agentes resultó funcional y replicable, con trazabilidad end-to-end y capacidad de monitoreo y reporte por experimento.
- La ausencia de diferencias podría atribuirse a: (i) tamaño de dataset y carga insuficiente para visibilizar ventajas del paralelismo/orquestación, (ii) overhead de coordinación del SMA, (iii) uniformidad de las condiciones de cómputo.

## 2. Implicaciones técnicas
- En cargas modestas, el beneficio de SMA respecto a centralizado puede ser neutral; se sugiere escalar volumen, complejidad de preprocessing o concurrencia de agentes para valorar ventajas.
- El proxy energético basado en TDP×utilización es útil para comparaciones relativas, pero debe complementarse con medición directa cuando el hardware lo permita.
- La modularidad del SMA facilita reemplazar componentes (p. ej., modelos, monitores), acelerando investigación aplicada y reproducible.

## 3. Implicaciones éticas y de sostenibilidad
- Adoptar el principio de “control humano significativo” en orquestación de agentes y decisiones sensibles.
- Transparencia: registrar y versionar datasets, configuraciones y artefactos de modelos para auditoría.
- Sostenibilidad: documentar consumo energético y, cuando sea posible, usar mediciones directas para reducir incertidumbre. Evaluar impacto ambiental y costo-beneficio de mantener infraestructura multiagente en producción.

## 4. Limitaciones del estudio
- Dataset sintético único y tamaño limitado.
- Medición energética aproximada; ausencia de lectura directa de potencia/energía del sistema.
- Número de repeticiones (n=10 por grupo) suficiente para estimación inicial, pero puede no detectar efectos pequeños.

## 5. Trabajos futuros
- Integrar lectura directa de potencia/energía vía RAPL/powercap en Linux, y abstraer a otras plataformas cuando sea posible.
- Escalar con datasets reales de mayor volumen y diversidad; introducir escenarios con concurrencia de agentes, fallos inducidos y balanceo dinámico.
- Extender el set de modelos (e.g., XGBoost, LightGBM) y etapas (inferencia en lotes, pipelines de feature engineering más complejos).
- Evaluar elasticidad y resiliencia: tiempos de recuperación, reconfiguración autónoma, tolerancia a fallos.
- Incorporar tamaños de efecto y análisis bayesiano para complementar p-values; documentar poder estadístico.

## 6. Recomendaciones prácticas
- Para evidenciar beneficios de SMA, diseñar experimentos con cargas que favorezcan paralelismo (múltiples agentes trabajando en colas o particiones de datos).
- Parametrizar `CPU_POWER_W` según el hardware real y registrar el valor utilizado por experimento.
- Automatizar empaquetado de evidencia (métricas, figuras, reportes) en el pipeline CI/CD para auditoría continua.

## 7. Cierre
Este trabajo establece una base experimental multiagente reproducible para medir eficiencia y sostenibilidad en ML. Si bien los resultados no muestran diferencias significativas en el escenario actual, el marco permite explorar condiciones donde los SMA puedan ofrecer ventajas claras en escalabilidad, resiliencia y eficiencia energética.

---
_Última actualización (auto): YYYY-MM-DD._

## Referencias cruzadas
- Metodología (cómo fue, por qué y para qué): `docs/achievements/metodologia.md`
- Cumplimiento del cronograma (cómo y por qué se lograron las actividades): `docs/achievements/cumplimiento_cronograma.md`
- Resultados esperados y aporte específico: `docs/achievements/resultados_aporte.md`
- Lista de reproducibilidad: `docs/appendix/reproducibility_checklist.md`

# Task List: Anomaly Detector V2

## Configuration
- [ ] Update `anomaly_detector/config.py` to include `THRESHOLD_DURACAO_CURTA_SEC`, `THRESHOLD_CONCENTRACAO_QTD`, `THRESHOLD_CONCENTRACAO_MINUTOS`, and Z-score thresholds.

## Metrics
- [ ] Modify `anomaly_detector/metrics.py` to calculate `taxa_marcada` (conversion rate).
- [ ] Modify `anomaly_detector/metrics.py` to calculate `short_calls` count.
- [ ] Modify `anomaly_detector/metrics.py` to calculate max call concentration per number.
- [ ] Modify `anomaly_detector/metrics.py` to aggregate `agent_stats` (total calls, leads, calls > 1min, meetings).

## Detection
- [ ] Modify `anomaly_detector/detector.py` to implement `detectar_queda_marcada` using Z-score.
- [ ] Modify `anomaly_detector/detector.py` to implement `detectar_aumento_curtas` using Z-score.
- [ ] Modify `anomaly_detector/detector.py` to implement `detectar_concentracao` using static thresholds.
- [ ] Update `detectar_todas` in `anomaly_detector/detector.py` to include new detectors.

## Reporting
- [ ] Modify `anomaly_detector/report.py` to implement `_montar_resumo_agentes`.
- [ ] Update `enviar_whatsapp` in `anomaly_detector/report.py` to include the agent summary in the report.

## Integration
- [ ] Verify `anomaly_detector/main.py` pipeline execution with new features.
- [ ] Update `anomaly_detector/README.md` with new metrics and configuration options.
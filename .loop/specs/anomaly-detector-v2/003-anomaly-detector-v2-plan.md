# Implementation Plan: Anomaly Detector V2

## Goal
Expand the anomaly detection system to monitor conversion rates, short calls, and call concentration, and provide a daily agent performance report.

## Milestones
1.  **Configuration & Setup**: Update environment variables and config handling.
2.  **Metrics Implementation**: Implement new metric calculations in `metrics.py`.
3.  **Detection Logic**: Implement anomaly detection for new metrics in `detector.py`.
4.  **Reporting**: Add agent performance summary to `report.py`.
5.  **Integration & Testing**: Verify the full pipeline in `main.py`.

## Timeline
- **Day 1**: Config, Metrics, and Detection logic.
- **Day 2**: Reporting, Integration, and Testing.

## Resources
- **Developer**: 1 Backend Developer (Python)
- **Access**: Supabase credentials, Z-API credentials.

## Risks
- **Data Quality**: Missing or malformed data in `marcada` or `duration` columns.
- **WhatsApp Limits**: Large agent reports might exceed message limits (mitigated by splitting messages).
- **Performance**: Rolling window calculations on large datasets might be slow (mitigated by filtering to 24h window).
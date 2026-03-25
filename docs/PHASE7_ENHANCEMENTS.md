# Phase 7 — Enhancements

## 1. Predictive Modeling
- **Substation upgrade prediction:** Train a model on historical IESO capacity expansion data to predict which substations are likely to be upgraded (voltage increase, capacity expansion). Parcels near predicted upgrades get a "future potential" bonus.
- **Demand growth modeling:** Use Ontario population/employment growth projections by region to predict where power demand (and thus grid investment) will increase.
- **Land value trajectory:** Combine assessment history with infrastructure investment announcements to predict which areas will appreciate fastest.

## 2. Alert System
- **New parcel alerts:** When new parcels matching user-defined criteria (e.g., >20 acres, industrial zoning, <5km from 230kV+ substation) appear in the data, send email/Slack notifications.
- **Score change alerts:** Notify when a parcel's score changes significantly (e.g., new substation announced nearby, zoning amendment approved).
- **Infrastructure change alerts:** Track grid connection queue (IESO) for new generation/load connections that signal development activity.

## 3. Satellite Imagery Integration
- **Site verification:** Overlay recent satellite imagery (Sentinel-2, free via Copernicus) to verify parcel conditions — is it actually vacant? Any existing structures?
- **Change detection:** Compare imagery over time to detect construction activity, land clearing, or other development signals.
- **Terrain analysis:** Use DEM data to assess site grading requirements (flat land preferred for data centers).

## 4. ML Scoring Improvements
- **Feature engineering:** Add derived features like road access quality, airport proximity, labor market density, climate risk scores.
- **Supervised learning:** If historical data on successful DC site selections is available, train a classification model to predict site success probability.
- **Clustering:** Use unsupervised learning to identify "site archetypes" — groups of parcels with similar characteristics — to surface non-obvious opportunities.

## 5. Additional Data Integrations
- **IESO connection queue:** Monitor the connection assessment queue for new large-load applications (signals competitive interest).
- **Building permit data:** Track permit applications in target municipalities for early signals of DC development.
- **Water availability:** Data centers need cooling water; integrate municipal water capacity data.
- **Climate risk:** Incorporate flood risk projections, extreme heat days, and ice storm frequency.

## 6. UX Enhancements
- **Comparison mode:** Select 2-3 parcels side-by-side with score breakdowns.
- **Report generation:** Export parcel analysis as PDF/PowerPoint for investment committee presentations.
- **Saved searches:** Persist filter configurations and get notified of new matching parcels.
- **Collaboration:** Multi-user annotations, notes, and status tracking per parcel.

## 7. Performance Optimization
- **Tile server:** Pre-render parcel score tiles using pg_tileserv or Martin for faster map rendering at scale.
- **Score caching:** Redis layer for frequently accessed score data.
- **Spatial partitioning:** Partition parcel table by municipality for faster queries at province scale.

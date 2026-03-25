-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Spatial reference check
SELECT PostGIS_Version();

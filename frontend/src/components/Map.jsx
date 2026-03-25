import React, { useEffect, useRef, useMemo } from 'react';
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  CircleMarker,
  Polyline,
  Tooltip,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import L from 'leaflet';
import { scoreToColor, voltageToColor, voltageToRadius, zoomToOpacity } from '../utils/colors';

// Fix Leaflet default icon paths (common issue with bundlers)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const ONTARIO_CENTER = [44.0, -79.0];
const DEFAULT_ZOOM = 8;

/**
 * Component that handles map events like zoom and move.
 */
function MapEventHandler({ onBoundsChange, onZoomChange }) {
  const map = useMapEvents({
    moveend: () => {
      const bounds = map.getBounds();
      onBoundsChange?.({
        west: bounds.getWest(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        north: bounds.getNorth(),
      });
    },
    zoomend: () => {
      onZoomChange?.(map.getZoom());
    },
  });

  useEffect(() => {
    // Fire initial bounds
    const bounds = map.getBounds();
    onBoundsChange?.({
      west: bounds.getWest(),
      south: bounds.getSouth(),
      east: bounds.getEast(),
      north: bounds.getNorth(),
    });
    onZoomChange?.(map.getZoom());
  }, []);

  return null;
}

/**
 * Invalidate map size when container changes (fixes tile rendering).
 */
function MapResizer() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => map.invalidateSize(), 200);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

export default function MapView({
  parcels,
  substations,
  fiberRoutes,
  layers,
  selectedParcelId,
  onParcelSelect,
  onBoundsChange,
}) {
  const [zoom, setZoom] = React.useState(DEFAULT_ZOOM);
  const geoJsonRef = useRef(null);

  // Style function for parcel GeoJSON features
  const parcelStyle = useMemo(() => {
    return (feature) => {
      const score = feature.properties?.overall_score ?? feature.properties?.score ?? 50;
      const isSelected = feature.properties?.id === selectedParcelId;
      return {
        color: scoreToColor(score),
        weight: isSelected ? 3 : 1.5,
        opacity: isSelected ? 1 : 0.8,
        fillColor: scoreToColor(score),
        fillOpacity: isSelected ? 0.45 : zoomToOpacity(zoom, 0.15, 0.4),
        dashArray: isSelected ? null : '3',
      };
    };
  }, [zoom, selectedParcelId]);

  // Interaction handler for each parcel feature
  const onEachParcel = useMemo(() => {
    return (feature, layer) => {
      const props = feature.properties || {};
      const score = props.overall_score ?? props.score ?? '?';
      const name = props.municipality || props.pin || 'Parcel';

      layer.bindTooltip(
        `<strong>${name}</strong><br/>Score: ${score}`,
        { sticky: true }
      );

      layer.on({
        click: () => {
          onParcelSelect?.(props.id);
        },
        mouseover: (e) => {
          const target = e.target;
          target.setStyle({
            weight: 3,
            fillOpacity: 0.5,
          });
          target.bringToFront();
        },
        mouseout: (e) => {
          if (geoJsonRef.current) {
            geoJsonRef.current.resetStyle(e.target);
          }
        },
      });
    };
  }, [onParcelSelect]);

  // Re-key GeoJSON layer when data or style dependencies change
  const geoJsonKey = useMemo(() => {
    return `parcels-${parcels?.features?.length || 0}-${selectedParcelId}-${zoom}`;
  }, [parcels, selectedParcelId, zoom]);

  return (
    <MapContainer
      center={ONTARIO_CENTER}
      zoom={DEFAULT_ZOOM}
      className="w-full h-full"
      zoomControl={false}
      attributionControl={true}
    >
      {/* Dark-themed map tiles */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        maxZoom={19}
      />

      <MapResizer />
      <MapEventHandler onBoundsChange={onBoundsChange} onZoomChange={setZoom} />

      {/* Zoom control in top-right */}
      <div className="leaflet-top leaflet-right">
        <div className="leaflet-control leaflet-bar" />
      </div>

      {/* Parcel polygons */}
      {layers.parcels && parcels?.features?.length > 0 && (
        <GeoJSON
          key={geoJsonKey}
          ref={geoJsonRef}
          data={parcels}
          style={parcelStyle}
          onEachFeature={onEachParcel}
        />
      )}

      {/* Substations */}
      {layers.substations &&
        substations?.map((sub) => {
          const lat = sub.latitude ?? sub.lat;
          const lng = sub.longitude ?? sub.lng ?? sub.lon;
          if (lat == null || lng == null) return null;
          const kv = sub.voltage_kv ?? sub.voltage ?? 0;
          return (
            <CircleMarker
              key={`sub-${sub.id}`}
              center={[lat, lng]}
              radius={voltageToRadius(kv)}
              pathOptions={{
                color: voltageToColor(kv),
                fillColor: voltageToColor(kv),
                fillOpacity: 0.7,
                weight: 2,
              }}
            >
              <Tooltip>
                <strong>{sub.name || 'Substation'}</strong>
                <br />
                Voltage: {kv} kV
                <br />
                {sub.owner && `Owner: ${sub.owner}`}
              </Tooltip>
            </CircleMarker>
          );
        })}

      {/* Fiber routes */}
      {layers.fiber &&
        fiberRoutes?.map((route) => {
          const coords = route.coordinates || route.geometry?.coordinates;
          if (!coords?.length) return null;
          // GeoJSON coords are [lng, lat], Leaflet needs [lat, lng]
          const positions = coords.map((c) =>
            Array.isArray(c[0]) ? c.map((p) => [p[1], p[0]]) : [c[1], c[0]]
          );
          const isNested = Array.isArray(coords[0]?.[0]);
          return (
            <Polyline
              key={`fiber-${route.id}`}
              positions={isNested ? positions : [positions]}
              pathOptions={{
                color: '#06b6d4',
                weight: 2,
                opacity: 0.65,
                dashArray: '8 6',
              }}
            >
              <Tooltip sticky>
                <strong>{route.provider || 'Fiber Route'}</strong>
                {route.capacity && <><br />Capacity: {route.capacity}</>}
              </Tooltip>
            </Polyline>
          );
        })}
    </MapContainer>
  );
}

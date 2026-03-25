import React, { useState, useEffect, useCallback, useRef } from 'react';
import MapView from './components/Map';
import FilterPanel from './components/FilterPanel';
import ParcelDetail from './components/ParcelDetail';
import ScoreOverlay from './components/ScoreOverlay';
import LayerControl from './components/LayerControl';
import {
  getParcels,
  getParcelDetail,
  getSubstations,
  getFiberRoutes,
  getScoreStats,
} from './api/client';

export default function App() {
  // Data state
  const [parcels, setParcels] = useState(null);
  const [substations, setSubstations] = useState([]);
  const [fiberRoutes, setFiberRoutes] = useState([]);
  const [scoreStats, setScoreStats] = useState(null);

  // UI state
  const [selectedParcelId, setSelectedParcelId] = useState(null);
  const [selectedParcel, setSelectedParcel] = useState(null);
  const [filters, setFilters] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [layers, setLayers] = useState({
    parcels: true,
    substations: true,
    transmission: false,
    fiber: true,
    constraints: false,
  });

  const boundsRef = useRef(null);

  // Initial data load
  useEffect(() => {
    fetchParcels({});
    fetchScoreStats();
  }, []);

  // Fetch parcels with filters
  const fetchParcels = useCallback(async (appliedFilters) => {
    setIsLoading(true);
    try {
      const data = await getParcels({ ...appliedFilters, limit: 500 });
      setParcels(data);
    } catch (err) {
      console.error('Failed to fetch parcels:', err);
      // Set empty collection so UI still works
      setParcels({ type: 'FeatureCollection', features: [] });
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch score stats
  const fetchScoreStats = useCallback(async () => {
    try {
      const data = await getScoreStats();
      setScoreStats(data);
    } catch (err) {
      console.error('Failed to fetch score stats:', err);
    }
  }, []);

  // Fetch infrastructure data when map bounds change
  const handleBoundsChange = useCallback(async (bbox) => {
    boundsRef.current = bbox;
    try {
      const [subs, fiber] = await Promise.allSettled([
        getSubstations(bbox),
        getFiberRoutes(bbox),
      ]);
      if (subs.status === 'fulfilled') {
        setSubstations(Array.isArray(subs.value) ? subs.value : subs.value?.features || []);
      }
      if (fiber.status === 'fulfilled') {
        setFiberRoutes(Array.isArray(fiber.value) ? fiber.value : fiber.value?.features || []);
      }
    } catch (err) {
      console.error('Failed to fetch infrastructure:', err);
    }
  }, []);

  // Handle parcel selection
  const handleParcelSelect = useCallback(async (id) => {
    if (!id) {
      setSelectedParcelId(null);
      setSelectedParcel(null);
      return;
    }
    setSelectedParcelId(id);
    try {
      const detail = await getParcelDetail(id);
      setSelectedParcel(detail);
    } catch (err) {
      console.error('Failed to fetch parcel detail:', err);
      // Fallback: try to find it in loaded parcels
      const found = parcels?.features?.find((f) => f.properties?.id === id);
      if (found) setSelectedParcel(found);
    }
  }, [parcels]);

  // Handle filter application
  const handleApplyFilters = useCallback((newFilters) => {
    setFilters(newFilters);
    fetchParcels(newFilters);
  }, [fetchParcels]);

  // Toggle map layers
  const handleLayerToggle = useCallback((key) => {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  }, []);

  const resultCount = parcels?.features?.length ?? null;

  return (
    <div className="w-screen h-screen flex relative overflow-hidden">
      {/* Left sidebar - Filters */}
      <FilterPanel
        onApply={handleApplyFilters}
        resultCount={resultCount}
        isLoading={isLoading}
      />

      {/* Map area */}
      <div className="flex-1 relative">
        <MapView
          parcels={parcels}
          substations={substations}
          fiberRoutes={fiberRoutes}
          layers={layers}
          selectedParcelId={selectedParcelId}
          onParcelSelect={handleParcelSelect}
          onBoundsChange={handleBoundsChange}
        />

        {/* Layer controls */}
        <LayerControl layers={layers} onToggle={handleLayerToggle} />

        {/* Score overlay */}
        <ScoreOverlay stats={scoreStats} parcels={parcels} />

        {/* Dashboard title bar */}
        <div className="absolute top-4 left-4 z-40 flex items-center gap-3">
          <div className="bg-panel-900/95 backdrop-blur-md rounded-lg border border-panel-600 px-4 py-2.5 shadow-xl flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-bold text-white leading-tight">
                Data Center Site Intelligence
              </h1>
              <p className="text-xs text-slate-400">Ontario, Canada</p>
            </div>
          </div>

          {isLoading && (
            <div className="bg-panel-900/95 backdrop-blur-md rounded-lg border border-blue-500/30 px-3 py-2 shadow-xl flex items-center gap-2">
              <svg className="animate-spin w-4 h-4 text-blue-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span className="text-xs text-blue-300">Loading...</span>
            </div>
          )}
        </div>

        {/* Right panel - Parcel detail */}
        {selectedParcel && (
          <ParcelDetail
            parcel={selectedParcel}
            onClose={() => {
              setSelectedParcelId(null);
              setSelectedParcel(null);
            }}
          />
        )}
      </div>
    </div>
  );
}

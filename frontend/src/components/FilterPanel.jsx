import React, { useState, useCallback } from 'react';

const ZONING_OPTIONS = [
  { value: 'Industrial', label: 'Industrial' },
  { value: 'Commercial', label: 'Commercial' },
  { value: 'Agricultural', label: 'Agricultural' },
  { value: 'Rural', label: 'Rural' },
  { value: 'Other', label: 'Other' },
];

const DEFAULT_FILTERS = {
  powerProximity: 25,
  minAcres: 0,
  maxAcres: 500,
  zoningTypes: ['Industrial', 'Commercial', 'Agricultural', 'Rural', 'Other'],
  minScore: 0,
};

export default function FilterPanel({ onApply, resultCount, isLoading }) {
  const [filters, setFilters] = useState({ ...DEFAULT_FILTERS });

  const updateFilter = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const toggleZoning = useCallback((zoneType) => {
    setFilters((prev) => {
      const types = prev.zoningTypes.includes(zoneType)
        ? prev.zoningTypes.filter((z) => z !== zoneType)
        : [...prev.zoningTypes, zoneType];
      return { ...prev, zoningTypes: types };
    });
  }, []);

  const handleApply = () => {
    onApply?.({
      power_proximity_km: filters.powerProximity,
      min_acres: filters.minAcres || undefined,
      max_acres: filters.maxAcres || undefined,
      zoning_types: filters.zoningTypes,
      min_score: filters.minScore || undefined,
    });
  };

  const handleReset = () => {
    setFilters({ ...DEFAULT_FILTERS });
    onApply?.({});
  };

  return (
    <div className="w-80 h-full panel-glass flex flex-col overflow-hidden slide-in">
      {/* Header */}
      <div className="panel-section flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
        </div>
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide">SITE FILTERS</h2>
          <p className="text-xs text-slate-400">Refine parcel search</p>
        </div>
      </div>

      {/* Scrollable filters */}
      <div className="flex-1 overflow-y-auto">
        {/* Power Proximity */}
        <div className="panel-section">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Power Proximity
          </label>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Max distance to substation</span>
            <span className="text-sm font-bold text-blue-400">{filters.powerProximity} km</span>
          </div>
          <input
            type="range"
            min={1}
            max={50}
            value={filters.powerProximity}
            onChange={(e) => updateFilter('powerProximity', Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>1 km</span>
            <span>50 km</span>
          </div>
        </div>

        {/* Parcel Size */}
        <div className="panel-section">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Parcel Size (acres)
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-xs text-slate-400 block mb-1">Minimum</span>
              <input
                type="number"
                min={0}
                max={filters.maxAcres}
                value={filters.minAcres}
                onChange={(e) => updateFilter('minAcres', Number(e.target.value))}
                className="w-full bg-panel-700 border border-panel-500 rounded px-3 py-1.5 text-sm text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <span className="text-xs text-slate-400 block mb-1">Maximum</span>
              <input
                type="number"
                min={filters.minAcres}
                value={filters.maxAcres}
                onChange={(e) => updateFilter('maxAcres', Number(e.target.value))}
                className="w-full bg-panel-700 border border-panel-500 rounded px-3 py-1.5 text-sm text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Zoning Type */}
        <div className="panel-section">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Zoning Type
          </label>
          <div className="space-y-2">
            {ZONING_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className="flex items-center gap-3 cursor-pointer group"
              >
                <input
                  type="checkbox"
                  checked={filters.zoningTypes.includes(opt.value)}
                  onChange={() => toggleZoning(opt.value)}
                />
                <span className="text-sm text-slate-300 group-hover:text-white transition-colors">
                  {opt.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Minimum Score */}
        <div className="panel-section">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Minimum Score
          </label>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Suitability threshold</span>
            <span className="text-sm font-bold text-blue-400">{filters.minScore}</span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            value={filters.minScore}
            onChange={(e) => updateFilter('minScore', Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>0</span>
            <span>100</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="panel-section flex flex-col gap-2">
        {resultCount != null && (
          <div className="text-center mb-1">
            <span className="text-xs text-slate-400">
              Showing{' '}
              <span className="text-blue-400 font-bold text-sm">{resultCount}</span>{' '}
              parcels
            </span>
          </div>
        )}
        <div className="flex gap-2">
          <button
            className="btn-primary flex-1 flex items-center justify-center gap-2"
            onClick={handleApply}
            disabled={isLoading}
          >
            {isLoading ? (
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : null}
            Apply Filters
          </button>
          <button className="btn-secondary" onClick={handleReset}>
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}

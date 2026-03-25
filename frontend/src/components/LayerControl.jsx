import React from 'react';

const LAYERS = [
  {
    key: 'parcels',
    label: 'Parcels',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
    color: '#10b981',
  },
  {
    key: 'substations',
    label: 'Substations',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    color: '#f59e0b',
  },
  {
    key: 'transmission',
    label: 'Transmission Lines',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    ),
    color: '#ef4444',
  },
  {
    key: 'fiber',
    label: 'Fiber Routes',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.14 0M1.394 9.393c5.857-5.858 15.355-5.858 21.213 0" />
      </svg>
    ),
    color: '#06b6d4',
  },
  {
    key: 'constraints',
    label: 'Constraints',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    ),
    color: '#8b5cf6',
  },
];

export default function LayerControl({ layers, onToggle }) {
  return (
    <div className="absolute top-4 right-4 z-40 bg-panel-900/95 backdrop-blur-md rounded-lg border border-panel-600 shadow-xl">
      <div className="px-3 py-2 border-b border-panel-600">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Layers</h3>
      </div>
      <div className="p-2">
        {LAYERS.map(({ key, label, icon, color }) => (
          <label
            key={key}
            className="flex items-center gap-2.5 px-2 py-1.5 rounded cursor-pointer hover:bg-panel-700 transition-colors group"
          >
            <input
              type="checkbox"
              checked={layers[key] ?? false}
              onChange={() => onToggle(key)}
              className="flex-shrink-0"
            />
            <span
              className="flex-shrink-0 opacity-70 group-hover:opacity-100 transition-opacity"
              style={{ color }}
            >
              {icon}
            </span>
            <span className="text-xs text-slate-400 group-hover:text-slate-200 transition-colors">
              {label}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}

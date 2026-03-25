import React from 'react';
import { scoreToColor, scoreLevel } from '../utils/colors';

const SCORE_COMPONENTS = [
  { key: 'power_score', label: 'Power Access', icon: 'bolt' },
  { key: 'fiber_score', label: 'Fiber Connectivity', icon: 'signal' },
  { key: 'zoning_score', label: 'Zoning Suitability', icon: 'building' },
  { key: 'size_score', label: 'Parcel Size', icon: 'expand' },
  { key: 'constraints_score', label: 'Constraints', icon: 'shield' },
];

function ScoreBar({ label, value, maxValue = 100 }) {
  const pct = Math.min(100, Math.max(0, (value / maxValue) * 100));
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-slate-400">{label}</span>
        <span className="text-xs font-bold" style={{ color: scoreToColor(value) }}>
          {value != null ? Math.round(value) : '--'}
        </span>
      </div>
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${scoreToColor(Math.max(0, value - 20))}, ${scoreToColor(value)})`,
          }}
        />
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  if (value == null) return null;
  return (
    <div className="flex justify-between items-center py-1.5">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-sm text-slate-200 font-medium">{value}</span>
    </div>
  );
}

export default function ParcelDetail({ parcel, onClose }) {
  if (!parcel) return null;

  const props = parcel.properties || parcel;
  const overallScore = props.overall_score ?? props.score ?? 0;
  const level = scoreLevel(overallScore);

  return (
    <div className="w-96 h-full panel-glass flex flex-col overflow-hidden slide-in-right absolute right-0 top-0 z-50">
      {/* Header with score */}
      <div className="panel-section relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 w-8 h-8 rounded-full bg-panel-700 hover:bg-panel-600 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
          aria-label="Close"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="flex items-center gap-4">
          {/* Overall score circle */}
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0"
            style={{
              background: `conic-gradient(${scoreToColor(overallScore)} ${overallScore * 3.6}deg, rgba(255,255,255,0.05) 0deg)`,
            }}
          >
            <div className="w-12 h-12 rounded-full bg-panel-900 flex items-center justify-center">
              <span className="text-lg font-black" style={{ color: scoreToColor(overallScore) }}>
                {Math.round(overallScore)}
              </span>
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              {props.pin || props.parcel_id || 'Parcel'}
            </h3>
            <p className="text-xs text-slate-400">{props.municipality || 'Ontario'}</p>
            <span className={`risk-badge risk-badge-${level} mt-1`}>
              {level} suitability
            </span>
          </div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        {/* Parcel Info */}
        <div className="panel-section">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Parcel Information
          </h4>
          <InfoRow label="PIN" value={props.pin} />
          <InfoRow label="Municipality" value={props.municipality} />
          <InfoRow
            label="Area"
            value={
              props.area_acres != null
                ? `${Number(props.area_acres).toFixed(1)} acres`
                : props.area_sqm != null
                  ? `${(props.area_sqm / 4046.86).toFixed(1)} acres`
                  : null
            }
          />
          <InfoRow label="Current Use" value={props.current_use || props.use_description} />
          <InfoRow label="Zoning" value={props.zoning || props.zoning_type} />
          <InfoRow label="Assessment" value={props.assessment_value ? `$${Number(props.assessment_value).toLocaleString()}` : null} />
        </div>

        {/* Score Breakdown */}
        <div className="panel-section">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Score Breakdown
          </h4>
          {SCORE_COMPONENTS.map(({ key, label }) => (
            <ScoreBar
              key={key}
              label={label}
              value={props[key] ?? props.scores?.[key] ?? null}
            />
          ))}
        </div>

        {/* Nearest Infrastructure */}
        <div className="panel-section">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Nearest Infrastructure
          </h4>
          <InfoRow
            label="Substation"
            value={
              props.nearest_substation_km != null
                ? `${Number(props.nearest_substation_km).toFixed(1)} km`
                : props.nearest_substation_distance != null
                  ? `${Number(props.nearest_substation_distance).toFixed(1)} km`
                  : '--'
            }
          />
          <InfoRow
            label="Substation Name"
            value={props.nearest_substation_name}
          />
          <InfoRow
            label="Substation Voltage"
            value={
              props.nearest_substation_kv
                ? `${props.nearest_substation_kv} kV`
                : null
            }
          />
          <InfoRow
            label="Fiber Route"
            value={
              props.nearest_fiber_km != null
                ? `${Number(props.nearest_fiber_km).toFixed(1)} km`
                : props.nearest_fiber_distance != null
                  ? `${Number(props.nearest_fiber_distance).toFixed(1)} km`
                  : '--'
            }
          />
          <InfoRow
            label="Transmission Line"
            value={
              props.nearest_transmission_km != null
                ? `${Number(props.nearest_transmission_km).toFixed(1)} km`
                : '--'
            }
          />
          <InfoRow
            label="Highway"
            value={
              props.nearest_highway_km != null
                ? `${Number(props.nearest_highway_km).toFixed(1)} km`
                : null
            }
          />
        </div>

        {/* Risk Flags */}
        {(props.risk_flags?.length > 0 || props.constraints?.length > 0) && (
          <div className="panel-section">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Risk Flags
            </h4>
            <div className="flex flex-wrap gap-2">
              {(props.risk_flags || props.constraints || []).map((flag, i) => {
                const severity = typeof flag === 'object' ? flag.severity : 'medium';
                const label = typeof flag === 'object' ? flag.label || flag.name : flag;
                return (
                  <span key={i} className={`risk-badge risk-badge-${severity || 'medium'}`}>
                    {label}
                  </span>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

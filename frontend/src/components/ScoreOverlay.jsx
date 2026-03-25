import React, { useMemo } from 'react';
import { scoreToColor } from '../utils/colors';

function MiniHistogram({ distribution }) {
  if (!distribution?.length) return null;
  const max = Math.max(...distribution.map((d) => d.count));

  return (
    <div className="flex items-end gap-px h-12 mt-2">
      {distribution.map((bucket, i) => {
        const height = max > 0 ? (bucket.count / max) * 100 : 0;
        const midScore = (bucket.min + bucket.max) / 2;
        return (
          <div
            key={i}
            className="flex-1 histogram-bar rounded-t-sm relative group"
            style={{
              height: `${height}%`,
              backgroundColor: scoreToColor(midScore),
              minHeight: bucket.count > 0 ? '2px' : '0',
              opacity: 0.8,
            }}
          >
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block">
              <div className="bg-panel-900 text-xs text-slate-300 px-1.5 py-0.5 rounded whitespace-nowrap border border-panel-600">
                {bucket.min}-{bucket.max}: {bucket.count}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ColorLegend() {
  const stops = [0, 20, 40, 60, 80, 100];
  return (
    <div className="mt-3">
      <div className="flex h-2 rounded-full overflow-hidden">
        {stops.slice(0, -1).map((start, i) => {
          const end = stops[i + 1];
          const mid = (start + end) / 2;
          return (
            <div
              key={i}
              className="flex-1"
              style={{ backgroundColor: scoreToColor(mid) }}
            />
          );
        })}
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-xs text-slate-500">0</span>
        <span className="text-xs text-slate-500">25</span>
        <span className="text-xs text-slate-500">50</span>
        <span className="text-xs text-slate-500">75</span>
        <span className="text-xs text-slate-500">100</span>
      </div>
    </div>
  );
}

export default function ScoreOverlay({ stats, parcels }) {
  // Build distribution from parcels if stats don't include it
  const distribution = useMemo(() => {
    if (stats?.distribution) return stats.distribution;
    if (!parcels?.features?.length) return [];

    const buckets = [];
    const bucketSize = 10;
    for (let i = 0; i < 100; i += bucketSize) {
      buckets.push({ min: i, max: i + bucketSize, count: 0 });
    }

    parcels.features.forEach((f) => {
      const score = f.properties?.overall_score ?? f.properties?.score ?? 0;
      const idx = Math.min(Math.floor(score / bucketSize), buckets.length - 1);
      buckets[idx].count++;
    });

    return buckets;
  }, [stats, parcels]);

  const totalParcels = stats?.total_parcels ?? parcels?.features?.length ?? 0;
  const avgScore = stats?.avg_score ?? (
    parcels?.features?.length
      ? (parcels.features.reduce((s, f) => s + (f.properties?.overall_score ?? f.properties?.score ?? 0), 0) / parcels.features.length)
      : 0
  );
  const topScore = stats?.top_score ?? (
    parcels?.features?.length
      ? Math.max(...parcels.features.map(f => f.properties?.overall_score ?? f.properties?.score ?? 0))
      : 0
  );

  return (
    <div className="absolute bottom-6 left-[340px] z-40 w-72 bg-panel-900/95 backdrop-blur-md rounded-lg border border-panel-600 p-4 shadow-xl">
      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
        Score Distribution
      </h3>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="text-center">
          <div className="text-lg font-black text-blue-400">{totalParcels.toLocaleString()}</div>
          <div className="text-xs text-slate-500">Parcels</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-black" style={{ color: scoreToColor(avgScore) }}>
            {avgScore > 0 ? avgScore.toFixed(1) : '--'}
          </div>
          <div className="text-xs text-slate-500">Avg Score</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-black" style={{ color: scoreToColor(topScore) }}>
            {topScore > 0 ? Math.round(topScore) : '--'}
          </div>
          <div className="text-xs text-slate-500">Top Score</div>
        </div>
      </div>

      {/* Histogram */}
      <MiniHistogram distribution={distribution} />

      {/* Color legend */}
      <ColorLegend />

      <div className="flex justify-between mt-2">
        <span className="text-xs text-red-400">Low</span>
        <span className="text-xs text-slate-400">Suitability Score</span>
        <span className="text-xs text-green-400">High</span>
      </div>
    </div>
  );
}

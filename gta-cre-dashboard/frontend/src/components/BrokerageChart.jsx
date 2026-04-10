import { useApi } from '../hooks/useApi'

export default function BrokerageChart() {
  const { data, loading } = useApi('/stats/by-brokerage')

  if (loading || !data?.stats?.length) return null

  const stats = data.stats
  const maxCount = Math.max(...stats.map((s) => s.count), 1)

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">
        Active Listings by Brokerage
      </h2>
      <div className="space-y-2">
        {stats.map((item) => (
          <div key={item.brokerage} className="flex items-center gap-3">
            <div className="w-40 text-xs text-gray-600 text-right truncate flex-shrink-0">
              {item.brokerage}
            </div>
            <div className="flex-1 bg-gray-100 rounded-sm h-6 relative overflow-hidden">
              <div
                className="bg-blue-500 h-full rounded-sm transition-all duration-500"
                style={{ width: `${(item.count / maxCount) * 100}%` }}
              />
              <span className="absolute inset-y-0 right-2 flex items-center text-xs font-medium text-gray-700">
                {item.count}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

import { useFilters } from '../hooks/useApi'

export default function Filters({ filters, onChange }) {
  const { data: filterOptions } = useFilters()

  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value || null })
  }

  const selectClass =
    'border border-gray-300 rounded px-2 py-1.5 text-sm bg-white text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500'
  const inputClass =
    'border border-gray-300 rounded px-2 py-1.5 text-sm bg-white text-gray-700 w-28 focus:outline-none focus:ring-1 focus:ring-blue-500'

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Search</label>
          <input
            type="text"
            placeholder="Address or broker..."
            className={inputClass + ' w-48'}
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Asset Type</label>
          <select
            className={selectClass}
            value={filters.asset_type || ''}
            onChange={(e) => handleChange('asset_type', e.target.value)}
          >
            <option value="">All</option>
            {filterOptions?.asset_types?.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Listing Type</label>
          <select
            className={selectClass}
            value={filters.listing_type || ''}
            onChange={(e) => handleChange('listing_type', e.target.value)}
          >
            <option value="">All</option>
            {filterOptions?.listing_types?.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Brokerage</label>
          <select
            className={selectClass}
            value={filters.brokerage || ''}
            onChange={(e) => handleChange('brokerage', e.target.value)}
          >
            <option value="">All</option>
            {filterOptions?.brokerages?.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">City</label>
          <select
            className={selectClass}
            value={filters.city || ''}
            onChange={(e) => handleChange('city', e.target.value)}
          >
            <option value="">All</option>
            {filterOptions?.cities?.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Min Price</label>
          <input
            type="number"
            placeholder="Min $"
            className={inputClass}
            value={filters.min_price || ''}
            onChange={(e) => handleChange('min_price', e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Max Price</label>
          <input
            type="number"
            placeholder="Max $"
            className={inputClass}
            value={filters.max_price || ''}
            onChange={(e) => handleChange('max_price', e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Min Sqft</label>
          <input
            type="number"
            placeholder="Min sf"
            className={inputClass}
            value={filters.min_sqft || ''}
            onChange={(e) => handleChange('min_sqft', e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Max Sqft</label>
          <input
            type="number"
            placeholder="Max sf"
            className={inputClass}
            value={filters.max_sqft || ''}
            onChange={(e) => handleChange('max_sqft', e.target.value)}
          />
        </div>

        <button
          onClick={() => onChange({
            search: null, asset_type: null, listing_type: null,
            brokerage: null, city: null, min_price: null,
            max_price: null, min_sqft: null, max_sqft: null,
          })}
          className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>
  )
}

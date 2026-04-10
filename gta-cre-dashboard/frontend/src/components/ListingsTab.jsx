import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import Filters from './Filters'
import ListingsTable from './ListingsTable'

export default function ListingsTab() {
  const [filters, setFilters] = useState({
    search: null,
    asset_type: null,
    listing_type: null,
    brokerage: null,
    city: null,
    min_price: null,
    max_price: null,
    min_sqft: null,
    max_sqft: null,
  })

  const { data, loading, error } = useApi('/listings', filters)

  return (
    <div>
      <Filters filters={filters} onChange={setFilters} />

      {loading && (
        <div className="text-center py-12 text-gray-500">Loading listings...</div>
      )}

      {error && (
        <div className="text-center py-12 text-red-500">
          Error loading listings: {error}
        </div>
      )}

      {data && (
        <>
          <div className="text-sm text-gray-500 mb-2">
            {data.count} active listing{data.count !== 1 ? 's' : ''}
          </div>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <ListingsTable listings={data.listings} />
          </div>
        </>
      )}
    </div>
  )
}

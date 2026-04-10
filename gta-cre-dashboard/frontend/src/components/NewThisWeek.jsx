import { useApi } from '../hooks/useApi'
import ListingsTable from './ListingsTable'

export default function NewThisWeek() {
  const { data, loading, error } = useApi('/listings/new')

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>
  if (error) return <div className="text-center py-12 text-red-500">Error: {error}</div>

  return (
    <div>
      <div className="text-sm text-gray-500 mb-2">
        {data?.count || 0} new listing{data?.count !== 1 ? 's' : ''} in the last 7 days
      </div>
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <ListingsTable listings={data?.listings || []} />
      </div>
    </div>
  )
}

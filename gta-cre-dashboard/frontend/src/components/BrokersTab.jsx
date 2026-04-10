import { useState } from 'react'
import { useApi } from '../hooks/useApi'

export default function BrokersTab() {
  const { data, loading, error } = useApi('/brokers')
  const [sortKey, setSortKey] = useState('active_listings')
  const [sortDir, setSortDir] = useState('desc')

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const sortedBrokers = data?.brokers
    ? [...data.brokers].sort((a, b) => {
        const aVal = a[sortKey] ?? ''
        const bVal = b[sortKey] ?? ''
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDir === 'asc' ? aVal - bVal : bVal - aVal
        }
        return sortDir === 'asc'
          ? String(aVal).localeCompare(String(bVal))
          : String(bVal).localeCompare(String(aVal))
      })
    : []

  const SortHeader = ({ label, field }) => (
    <th
      className="px-3 py-2 cursor-pointer hover:bg-gray-200 select-none"
      onClick={() => handleSort(field)}
    >
      {label}
      {sortKey === field && (
        <span className="ml-1">{sortDir === 'asc' ? '\u25B2' : '\u25BC'}</span>
      )}
    </th>
  )

  if (loading) return <div className="text-center py-12 text-gray-500">Loading brokers...</div>
  if (error) return <div className="text-center py-12 text-red-500">Error: {error}</div>

  return (
    <div>
      <div className="text-sm text-gray-500 mb-2">
        {sortedBrokers.length} broker{sortedBrokers.length !== 1 ? 's' : ''} found
      </div>
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-gray-100 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortHeader label="Name" field="name" />
                <SortHeader label="Brokerage" field="brokerage" />
                <SortHeader label="Active Listings" field="active_listings" />
                <th className="px-3 py-2">Email</th>
                <th className="px-3 py-2">Phone</th>
                <th className="px-3 py-2">LinkedIn</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sortedBrokers.map((broker) => (
                <tr key={broker.id} className="hover:bg-gray-50">
                  <td className="px-3 py-2 font-medium text-gray-900">{broker.name}</td>
                  <td className="px-3 py-2 text-gray-600">{broker.brokerage}</td>
                  <td className="px-3 py-2 text-right">
                    <span className="inline-block min-w-[24px] px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs text-center">
                      {broker.active_listings}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-gray-600">{broker.email || '-'}</td>
                  <td className="px-3 py-2 text-gray-600">{broker.phone || '-'}</td>
                  <td className="px-3 py-2">
                    {broker.linkedin_url ? (
                      <a
                        href={broker.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-xs"
                      >
                        Profile
                      </a>
                    ) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

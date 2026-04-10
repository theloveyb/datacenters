function formatPrice(price) {
  if (!price) return '-'
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(price)
}

function formatSqft(sqft) {
  if (!sqft) return '-'
  return new Intl.NumberFormat('en-CA').format(Math.round(sqft)) + ' sf'
}

export default function ListingsTable({ listings, showDaysOnMarket = true }) {
  if (!listings || listings.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No listings found.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-gray-100 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            <th className="px-3 py-2">Address</th>
            <th className="px-3 py-2">City</th>
            <th className="px-3 py-2">Asset Type</th>
            <th className="px-3 py-2">Type</th>
            <th className="px-3 py-2 text-right">Price / Rent</th>
            <th className="px-3 py-2 text-right">Size</th>
            <th className="px-3 py-2">Broker(s)</th>
            <th className="px-3 py-2">Brokerage</th>
            {showDaysOnMarket && <th className="px-3 py-2 text-right">Days on Mkt</th>}
            <th className="px-3 py-2">Link</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {listings.map((listing) => (
            <tr key={listing.id} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-medium text-gray-900 max-w-[250px] truncate">
                {listing.address}
              </td>
              <td className="px-3 py-2 text-gray-600">{listing.city || '-'}</td>
              <td className="px-3 py-2">
                {listing.asset_type ? (
                  <span className="inline-block px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs">
                    {listing.asset_type}
                  </span>
                ) : '-'}
              </td>
              <td className="px-3 py-2">
                {listing.listing_type ? (
                  <span className={`inline-block px-2 py-0.5 rounded text-xs ${
                    listing.listing_type === 'Sale'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-purple-100 text-purple-800'
                  }`}>
                    {listing.listing_type}
                  </span>
                ) : '-'}
              </td>
              <td className="px-3 py-2 text-right text-gray-600">
                {listing.listing_type === 'Lease'
                  ? formatPrice(listing.asking_rent)
                  : formatPrice(listing.asking_price)}
              </td>
              <td className="px-3 py-2 text-right text-gray-600">
                {formatSqft(listing.square_footage)}
              </td>
              <td className="px-3 py-2 text-gray-600 max-w-[180px] truncate">
                {listing.broker_names || '-'}
              </td>
              <td className="px-3 py-2 text-gray-600">{listing.brokerage}</td>
              {showDaysOnMarket && (
                <td className="px-3 py-2 text-right text-gray-600">
                  {listing.days_on_market != null ? Math.round(listing.days_on_market) : '-'}
                </td>
              )}
              <td className="px-3 py-2">
                {listing.listing_url ? (
                  <a
                    href={listing.listing_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-xs"
                  >
                    View
                  </a>
                ) : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

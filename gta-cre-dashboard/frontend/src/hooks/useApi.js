import { useState, useEffect, useCallback } from 'react'

const API_BASE = '/api'

export function useApi(endpoint, params = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const paramsKey = JSON.stringify(params)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL(`${API_BASE}${endpoint}`, window.location.origin)
      const parsedParams = JSON.parse(paramsKey)
      Object.entries(parsedParams).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          url.searchParams.append(key, value)
        }
      })

      const response = await fetch(url)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const json = await response.json()
      setData(json)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [endpoint, paramsKey])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

export function useFilters() {
  return useApi('/filters')
}

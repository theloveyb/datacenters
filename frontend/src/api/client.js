import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    console.error('[API Error]', message);
    return Promise.reject(error);
  }
);

/**
 * Fetch parcels with optional filters.
 * @param {Object} filters
 * @param {number} [filters.power_proximity_km]
 * @param {number} [filters.min_acres]
 * @param {number} [filters.max_acres]
 * @param {string[]} [filters.zoning_types]
 * @param {number} [filters.min_score]
 * @param {number} [filters.limit]
 * @param {number} [filters.offset]
 * @returns {Promise} GeoJSON FeatureCollection
 */
export async function getParcels(filters = {}) {
  const params = {};
  if (filters.power_proximity_km != null) params.power_proximity_km = filters.power_proximity_km;
  if (filters.min_acres != null) params.min_acres = filters.min_acres;
  if (filters.max_acres != null) params.max_acres = filters.max_acres;
  if (filters.zoning_types?.length) params.zoning_types = filters.zoning_types.join(',');
  if (filters.min_score != null) params.min_score = filters.min_score;
  if (filters.limit != null) params.limit = filters.limit;
  if (filters.offset != null) params.offset = filters.offset;

  const { data } = await api.get('/parcels', { params });
  return data;
}

/**
 * Fetch detailed info for a single parcel.
 * @param {string|number} id
 * @returns {Promise}
 */
export async function getParcelDetail(id) {
  const { data } = await api.get(`/parcels/${id}`);
  return data;
}

/**
 * Fetch substations within a bounding box.
 * @param {Object} bbox - { west, south, east, north }
 * @returns {Promise}
 */
export async function getSubstations(bbox) {
  const params = {
    west: bbox.west,
    south: bbox.south,
    east: bbox.east,
    north: bbox.north,
  };
  const { data } = await api.get('/substations', { params });
  return data;
}

/**
 * Fetch fiber routes within a bounding box.
 * @param {Object} bbox - { west, south, east, north }
 * @returns {Promise}
 */
export async function getFiberRoutes(bbox) {
  const params = {
    west: bbox.west,
    south: bbox.south,
    east: bbox.east,
    north: bbox.north,
  };
  const { data } = await api.get('/fiber-routes', { params });
  return data;
}

/**
 * Fetch top-scoring parcels.
 * @param {number} [limit=10]
 * @returns {Promise}
 */
export async function getTopScores(limit = 10) {
  const { data } = await api.get('/scores/top', { params: { limit } });
  return data;
}

/**
 * Fetch aggregate score statistics.
 * @returns {Promise}
 */
export async function getScoreStats() {
  const { data } = await api.get('/scores/stats');
  return data;
}

export default api;

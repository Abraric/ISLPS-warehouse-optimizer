'use client'

import { useState, useEffect } from 'react'
import { getShelves, getMovementLogs } from '@/lib/api'

export default function CongestionMapTab() {
  const [shelves, setShelves] = useState<any[]>([])
  const [movements, setMovements] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedZone, setSelectedZone] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [shelfData, movementData] = await Promise.all([
        getShelves(),
        getMovementLogs({ hours: 2 }),
      ])
      setShelves(shelfData)
      setMovements(movementData)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Calculate congestion per shelf
  const getCongestionLevel = (shelfId: string) => {
    const recentMovements = movements.filter(
      (m) => m.shelf_id === shelfId || 
      (shelves.find(s => s.shelf_id === shelfId)?.adjacent_shelves || []).includes(m.shelf_id)
    )
    return Math.min(recentMovements.length / 10, 1.0) // Normalize to 0-1
  }

  const getCongestionColor = (level: number) => {
    if (level < 0.3) return 'bg-green-500'
    if (level < 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const filteredShelves = selectedZone === 'all' 
    ? shelves 
    : shelves.filter(s => s.location?.zone === selectedZone)

  const zones = Array.from(new Set(shelves.map(s => s.location?.zone).filter(Boolean)))

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Warehouse Congestion Map</h2>

        {/* Zone Filter */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filter by Zone
          </label>
          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Zones</option>
            {zones.map((zone) => (
              <option key={zone} value={zone}>
                Zone {zone}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading warehouse layout...</div>
        ) : (
          <div className="space-y-4">
            {/* Legend */}
            <div className="flex items-center gap-4 text-sm">
              <span className="font-medium">Congestion Level:</span>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span>Low (&lt;30%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                <span>Medium (30-60%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span>High (&gt;60%)</span>
              </div>
            </div>

            {/* Warehouse Grid */}
            <div className="grid grid-cols-8 gap-2">
              {filteredShelves.map((shelf) => {
                const congestion = getCongestionLevel(shelf.shelf_id)
                return (
                  <div
                    key={shelf.shelf_id}
                    className={`
                      p-3 border-2 rounded-lg text-center text-xs
                      ${getCongestionColor(congestion)} text-white
                      ${shelf.is_restricted ? 'border-red-600' : 'border-gray-300'}
                      ${!shelf.is_available ? 'opacity-50' : ''}
                    `}
                    title={`${shelf.shelf_id}\nCongestion: ${(congestion * 100).toFixed(0)}%\nZone: ${shelf.location?.zone || 'N/A'}`}
                  >
                    <div className="font-semibold">{shelf.shelf_id}</div>
                    <div className="text-xs mt-1">
                      {(congestion * 100).toFixed(0)}%
                    </div>
                    {shelf.is_restricted && (
                      <div className="text-xs mt-1">⚠️ Restricted</div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Shelf Details */}
            <div className="mt-6">
              <h3 className="font-semibold mb-2">Shelf Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredShelves.slice(0, 12).map((shelf) => {
                  const congestion = getCongestionLevel(shelf.shelf_id)
                  return (
                    <div
                      key={shelf.shelf_id}
                      className="p-3 border border-gray-200 rounded-md"
                    >
                      <div className="font-semibold">{shelf.shelf_id}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        Zone: {shelf.location?.zone || 'N/A'} | 
                        Congestion: {(congestion * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Available Space: {shelf.available_space_m3?.toFixed(2) || 0} m³
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


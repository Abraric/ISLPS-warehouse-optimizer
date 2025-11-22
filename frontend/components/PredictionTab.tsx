'use client'

import { useState } from 'react'
import { predictLocation, getComponents } from '@/lib/api'

interface PredictionResult {
  component_id: string
  recommended_shelf_id: string
  confidence_score: number
  alternative_shelves: Array<{
    shelf_id: string
    score: number
    zone: string
  }>
  reasoning: string
  feature_vector?: Record<string, number>
  error?: string
}

export default function PredictionTab() {
  const [componentId, setComponentId] = useState('')
  const [components, setComponents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [considerCongestion, setConsiderCongestion] = useState(true)

  const loadComponents = async () => {
    try {
      const data = await getComponents()
      setComponents(data)
    } catch (err: any) {
      setError('Failed to load components: ' + (err.message || 'Unknown error'))
    }
  }

  const handlePredict = async () => {
    if (!componentId.trim()) {
      setError('Please enter a component ID')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const prediction = await predictLocation(componentId, {
        consider_congestion: considerCongestion,
      })
      setResult(prediction)
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Prediction failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Predict Storage Location</h2>

        {/* Component Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Component ID
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={componentId}
              onChange={(e) => setComponentId(e.target.value)}
              placeholder="Enter component ID (e.g., COMP-001)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={loadComponents}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Load Components
            </button>
          </div>
          {components.length > 0 && (
            <select
              onChange={(e) => setComponentId(e.target.value)}
              className="mt-2 w-full px-4 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select a component...</option>
              {components.map((comp) => (
                <option key={comp.component_id} value={comp.component_id}>
                  {comp.component_id} - {comp.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Options */}
        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={considerCongestion}
              onChange={(e) => setConsiderCongestion(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Consider congestion in prediction</span>
          </label>
        </div>

        {/* Predict Button */}
        <button
          onClick={handlePredict}
          disabled={loading}
          className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Predicting...' : 'Predict Optimal Location'}
        </button>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
            {error}
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className="mt-6 space-y-4">
            {result.error ? (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md text-yellow-700">
                {result.error}
              </div>
            ) : (
              <>
                <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                  <h3 className="font-semibold text-green-900 mb-2">Recommended Location</h3>
                  <p className="text-lg font-bold text-green-700">
                    Shelf: {result.recommended_shelf_id}
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    Confidence: {(result.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>

                {result.reasoning && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <h4 className="font-semibold text-blue-900 mb-2">Reasoning</h4>
                    <p className="text-sm text-blue-700">{result.reasoning}</p>
                  </div>
                )}

                {result.alternative_shelves && result.alternative_shelves.length > 0 && (
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <h4 className="font-semibold text-gray-900 mb-2">Alternative Locations</h4>
                    <ul className="space-y-2">
                      {result.alternative_shelves.map((alt, idx) => (
                        <li key={idx} className="text-sm text-gray-700">
                          {alt.shelf_id} (Zone: {alt.zone}) - Score: {(alt.score * 100).toFixed(1)}%
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.feature_vector && (
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <h4 className="font-semibold text-gray-900 mb-2">Feature Vector</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {Object.entries(result.feature_vector).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-600">{key}:</span>
                          <span className="font-mono">{value.toFixed(3)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}


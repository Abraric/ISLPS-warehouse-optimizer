'use client'

import { useState, useEffect } from 'react'
import { getModelPerformance } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function MonitoringTab() {
  const [performance, setPerformance] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPerformance()
  }, [])

  const loadPerformance = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getModelPerformance('latest', 168) // Last week
      setPerformance(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load performance data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-8 text-gray-500">Loading model performance data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      </div>
    )
  }

  if (!performance || !performance.history) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-8 text-gray-500">
          No performance metrics available. Train a model first.
        </div>
      </div>
    )
  }

  const chartData = performance.history.map((entry: any) => ({
    date: new Date(entry.evaluated_at).toLocaleDateString(),
    accuracy: (entry.accuracy * 100).toFixed(1),
    f1_score: (entry.f1_score * 100).toFixed(1),
  }))

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Model Performance Monitoring</h2>

        {/* Current Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600">Accuracy</div>
            <div className="text-2xl font-bold text-blue-700">
              {(performance.accuracy * 100).toFixed(2)}%
            </div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="text-sm text-gray-600">Precision</div>
            <div className="text-2xl font-bold text-green-700">
              {(performance.precision * 100).toFixed(2)}%
            </div>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="text-sm text-gray-600">Recall</div>
            <div className="text-2xl font-bold text-purple-700">
              {(performance.recall * 100).toFixed(2)}%
            </div>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg">
            <div className="text-sm text-gray-600">F1 Score</div>
            <div className="text-2xl font-bold text-orange-700">
              {(performance.f1_score * 100).toFixed(2)}%
            </div>
          </div>
        </div>

        {/* Model Info */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600">Model Version</div>
          <div className="text-lg font-semibold">{performance.model_version}</div>
          <div className="text-xs text-gray-500 mt-1">
            Sample Size: {performance.sample_size} | 
            Evaluated: {new Date(performance.evaluated_at).toLocaleString()}
          </div>
        </div>

        {/* Drift Chart */}
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4">Accuracy Drift Over Time</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="accuracy"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Accuracy (%)"
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="f1_score"
                stroke="#f59e0b"
                strokeWidth={2}
                name="F1 Score (%)"
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Refresh Button */}
        <div className="mt-4">
          <button
            onClick={loadPerformance}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Refresh Metrics
          </button>
        </div>
      </div>
    </div>
  )
}


'use client'

import { useState } from 'react'
import PredictionTab from '@/components/PredictionTab'
import HeatmapTab from '@/components/HeatmapTab'
import CongestionMapTab from '@/components/CongestionMapTab'
import MonitoringTab from '@/components/MonitoringTab'

export default function Home() {
  const [activeTab, setActiveTab] = useState(1)

  const tabs = [
    { id: 1, name: 'Predict Storage Location', component: PredictionTab },
    { id: 2, name: 'Movement Trends Heatmap', component: HeatmapTab },
    { id: 3, name: 'Congestion Map', component: CongestionMapTab },
    { id: 4, name: 'Model Monitoring', component: MonitoringTab },
  ]

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || PredictionTab

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            ASLPS - Adaptive Storage Location Prediction System
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Smart Warehouse Logistics | Industrial Manufacturing
          </p>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.id}️⃣ {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ActiveComponent />
      </main>
    </div>
  )
}


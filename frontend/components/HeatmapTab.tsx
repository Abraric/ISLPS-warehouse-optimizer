'use client'

import { useState, useEffect } from 'react'
import { getMovementLogs, getShelves } from '@/lib/api'
import * as d3 from 'd3'

export default function HeatmapTab() {
  const [movements, setMovements] = useState<any[]>([])
  const [shelves, setShelves] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [hours, setHours] = useState(24)

  useEffect(() => {
    loadData()
  }, [hours])

  const loadData = async () => {
    setLoading(true)
    try {
      const [movementData, shelfData] = await Promise.all([
        getMovementLogs({ hours }),
        getShelves(),
      ])
      setMovements(movementData)
      setShelves(shelfData)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (movements.length > 0 && shelves.length > 0) {
      renderHeatmap()
    }
  }, [movements, shelves])

  const renderHeatmap = () => {
    // Clear previous
    d3.select('#heatmap-container').selectAll('*').remove()

    // Calculate movement counts per shelf
    const shelfMovements = new Map<string, number>()
    movements.forEach((movement) => {
      const count = shelfMovements.get(movement.shelf_id) || 0
      shelfMovements.set(movement.shelf_id, count + 1)
    })

    // Get max count for normalization
    const maxCount = Math.max(...Array.from(shelfMovements.values()), 1)

    // Create color scale
    const colorScale = d3
      .scaleSequential(d3.interpolateYlOrRd)
      .domain([0, maxCount])

    // Create SVG
    const width = 800
    const height = 600
    const margin = { top: 40, right: 40, bottom: 40, left: 40 }

    const svg = d3
      .select('#heatmap-container')
      .append('svg')
      .attr('width', width)
      .attr('height', height)

    // Title
    svg
      .append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '18px')
      .style('font-weight', 'bold')
      .text('Movement Trends Heatmap')

    // Create grid of shelves
    const cols = Math.ceil(Math.sqrt(shelves.length))
    const cellWidth = (width - margin.left - margin.right) / cols
    const cellHeight = 30

    shelves.forEach((shelf, i) => {
      const row = Math.floor(i / cols)
      const col = i % cols
      const x = margin.left + col * cellWidth
      const y = margin.top + row * cellHeight + 20

      const count = shelfMovements.get(shelf.shelf_id) || 0
      const color = colorScale(count)

      // Draw cell
      svg
        .append('rect')
        .attr('x', x)
        .attr('y', y)
        .attr('width', cellWidth - 2)
        .attr('height', cellHeight - 2)
        .attr('fill', color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
        .append('title')
        .text(`${shelf.shelf_id}: ${count} movements`)

      // Label
      svg
        .append('text')
        .attr('x', x + cellWidth / 2)
        .attr('y', y + cellHeight / 2)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .style('font-size', '10px')
        .style('fill', count > maxCount / 2 ? '#fff' : '#000')
        .text(shelf.shelf_id.substring(0, 8))
    })

    // Legend
    const legendWidth = 200
    const legendHeight = 20
    const legendX = width - margin.right - legendWidth
    const legendY = height - margin.bottom

    const legendScale = d3.scaleLinear().domain([0, maxCount]).range([0, legendWidth])

    const legendAxis = d3.axisBottom(legendScale).ticks(5)

    svg
      .append('g')
      .attr('transform', `translate(${legendX}, ${legendY})`)
      .call(legendAxis)

    // Gradient for legend
    const gradient = svg
      .append('defs')
      .append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('x2', '100%')

    gradient
      .selectAll('stop')
      .data(d3.range(0, 1.1, 0.1))
      .enter()
      .append('stop')
      .attr('offset', (d) => `${d * 100}%`)
      .attr('stop-color', (d) => colorScale(d * maxCount))

    svg
      .append('rect')
      .attr('x', legendX)
      .attr('y', legendY - legendHeight)
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#legend-gradient)')

    svg
      .append('text')
      .attr('x', legendX + legendWidth / 2)
      .attr('y', legendY - 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Movement Count')
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Movement Trends Heatmap</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Window (hours)
          </label>
          <input
            type="number"
            value={hours}
            onChange={(e) => setHours(parseInt(e.target.value) || 24)}
            min="1"
            max="168"
            className="px-4 py-2 border border-gray-300 rounded-md w-32"
          />
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading data...</div>
        ) : (
          <div id="heatmap-container" className="border border-gray-200 rounded-md p-4 bg-white" />
        )}
      </div>
    </div>
  )
}


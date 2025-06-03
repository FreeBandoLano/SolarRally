import React from 'react'
import { Clock, DollarSign, Zap, Calendar } from 'lucide-react'

interface TelemetryData {
  timestamp: string
  session_id: string | null
  voltage_v: number
  current_a: number
  power_w: number
  session_energy_kwh_solar: number
  session_energy_kwh_grid: number
  session_total_energy_kwh: number
  energy_source: 'solar' | 'grid' | 'none'
  temperature_c: number
  status: 'available' | 'preparing' | 'charging' | 'finishing' | 'faulted'
}

interface SessionInfoProps {
  telemetryData: TelemetryData | null
}

const SessionInfo: React.FC<SessionInfoProps> = ({ telemetryData }) => {
  if (!telemetryData) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-gray-200 rounded mb-4"></div>
        <div className="space-y-3">
          <div className="h-3 bg-gray-200 rounded"></div>
          <div className="h-3 bg-gray-200 rounded"></div>
          <div className="h-3 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  const { session_id, session_energy_kwh_solar, session_energy_kwh_grid, session_total_energy_kwh, status } = telemetryData

  // Tariff rates (JM$ per kWh)
  const SOLAR_RATE = 10  // JM$10/kWh for solar
  const GRID_RATE = 50   // JM$50/kWh for grid

  // Calculate costs
  const solarCost = session_energy_kwh_solar * SOLAR_RATE
  const gridCost = session_energy_kwh_grid * GRID_RATE
  const totalCost = solarCost + gridCost

  // Calculate savings (compared to all grid power)
  const allGridCost = session_total_energy_kwh * GRID_RATE
  const savings = allGridCost - totalCost

  if (!session_id && status === 'available') {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Session Information
        </h3>
        <div className="text-center text-gray-500 py-8">
          <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-sm">No active session</p>
          <p className="text-xs text-gray-400 mt-1">Ready for charging</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Session Information
      </h3>

      <div className="space-y-4">
        {/* Session ID */}
        {session_id && (
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Zap className="w-5 h-5 text-primary-500" />
            <div>
              <p className="text-sm font-medium text-gray-700">Session ID</p>
              <p className="text-xs text-gray-500 font-mono">
                {session_id}
              </p>
            </div>
          </div>
        )}

        {/* Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-secondary-500" />
            <div>
              <p className="text-sm font-medium text-gray-700">Status</p>
              <p className="text-xs text-gray-500 capitalize">{status}</p>
            </div>
          </div>
          <div className={`status-indicator status-${status}`}></div>
        </div>

        {/* Energy Consumption */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700 text-sm">Energy Consumption</h4>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <p className="text-xs text-primary-600 font-medium">Solar</p>
              <p className="text-lg font-bold text-primary-700">
                {session_energy_kwh_solar.toFixed(3)}
              </p>
              <p className="text-xs text-primary-600">kWh</p>
            </div>
            
            <div className="p-3 bg-secondary-50 rounded-lg">
              <p className="text-xs text-secondary-600 font-medium">Grid</p>
              <p className="text-lg font-bold text-secondary-700">
                {session_energy_kwh_grid.toFixed(3)}
              </p>
              <p className="text-xs text-secondary-600">kWh</p>
            </div>
          </div>

          <div className="p-3 bg-success-50 rounded-lg">
            <p className="text-xs text-success-600 font-medium">Total Energy</p>
            <p className="text-xl font-bold text-success-700">
              {session_total_energy_kwh.toFixed(3)} kWh
            </p>
          </div>
        </div>

        {/* Cost Breakdown */}
        {session_total_energy_kwh > 0 && (
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-green-600" />
              <h4 className="font-medium text-gray-700 text-sm">Cost Breakdown</h4>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Solar cost (JM$10/kWh)</span>
                <span className="font-medium">JM${solarCost.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Grid cost (JM$50/kWh)</span>
                <span className="font-medium">JM${gridCost.toFixed(2)}</span>
              </div>
              
              <div className="border-t pt-2 flex justify-between items-center font-semibold">
                <span className="text-gray-900">Total Cost</span>
                <span className="text-lg">JM${totalCost.toFixed(2)}</span>
              </div>
              
              {savings > 0 && (
                <div className="flex justify-between items-center text-success-600 bg-success-50 p-2 rounded">
                  <span className="text-sm">Solar Savings</span>
                  <span className="font-medium">JM${savings.toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div className="pt-3 border-t text-xs text-gray-500">
          <p>Last updated: {new Date(telemetryData.timestamp).toLocaleString()}</p>
        </div>
      </div>
    </div>
  )
}

export default SessionInfo 
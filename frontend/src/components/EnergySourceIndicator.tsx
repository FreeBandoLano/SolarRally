import React from 'react'
import { Sun, Grid3X3, PowerOff } from 'lucide-react'
import { clsx } from 'clsx'

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

interface EnergySourceIndicatorProps {
  telemetryData: TelemetryData | null
}

const EnergySourceIndicator: React.FC<EnergySourceIndicatorProps> = ({ telemetryData }) => {
  if (!telemetryData) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-gray-200 rounded mb-4"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    )
  }

  const { energy_source, session_energy_kwh_solar, session_energy_kwh_grid } = telemetryData
  const totalEnergy = session_energy_kwh_solar + session_energy_kwh_grid
  const solarPercentage = totalEnergy > 0 ? (session_energy_kwh_solar / totalEnergy) * 100 : 0
  const gridPercentage = totalEnergy > 0 ? (session_energy_kwh_grid / totalEnergy) * 100 : 0

  const getSourceIcon = () => {
    switch (energy_source) {
      case 'solar':
        return <Sun className="w-8 h-8 text-primary-500" />
      case 'grid':
        return <Grid3X3 className="w-8 h-8 text-secondary-500" />
      case 'none':
        return <PowerOff className="w-8 h-8 text-gray-400" />
      default:
        return <PowerOff className="w-8 h-8 text-gray-400" />
    }
  }

  const getSourceColor = () => {
    switch (energy_source) {
      case 'solar':
        return 'text-primary-600 bg-primary-50 border-primary-200'
      case 'grid':
        return 'text-secondary-600 bg-secondary-50 border-secondary-200'
      case 'none':
        return 'text-gray-600 bg-gray-50 border-gray-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getSourceDescription = () => {
    switch (energy_source) {
      case 'solar':
        return 'Clean solar power ☀️'
      case 'grid':
        return 'Grid electricity ⚡'
      case 'none':
        return 'No power source'
      default:
        return 'Unknown source'
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Energy Source
      </h3>

      {/* Current Source Indicator */}
      <div className={clsx(
        'flex items-center justify-center p-6 rounded-lg border-2 mb-6 transition-all duration-300',
        getSourceColor()
      )}>
        <div className="text-center">
          <div className="flex justify-center mb-3">
            {getSourceIcon()}
          </div>
          <h4 className="text-xl font-bold capitalize">
            {energy_source}
          </h4>
          <p className="text-sm opacity-80">
            {getSourceDescription()}
          </p>
        </div>
      </div>

      {/* Energy Mix Progress */}
      {totalEnergy > 0 && (
        <div className="space-y-4">
          <h4 className="font-medium text-gray-700">Session Energy Mix</h4>
          
          {/* Solar Progress Bar */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center space-x-2">
                <Sun className="w-4 h-4 text-primary-500" />
                <span className="text-sm font-medium text-gray-700">Solar</span>
              </div>
              <span className="text-sm text-gray-500">
                {solarPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-primary-400 to-primary-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${solarPercentage}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {session_energy_kwh_solar.toFixed(3)} kWh
            </div>
          </div>

          {/* Grid Progress Bar */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center space-x-2">
                <Grid3X3 className="w-4 h-4 text-secondary-500" />
                <span className="text-sm font-medium text-gray-700">Grid</span>
              </div>
              <span className="text-sm text-gray-500">
                {gridPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-secondary-400 to-secondary-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${gridPercentage}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {session_energy_kwh_grid.toFixed(3)} kWh
            </div>
          </div>
        </div>
      )}

      {totalEnergy === 0 && (
        <div className="text-center text-gray-500 py-4">
          <PowerOff className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No energy consumed yet</p>
        </div>
      )}
    </div>
  )
}

export default EnergySourceIndicator 
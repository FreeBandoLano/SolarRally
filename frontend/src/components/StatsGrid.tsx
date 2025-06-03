import React from 'react'
import { useFirebaseData } from '../hooks/useFirebaseData'

const StatsGrid: React.FC = () => {
  const { systemStats, evseUnits } = useFirebaseData()

  // Use system stats if available, otherwise show placeholder
  const stats = systemStats || {
    total_power_w: 0,
    total_solar_energy_kwh: 0,
    total_grid_energy_kwh: 0,
    total_energy_kwh: 0,
    avg_temperature_c: 0,
    solar_percentage: 0,
    active_sessions: 0,
    available_units: 0,
    charging_units: 0,
    faulted_units: 0
  }

  const unitCount = evseUnits.size

  // Calculate costs in Jamaican Dollars
  const solarCostJMD = stats.total_solar_energy_kwh * 10 // JM$10/kWh for solar
  const gridCostJMD = stats.total_grid_energy_kwh * 50    // JM$50/kWh for grid
  const totalCostJMD = solarCostJMD + gridCostJMD

  const statItems = [
    {
      label: 'Total Power',
      value: `${stats.total_power_w.toLocaleString()}W`,
      icon: '⚡',
      color: stats.total_power_w > 0 ? 'text-green-600' : 'text-gray-500'
    },
    {
      label: 'Active Units',
      value: `${stats.charging_units}/${unitCount}`,
      icon: '🔌',
      color: stats.charging_units > 0 ? 'text-blue-600' : 'text-gray-500'
    },
    {
      label: 'Solar Energy',
      value: `${stats.total_solar_energy_kwh.toFixed(2)} kWh`,
      icon: '☀️',
      color: 'text-yellow-500'
    },
    {
      label: 'Grid Energy',
      value: `${stats.total_grid_energy_kwh.toFixed(2)} kWh`,
      icon: '🏭',
      color: 'text-blue-500'
    },
    {
      label: 'Solar Usage',
      value: `${stats.solar_percentage.toFixed(1)}%`,
      icon: '🌱',
      color: stats.solar_percentage > 50 ? 'text-green-500' : 'text-orange-500'
    },
    {
      label: 'Avg Temperature',
      value: `${stats.avg_temperature_c.toFixed(1)}°C`,
      icon: '🌡️',
      color: stats.avg_temperature_c > 40 ? 'text-red-500' : 'text-blue-500'
    },
    {
      label: 'Session Cost',
      value: `JM$${totalCostJMD.toFixed(2)}`,
      icon: '💰',
      color: 'text-green-600'
    },
    {
      label: 'Total Energy',
      value: `${stats.total_energy_kwh.toFixed(2)} kWh`,
      icon: '🔋',
      color: 'text-purple-600'
    }
  ]

  // Status indicators for different unit states
  const statusItems = [
    {
      label: 'Available',
      count: stats.available_units,
      icon: '✅',
      color: 'text-green-600'
    },
    {
      label: 'Charging',
      count: stats.charging_units,
      icon: '⚡',
      color: 'text-blue-600'
    },
    {
      label: 'Sessions',
      count: stats.active_sessions,
      icon: '🔄',
      color: 'text-purple-600'
    },
    {
      label: 'Faulted',
      count: stats.faulted_units,
      icon: '⚠️',
      color: 'text-red-600'
    }
  ]

  return (
    <div className="space-y-6">
      {/* System Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statItems.map((item, index) => (
          <div
            key={index}
            className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 
                     hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">
                  {item.label}
                </p>
                <p className={`text-xl font-bold ${item.color}`}>
                  {item.value}
                </p>
              </div>
              <div className="text-2xl opacity-75">
                {item.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Unit Status Overview */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          🏢 System Status
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({unitCount} EVSE Units)
          </span>
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {statusItems.map((status, index) => (
            <div key={index} className="text-center">
              <div className={`text-3xl ${status.color} mb-2`}>
                {status.icon}
              </div>
              <div className={`text-2xl font-bold ${status.color} mb-1`}>
                {status.count}
              </div>
              <div className="text-sm text-gray-600">
                {status.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Breakdown */}
      {totalCostJMD > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            💰 Session Cost Breakdown
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-yellow-500 text-2xl mb-2">☀️</div>
              <div className="text-lg font-bold text-gray-900">
                JM${solarCostJMD.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">
                Solar ({stats.total_solar_energy_kwh.toFixed(2)} kWh)
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-blue-500 text-2xl mb-2">🏭</div>
              <div className="text-lg font-bold text-gray-900">
                JM${gridCostJMD.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">
                Grid ({stats.total_grid_energy_kwh.toFixed(2)} kWh)
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-green-500 text-2xl mb-2">💵</div>
              <div className="text-xl font-bold text-green-600">
                JM${totalCostJMD.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">
                Total Cost
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default StatsGrid 
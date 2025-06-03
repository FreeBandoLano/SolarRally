import React from 'react'
import { Battery, Zap, Thermometer, Activity, Sun, Grid3X3 } from 'lucide-react'
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

interface StatsGridProps {
  telemetryData: TelemetryData | null
}

interface StatCardProps {
  title: string
  value: string
  unit: string
  icon: React.ComponentType<any>
  color: 'solar' | 'grid' | 'charging' | 'available'
  subtitle?: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, unit, icon: Icon, color, subtitle }) => {
  return (
    <div className={clsx('stat-card animate-slide-up', color)}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Icon className="w-5 h-5 text-gray-600" />
          <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
            {title}
          </h3>
        </div>
      </div>
      
      <div className="flex items-end space-x-1">
        <span className="text-3xl font-bold text-gray-900">
          {value}
        </span>
        <span className="text-lg font-medium text-gray-600 mb-1">
          {unit}
        </span>
      </div>
      
      {subtitle && (
        <p className="text-xs text-gray-500 mt-2">
          {subtitle}
        </p>
      )}
    </div>
  )
}

const StatsGrid: React.FC<StatsGridProps> = ({ telemetryData }) => {
  if (!telemetryData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-200 rounded mb-3"></div>
            <div className="h-8 bg-gray-200 rounded mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  const isCharging = telemetryData.status === 'charging'
  const currentPowerKw = telemetryData.power_w / 1000

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Voltage */}
      <StatCard
        title="Voltage"
        value={telemetryData.voltage_v.toFixed(1)}
        unit="V"
        icon={Battery}
        color={isCharging ? 'charging' : 'available'}
        subtitle="AC Voltage"
      />

      {/* Current */}
      <StatCard
        title="Current"
        value={telemetryData.current_a.toFixed(1)}
        unit="A"
        icon={Zap}
        color={isCharging ? 'charging' : 'available'}
        subtitle="AC Current"
      />

      {/* Power */}
      <StatCard
        title="Power"
        value={currentPowerKw.toFixed(2)}
        unit="kW"
        icon={Activity}
        color={isCharging ? 'charging' : 'available'}
        subtitle={`${telemetryData.power_w.toFixed(0)} W`}
      />

      {/* Temperature */}
      <StatCard
        title="Temperature"
        value={telemetryData.temperature_c.toFixed(1)}
        unit="°C"
        icon={Thermometer}
        color="available"
        subtitle="System Temperature"
      />

      {/* Solar Energy */}
      <StatCard
        title="Solar Energy"
        value={telemetryData.session_energy_kwh_solar.toFixed(3)}
        unit="kWh"
        icon={Sun}
        color="solar"
        subtitle="Current Session"
      />

      {/* Grid Energy */}
      <StatCard
        title="Grid Energy"
        value={telemetryData.session_energy_kwh_grid.toFixed(3)}
        unit="kWh"
        icon={Grid3X3}
        color="grid"
        subtitle="Current Session"
      />

      {/* Total Energy */}
      <StatCard
        title="Total Energy"
        value={telemetryData.session_total_energy_kwh.toFixed(3)}
        unit="kWh"
        icon={Battery}
        color="charging"
        subtitle="Session Total"
      />

      {/* Status */}
      <div className={clsx('stat-card', telemetryData.status === 'charging' ? 'charging' : 'available')}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-gray-600" />
            <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
              Status
            </h3>
          </div>
          <div className={clsx('status-indicator', `status-${telemetryData.status}`)}></div>
        </div>
        
        <div className="text-2xl font-bold text-gray-900 capitalize mb-2">
          {telemetryData.status}
        </div>
        
        <p className="text-xs text-gray-500">
          {telemetryData.session_id ? `Session: ${telemetryData.session_id.slice(0, 8)}...` : 'No active session'}
        </p>
      </div>
    </div>
  )
}

export default StatsGrid 
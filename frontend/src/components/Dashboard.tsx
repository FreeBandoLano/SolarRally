import React from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import StatsGrid from './StatsGrid'
import PowerChart from './PowerChart'
import SessionInfo from './SessionInfo'
import EnergySourceIndicator from './EnergySourceIndicator'

const Dashboard: React.FC = () => {
  const { systemStats, evseUnits, isConnected } = useWebSocket()

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            Connecting to Live Data...
          </h2>
          <p className="text-gray-500">
            Establishing real-time connection to your EVSE
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Real-time Charging Dashboard
        </h2>
        <p className="text-lg text-gray-600">
          Monitor your hybrid solar/grid EV charging station
        </p>
        {systemStats && (
          <p className="text-sm text-gray-500 mt-2">
            Managing {evseUnits.size} EVSE units • {systemStats.active_sessions} active sessions
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <StatsGrid />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Power Chart - Takes up 2 columns on xl screens */}
        <div className="xl:col-span-2">
          <PowerChart />
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Energy Source Indicator */}
          <EnergySourceIndicator />
          
          {/* Session Information */}
          <SessionInfo />
        </div>
      </div>

      {/* Status Message */}
      {systemStats && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(systemStats.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  )
}

export default Dashboard 
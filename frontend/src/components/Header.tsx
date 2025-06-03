import React from 'react'
import { Zap, Wifi, WifiOff } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'

const Header: React.FC = () => {
  const { isConnected, connectionError } = useWebSocket()

  return (
    <header className="bg-white shadow-card border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gradient">
                SolarRally
              </h1>
              <p className="text-sm text-gray-600">
                EV Charging Dashboard
              </p>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <>
                  <Wifi className="w-5 h-5 text-success-500" />
                  <span className="text-sm font-medium text-success-700">
                    Live Data Connected
                  </span>
                  <div className="status-indicator status-available"></div>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-red-500" />
                  <span className="text-sm font-medium text-red-700">
                    {connectionError || 'Disconnected'}
                  </span>
                  <div className="status-indicator status-faulted"></div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

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

interface EVSEUnit {
  unit_id: string
  telemetry: TelemetryData
  last_updated: string
}

interface SystemStats {
  total_power_w: number
  total_solar_energy_kwh: number
  total_grid_energy_kwh: number
  total_energy_kwh: number
  avg_temperature_c: number
  solar_percentage: number
  active_sessions: number
  available_units: number
  charging_units: number
  faulted_units: number
  last_updated: string
}

interface WebSocketContextType {
  telemetryData: TelemetryData | null // Legacy single unit support
  evseUnits: Map<string, EVSEUnit>
  systemStats: SystemStats | null
  isConnected: boolean
  connectionError: string | null
  connect: () => void
  disconnect: () => void
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [telemetryData, setTelemetryData] = useState<TelemetryData | null>(null)
  const [evseUnits, setEvseUnits] = useState<Map<string, EVSEUnit>>(new Map())
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)

  const calculateSystemStats = (units: Map<string, EVSEUnit>): SystemStats => {
    const unitArray = Array.from(units.values())
    
    if (unitArray.length === 0) {
      return {
        total_power_w: 0,
        total_solar_energy_kwh: 0,
        total_grid_energy_kwh: 0,
        total_energy_kwh: 0,
        avg_temperature_c: 0,
        solar_percentage: 0,
        active_sessions: 0,
        available_units: 0,
        charging_units: 0,
        faulted_units: 0,
        last_updated: new Date().toISOString()
      }
    }

    const stats = unitArray.reduce((acc, unit) => {
      const t = unit.telemetry
      return {
        total_power_w: acc.total_power_w + t.power_w,
        total_solar_energy_kwh: acc.total_solar_energy_kwh + t.session_energy_kwh_solar,
        total_grid_energy_kwh: acc.total_grid_energy_kwh + t.session_energy_kwh_grid,
        total_temperature_c: acc.total_temperature_c + t.temperature_c,
        active_sessions: acc.active_sessions + (t.session_id ? 1 : 0),
        available_units: acc.available_units + (t.status === 'available' ? 1 : 0),
        charging_units: acc.charging_units + (t.status === 'charging' ? 1 : 0),
        faulted_units: acc.faulted_units + (t.status === 'faulted' ? 1 : 0)
      }
    }, {
      total_power_w: 0,
      total_solar_energy_kwh: 0,
      total_grid_energy_kwh: 0,
      total_temperature_c: 0,
      active_sessions: 0,
      available_units: 0,
      charging_units: 0,
      faulted_units: 0
    })

    const total_energy_kwh = stats.total_solar_energy_kwh + stats.total_grid_energy_kwh
    const solar_percentage = total_energy_kwh > 0 
      ? (stats.total_solar_energy_kwh / total_energy_kwh) * 100 
      : 0

    return {
      total_power_w: Math.round(stats.total_power_w),
      total_solar_energy_kwh: Number(stats.total_solar_energy_kwh.toFixed(4)),
      total_grid_energy_kwh: Number(stats.total_grid_energy_kwh.toFixed(4)),
      total_energy_kwh: Number(total_energy_kwh.toFixed(4)),
      avg_temperature_c: Number((stats.total_temperature_c / unitArray.length).toFixed(1)),
      solar_percentage: Number(solar_percentage.toFixed(1)),
      active_sessions: stats.active_sessions,
      available_units: stats.available_units,
      charging_units: stats.charging_units,
      faulted_units: stats.faulted_units,
      last_updated: new Date().toISOString()
    }
  }

  const connect = () => {
    try {
      setConnectionError(null)
      const websocket = new WebSocket('ws://localhost:8000/ws/live')
      
      websocket.onopen = () => {
        console.log('✅ Connected to WebSocket!')
        setIsConnected(true)
        setConnectionError(null)
      }
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as TelemetryData & { unit_id?: string }
          
          // Update legacy single unit data (use first unit received)
          setTelemetryData(data)
          
          // Extract unit ID from the message (sent by backend) or derive from other fields
          let unitId = data.unit_id || 'evse_unit_01' // Use backend-provided unit_id or default
          
          // If no unit_id provided by backend, try to extract from session_id pattern
          if (!data.unit_id && data.session_id) {
            const sessionParts = data.session_id.split('_')
            if (sessionParts.length >= 2) {
              // Look for patterns like "sess_abc123" -> extract prefix if meaningful
              // or "evse_unit_01_sess_abc123" -> extract "evse_unit_01"
              if (sessionParts[0] === 'evse' && sessionParts[1] === 'unit') {
                unitId = `${sessionParts[0]}_${sessionParts[1]}_${sessionParts[2]}`
              } else if (sessionParts[0] === 'sess') {
                // Session ID like "sess_abc123" - rotate through units
                const unitNumber = Math.floor(Date.now() / 5000) % 3 + 1 // Change every 5 seconds
                unitId = `evse_unit_${unitNumber.toString().padStart(2, '0')}`
              }
            }
          }
          
          // Update EVSE units map
          setEvseUnits(prevUnits => {
            const newUnits = new Map(prevUnits)
            newUnits.set(unitId, {
              unit_id: unitId,
              telemetry: data,
              last_updated: new Date().toISOString()
            })
            
            // Calculate and update system stats
            const newStats = calculateSystemStats(newUnits)
            setSystemStats(newStats)
            
            return newUnits
          })
          
        } catch (error) {
          console.error('Error parsing WebSocket data:', error)
        }
      }
      
      websocket.onclose = () => {
        console.log('🔌 WebSocket closed')
        setIsConnected(false)
        setWs(null)
      }
      
      websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        setConnectionError('Failed to connect to real-time data service')
        setIsConnected(false)
      }
      
      setWs(websocket)
    } catch (error) {
      setConnectionError('Unable to establish WebSocket connection')
      setIsConnected(false)
    }
  }

  const disconnect = () => {
    if (ws) {
      ws.close()
      setWs(null)
    }
  }

  useEffect(() => {
    // Auto-connect when component mounts
    connect()
    
    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])

  const value: WebSocketContextType = {
    telemetryData,
    evseUnits,
    systemStats,
    isConnected,
    connectionError,
    connect,
    disconnect
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
} 
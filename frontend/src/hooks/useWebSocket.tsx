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

interface WebSocketContextType {
  telemetryData: TelemetryData | null
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
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)

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
          const data = JSON.parse(event.data) as TelemetryData
          setTelemetryData(data)
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
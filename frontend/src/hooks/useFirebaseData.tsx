import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

// Mock Firebase database interface for demo
class MockFirebaseDB {
  private listeners: { [key: string]: ((data: any) => void)[] } = {}

  ref(path: string = '') {
    return {
      on: (_eventType: string, callback: (snapshot: any) => void) => {
        if (!this.listeners[path]) {
          this.listeners[path] = []
        }
        this.listeners[path].push((data) => {
          callback({ val: () => data })
        })
      },
      off: () => {
        if (this.listeners[path]) {
          this.listeners[path] = []
        }
      }
    }
  }

  simulateData() {
    // Generate mock data every 2 seconds
    setInterval(() => {
      const mockData = this.generateMockData()
      
      // Notify listeners
      Object.keys(this.listeners).forEach(path => {
        if (this.listeners[path]) {
          this.listeners[path].forEach(callback => {
            if (path === 'latest_telemetry') {
              callback(mockData.latest_telemetry)
            } else if (path === 'system_stats') {
              callback(mockData.system_stats)
            } else if (path === 'evse_units') {
              callback(mockData.evse_units)
            }
          })
        }
      })
    }, 2000)
  }

  generateMockData() {
    const scenarios = [
      {
        status: "charging",
        voltageRange: [220, 240],
        currentRange: [15, 32],
        energySource: ["solar", "grid", "solar"], // Bias toward solar
        sessionId: `sess_${Math.floor(Math.random() * 9000) + 1000}`
      },
      {
        status: "available",
        voltageRange: [220, 240],
        currentRange: [0, 0],
        energySource: ["none"],
        sessionId: null
      },
      {
        status: "preparing",
        voltageRange: [220, 240],
        currentRange: [0, 5],
        energySource: ["solar"],
        sessionId: `sess_${Math.floor(Math.random() * 9000) + 1000}`
      }
    ]

    const generateTelemetry = () => {
      const scenario = scenarios[Math.floor(Math.random() * scenarios.length)]
      const voltage = Math.random() * (scenario.voltageRange[1] - scenario.voltageRange[0]) + scenario.voltageRange[0]
      const current = Math.random() * (scenario.currentRange[1] - scenario.currentRange[0]) + scenario.currentRange[0]
      const power = voltage * current
      const energySource = scenario.energySource[Math.floor(Math.random() * scenario.energySource.length)]

      const sessionTime = Math.random() * 2.4 + 0.1
      const energyRate = power / 1000

      let solarEnergy = 0
      let gridEnergy = 0

      if (energySource === "solar") {
        solarEnergy = sessionTime * energyRate
        gridEnergy = sessionTime * energyRate * 0.1
      } else if (energySource === "grid") {
        solarEnergy = sessionTime * energyRate * 0.2
        gridEnergy = sessionTime * energyRate * 0.8
      }

      return {
        timestamp: new Date().toISOString(),
        session_id: scenario.sessionId,
        voltage_v: Math.round(voltage * 100) / 100,
        current_a: Math.round(current * 100) / 100,
        power_w: Math.round(power * 100) / 100,
        session_energy_kwh_solar: Math.round(solarEnergy * 10000) / 10000,
        session_energy_kwh_grid: Math.round(gridEnergy * 10000) / 10000,
        session_total_energy_kwh: Math.round((solarEnergy + gridEnergy) * 10000) / 10000,
        energy_source: energySource,
        temperature_c: Math.round((Math.random() * 25 + 20) * 10) / 10,
        status: scenario.status,
        unit_id: `evse_unit_${Math.floor(Math.random() * 3) + 1}`
      }
    }

    const units: any = {}
    for (let i = 1; i <= 3; i++) {
      const telemetry = generateTelemetry()
      const unitId = `evse_unit_${i}`
      units[unitId] = {
        unit_id: unitId,
        telemetry: telemetry,
        last_updated: new Date().toISOString()
      }
    }

    // Calculate system stats
    let totalPower = 0
    let totalSolar = 0
    let totalGrid = 0
    let activeSessions = 0
    let chargingUnits = 0
    let availableUnits = 0

    Object.values(units).forEach((unit: any) => {
      if (unit.telemetry) {
        totalPower += unit.telemetry.power_w
        totalSolar += unit.telemetry.session_energy_kwh_solar
        totalGrid += unit.telemetry.session_energy_kwh_grid
        
        if (unit.telemetry.session_id) activeSessions++
        if (unit.telemetry.status === "charging") chargingUnits++
        if (unit.telemetry.status === "available") availableUnits++
      }
    })

    const totalEnergy = totalSolar + totalGrid
    const solarPercentage = totalEnergy > 0 ? (totalSolar / totalEnergy * 100) : 0

    const systemStats = {
      total_power_w: Math.round(totalPower),
      total_solar_energy_kwh: Math.round(totalSolar * 10000) / 10000,
      total_grid_energy_kwh: Math.round(totalGrid * 10000) / 10000,
      total_energy_kwh: Math.round(totalEnergy * 10000) / 10000,
      avg_temperature_c: Math.round((Math.random() * 10 + 25) * 10) / 10,
      solar_percentage: Math.round(solarPercentage * 10) / 10,
      active_sessions: activeSessions,
      available_units: availableUnits,
      charging_units: chargingUnits,
      faulted_units: 0,
      last_updated: new Date().toISOString()
    }

    return {
      latest_telemetry: units[Object.keys(units)[0]].telemetry,
      system_stats: systemStats,
      evse_units: units
    }
  }
}

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

interface FirebaseDataContextType {
  telemetryData: TelemetryData | null
  evseUnits: Map<string, EVSEUnit>
  systemStats: SystemStats | null
  isConnected: boolean
  connectionError: string | null
}

const FirebaseDataContext = createContext<FirebaseDataContextType | null>(null)

export const useFirebaseData = () => {
  const context = useContext(FirebaseDataContext)
  if (!context) {
    throw new Error('useFirebaseData must be used within a FirebaseDataProvider')
  }
  return context
}

interface FirebaseDataProviderProps {
  children: ReactNode
}

export const FirebaseDataProvider: React.FC<FirebaseDataProviderProps> = ({ children }) => {
  const [telemetryData, setTelemetryData] = useState<TelemetryData | null>(null)
  const [evseUnits, setEvseUnits] = useState<Map<string, EVSEUnit>>(new Map())
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError] = useState<string | null>(null)

  useEffect(() => {
    console.log('🔥 Starting Firebase real-time data simulation...')
    setIsConnected(true)
    
    const mockDB = new MockFirebaseDB()
    
    // Listen for telemetry data
    mockDB.ref('latest_telemetry').on('value', (snapshot) => {
      const data = snapshot.val()
      if (data) {
        setTelemetryData(data)
      }
    })

    // Listen for system stats
    mockDB.ref('system_stats').on('value', (snapshot) => {
      const data = snapshot.val()
      if (data) {
        setSystemStats(data)
      }
    })

    // Listen for EVSE units
    mockDB.ref('evse_units').on('value', (snapshot) => {
      const data = snapshot.val()
      if (data) {
        const unitsMap = new Map<string, EVSEUnit>()
        Object.entries(data).forEach(([unitId, unit]) => {
          unitsMap.set(unitId, unit as EVSEUnit)
        })
        setEvseUnits(unitsMap)
      }
    })

    // Start simulation
    mockDB.simulateData()

    return () => {
      // Cleanup listeners
      mockDB.ref('latest_telemetry').off()
      mockDB.ref('system_stats').off()
      mockDB.ref('evse_units').off()
    }
  }, [])

  return (
    <FirebaseDataContext.Provider
      value={{
        telemetryData,
        evseUnits,
        systemStats,
        isConnected,
        connectionError
      }}
    >
      {children}
    </FirebaseDataContext.Provider>
  )
} 
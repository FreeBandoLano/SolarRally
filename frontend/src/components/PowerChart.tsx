import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Activity } from 'lucide-react'

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

interface PowerChartProps {
  telemetryData: TelemetryData | null
}

interface ChartDataPoint {
  time: string
  power: number
  voltage: number
  current: number
  temperature: number
}

const PowerChart: React.FC<PowerChartProps> = ({ telemetryData }) => {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])

  useEffect(() => {
    if (telemetryData) {
      const timeStr = new Date(telemetryData.timestamp).toLocaleTimeString()
      
      const newDataPoint: ChartDataPoint = {
        time: timeStr,
        power: telemetryData.power_w / 1000, // Convert to kW
        voltage: telemetryData.voltage_v,
        current: telemetryData.current_a,
        temperature: telemetryData.temperature_c
      }

      setChartData(prevData => {
        const newData = [...prevData, newDataPoint]
        // Keep only the last 20 data points for performance
        return newData.slice(-20)
      })
    }
  }, [telemetryData])

  const formatTooltip = (value: number, name: string) => {
    switch (name) {
      case 'power':
        return [`${value.toFixed(2)} kW`, 'Power']
      case 'voltage':
        return [`${value.toFixed(1)} V`, 'Voltage']
      case 'current':
        return [`${value.toFixed(1)} A`, 'Current']
      case 'temperature':
        return [`${value.toFixed(1)} °C`, 'Temperature']
      default:
        return [value, name]
    }
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <Activity className="w-5 h-5 text-gray-600" />
        <h3 className="text-lg font-semibold text-gray-900">
          Real-time Power Monitoring
        </h3>
      </div>

      {chartData.length === 0 ? (
        <div className="h-80 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p>Waiting for data...</p>
          </div>
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                tick={{ fill: '#6b7280' }}
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                tick={{ fill: '#6b7280' }}
              />
              <Tooltip 
                formatter={formatTooltip}
                labelStyle={{ color: '#374151' }}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="power"
                stroke="#ed7811"
                strokeWidth={3}
                dot={{ fill: '#ed7811', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#ed7811', strokeWidth: 2 }}
                name="Power (kW)"
              />
              <Line
                type="monotone"
                dataKey="voltage"
                stroke="#0ea5e9"
                strokeWidth={2}
                dot={{ fill: '#0ea5e9', strokeWidth: 2, r: 3 }}
                name="Voltage (V)"
              />
              <Line
                type="monotone"
                dataKey="current"
                stroke="#22c55e"
                strokeWidth={2}
                dot={{ fill: '#22c55e', strokeWidth: 2, r: 3 }}
                name="Current (A)"
              />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', strokeWidth: 2, r: 3 }}
                name="Temperature (°C)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500 text-center">
        Showing last 20 data points • Updates every 10 seconds
      </div>
    </div>
  )
}

export default PowerChart 
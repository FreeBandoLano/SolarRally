import React from 'react'
import { BrowserRouter as Router } from 'react-router-dom'
import { WebSocketProvider } from './hooks/useWebSocket'
import Dashboard from './components/Dashboard'
import Header from './components/Header'

function App() {
  return (
    <Router>
      <WebSocketProvider>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main className="container mx-auto px-4 py-8">
            <Dashboard />
          </main>
        </div>
      </WebSocketProvider>
    </Router>
  )
}

export default App 
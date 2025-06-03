import { BrowserRouter as Router } from 'react-router-dom'
import { FirebaseDataProvider } from './hooks/useFirebaseData'
import Dashboard from './components/Dashboard'
import Header from './components/Header'

function App() {
  return (
    <Router>
      <FirebaseDataProvider>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main className="container mx-auto px-4 py-8">
            <Dashboard />
          </main>
        </div>
      </FirebaseDataProvider>
    </Router>
  )
}

export default App 
import { useState } from 'react'
import ListingsTab from './components/ListingsTab'
import BrokersTab from './components/BrokersTab'
import NewThisWeek from './components/NewThisWeek'
import DelistedThisWeek from './components/DelistedThisWeek'
import BrokerageChart from './components/BrokerageChart'

const TABS = [
  { id: 'listings', label: 'Active Listings' },
  { id: 'brokers', label: 'Brokers' },
  { id: 'new', label: 'New This Week' },
  { id: 'delisted', label: 'Delisted This Week' },
]

function App() {
  const [activeTab, setActiveTab] = useState('listings')

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">
          GTA Commercial Real Estate Dashboard
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Aggregated listings from 12 brokerages across the Greater Toronto Area
        </p>
      </header>

      <div className="max-w-[1400px] mx-auto px-4 py-6">
        <BrokerageChart />

        <nav className="flex border-b border-gray-200 mt-6 mb-4">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div>
          {activeTab === 'listings' && <ListingsTab />}
          {activeTab === 'brokers' && <BrokersTab />}
          {activeTab === 'new' && <NewThisWeek />}
          {activeTab === 'delisted' && <DelistedThisWeek />}
        </div>
      </div>
    </div>
  )
}

export default App

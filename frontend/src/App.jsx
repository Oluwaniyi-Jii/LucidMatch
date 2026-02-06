import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Governance from './pages/Governance'
import Curriculum from './pages/Curriculum'

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/jobs" element={<Jobs />} />
                    <Route path="/jobs/:id" element={<JobDetail />} />
                    <Route path="/analysis" element={<Analysis />} />
                    <Route path="/governance" element={<Governance />} />
                    <Route path="/upskill" element={<Curriculum />} />
                </Routes>
            </Layout>
        </Router>
    )
}

export default App

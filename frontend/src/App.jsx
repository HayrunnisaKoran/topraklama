import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TransformerDetail from './pages/TransformerDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/transformer/:id" element={<TransformerDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

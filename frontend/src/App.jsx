import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Detail from './pages/Detail';
import { useAuth } from './contexts/AuthContext';
import GlossaryPopup from './components/GlossaryPopup';

const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <div className="min-h-screen relative flex flex-col">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/detail/:topic" element={
            <ProtectedRoute>
              <Detail />
            </ProtectedRoute>
          } />
        </Routes>
        <GlossaryPopup />
      </div>
    </BrowserRouter>
  );
}

export default App;

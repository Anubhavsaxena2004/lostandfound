import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  HomePage,
  LoginPage,
  RegisterPage,
  FoundItemPage,
  LostItemPage,
  MatchPage,
  VerificationPage,
  AdminDashboard
} from './pages';
import PrivateRoute from './components/PrivateRoute';
import { Navbar, Footer } from './components';
import { AuthProvider } from './context/AuthContext';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <div className="container">
          <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <PrivateRoute path="/found" element={<FoundItemPage />} />
          <PrivateRoute path="/lost" element={<LostItemPage />} />
          <PrivateRoute path="/matches" element={<MatchPage />} />
          <PrivateRoute path="/verify" element={<VerificationPage />} />
          <PrivateRoute path="/admin" element={<AdminDashboard />} />
          </Routes>
        </div>
        <Footer />
      </Router>
    </AuthProvider>
  );
}

export default App;

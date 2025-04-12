import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Navbar.css';

function Navbar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Lost & Found
        </Link>
        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <Link to="/found" className="navbar-link">
                Report Found Item
              </Link>
              <Link to="/lost" className="navbar-link">
                Report Lost Item
              </Link>
              <button onClick={logout} className="navbar-link">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">
                Login
              </Link>
              <Link to="/register" className="navbar-link">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

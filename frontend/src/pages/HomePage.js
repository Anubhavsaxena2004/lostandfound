import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/HomePage.css';

function HomePage() {
  return (
    <div className="home-page">
      <h1>Lost & Found Platform</h1>
      <p className="tagline">Find. Verify. Return. Give back to the world.</p>
      
      <div className="action-buttons">
        <Link to="/found" className="btn primary">
          Report Found Item
        </Link>
        <Link to="/lost" className="btn secondary">
          Report Lost Item
        </Link>
      </div>

      <div className="features">
        <div className="feature-card">
          <h3>Secure Verification</h3>
          <p>Our system ensures items are returned to their rightful owners through a thorough verification process.</p>
        </div>
        <div className="feature-card">
          <h3>Social Impact</h3>
          <p>Unclaimed items are donated to NGOs and social causes after 30 days.</p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;

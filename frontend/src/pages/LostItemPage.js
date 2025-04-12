import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/LostItemPage.css';

function LostItemPage() {
  const [formData, setFormData] = useState({
    photo: null,
    brand: '',
    color: '',
    size: '',
    uniqueIdentifiers: '',
    description: '',
    location: '',
    lostDate: '',
    lostTime: '',
    contactReward: '',
    latitude: '',
    longitude: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }));
          setErrors(prev => ({ ...prev, location: '' }));
        },
        (err) => {
          setErrors(prev => ({
            ...prev,
            location: 'Could not get your location. Please enter it manually.'
          }));
        }
      );
    } else {
      setErrors(prev => ({
        ...prev,
        location: 'Geolocation is not supported by your browser.'
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.description) newErrors.description = 'Description is required';
    if (!formData.location) newErrors.location = 'Location is required';
    if (!formData.lostDate) newErrors.lostDate = 'Date lost is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    setErrors({});

    try {
      const form = new FormData();
      for (const key in formData) {
        if (formData[key] !== null && formData[key] !== '') {
          form.append(key, formData[key]);
        }
      }
      form.append('submitter', user.id);

      await api.post('/lost-items/', form, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Token ${user.token}`
        }
      });

      setSuccess(true);
      setTimeout(() => navigate('/'), 2000);
    } catch (err) {
      setErrors(prev => ({
        ...prev,
        submit: err.response?.data?.message || 'Submission failed'
      }));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="lost-item-page">
      <h1>Report Lost Item</h1>
      
      {success && (
        <div className="alert alert-success">
          Item reported successfully! Redirecting...
        </div>
      )}
      
      {errors.submit && (
        <div className="alert alert-danger">{errors.submit}</div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Brand</label>
            <input
              type="text"
              name="brand"
              value={formData.brand}
              onChange={handleChange}
              className={errors.brand ? 'error' : ''}
            />
          </div>
          <div className="form-group">
            <label>Color</label>
            <input
              type="text"
              name="color"
              value={formData.color}
              onChange={handleChange}
              className={errors.color ? 'error' : ''}
            />
          </div>
          <div className="form-group">
            <label>Size</label>
            <input
              type="text"
              name="size"
              value={formData.size}
              onChange={handleChange}
              className={errors.size ? 'error' : ''}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Unique Identifiers</label>
          <textarea
            name="uniqueIdentifiers"
            value={formData.uniqueIdentifiers}
            onChange={handleChange}
            rows="2"
          />
        </div>

        <div className="form-group">
          <label>Description*</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows="4"
            className={errors.description ? 'error' : ''}
          />
          {errors.description && (
            <div className="error-message">{errors.description}</div>
          )}
        </div>

        <div className="form-group">
          <label>Location Lost*</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            required
            className={errors.location ? 'error' : ''}
          />
          <button 
            type="button" 
            onClick={handleGetLocation}
            className="location-btn"
          >
            <i className="fas fa-map-marker-alt"></i> Use Current Location
          </button>
          {errors.location && (
            <div className="error-message">{errors.location}</div>
          )}
          {formData.latitude && formData.longitude && (
            <div className="location-success">
              <i className="fas fa-check-circle"></i> Location captured
            </div>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Date Lost*</label>
            <input
              type="date"
              name="lostDate"
              value={formData.lostDate}
              onChange={handleChange}
              required
              className={errors.lostDate ? 'error' : ''}
            />
            {errors.lostDate && (
              <div className="error-message">{errors.lostDate}</div>
            )}
          </div>
          <div className="form-group">
            <label>Time Lost</label>
            <input
              type="time"
              name="lostTime"
              value={formData.lostTime}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Reward (optional)</label>
          <input
            type="number"
            name="contactReward"
            value={formData.contactReward}
            onChange={handleChange}
            min="0"
            step="0.01"
          />
        </div>

        <div className="form-group">
          <label>Item Photo (if available)</label>
          <input
            type="file"
            name="photo"
            accept="image/*"
            onChange={handleChange}
          />
        </div>

        <button 
          type="submit" 
          className="btn primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? <LoadingSpinner small /> : 'Submit Report'}
        </button>
      </form>
    </div>
  );
}

export default LostItemPage;

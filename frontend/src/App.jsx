import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SearchBar from './components/SearchBar';
import PropertyCard from './components/PropertyCard';
import './index.css';

function App() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useState({
    type: '',
    city: '',
    property_type: '',
    min_price: '',
    max_price: ''
  });

  const fetchProperties = async () => {
    setLoading(true);
    try {
      // Build query string
      const queryParts = [];
      Object.keys(searchParams).forEach(key => {
        if (searchParams[key] !== '') {
          queryParts.push(`${key}=${encodeURIComponent(searchParams[key])}`);
        }
      });
      const queryString = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
      
      const response = await fetch(`http://localhost:8000/properties/${queryString}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setProperties(data);
    } catch (error) {
      console.error("Failed to fetch properties:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handleSearch = () => {
    fetchProperties();
  };

  return (
    <div className="app-container">
      <Navbar />
      
      <main className="main-content">
        <section className="hero">
          <h1>Find Your Dream Property in India</h1>
          <p>Discover the best flats and houses for rent or sale in top cities.</p>
        </section>
        
        <div className="container">
          <SearchBar 
            searchParams={searchParams} 
            onSearchChange={setSearchParams} 
            onSearch={handleSearch} 
          />
          
          {loading ? (
            <div className="loader">Loading properties...</div>
          ) : properties.length > 0 ? (
            <div className="property-grid">
              {properties.map(property => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <h2>No Properties Found</h2>
              <p>Try adjusting your search filters to find what you're looking for.</p>
            </div>
          )} 
        </div>
      </main>
    </div>
  );
}

export default App;

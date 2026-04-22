import React from 'react';
import { Search } from 'lucide-react';

const SearchBar = ({ searchParams, onSearchChange, onSearch }) => {
  const cities = ['Bangalore', 'Mumbai', 'New Delhi', 'Bhubaneshwar', 'Hyderabad'];

  const handleChange = (e) => {
    const { name, value } = e.target;
    onSearchChange({ ...searchParams, [name]: value });
  };

  return (
    <div className="search-container">
      <div className="search-field">
        <label htmlFor="type">Looking to</label>
        <select 
          id="type" 
          name="type" 
          className="search-select"
          value={searchParams.type}
          onChange={handleChange}
        >
          <option value="">Any</option>
          <option value="Buy">Buy</option>
          <option value="Rent">Rent</option>
        </select>
      </div>

      <div className="search-field">
        <label htmlFor="city">City</label>
        <select 
          id="city" 
          name="city" 
          className="search-select"
          value={searchParams.city}
          onChange={handleChange}
        >
          <option value="">All Cities</option>
          {cities.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>
      </div>

      <div className="search-field">
        <label htmlFor="property_type">Property Type</label>
        <select 
          id="property_type" 
          name="property_type" 
          className="search-select"
          value={searchParams.property_type}
          onChange={handleChange}
        >
          <option value="">All Types</option>
          <option value="flat">Flat</option>
          <option value="house">House</option>
        </select>
      </div>

      <div className="search-field">
        <label htmlFor="min_price">Min Budget (₹)</label>
        <input 
          type="number" 
          id="min_price" 
          name="min_price" 
          className="search-input"
          placeholder="Min"
          value={searchParams.min_price}
          onChange={handleChange}
        />
      </div>

      <div className="search-field">
        <label htmlFor="max_price">Max Budget (₹)</label>
        <input 
          type="number" 
          id="max_price" 
          name="max_price" 
          className="search-input"
          placeholder="Max"
          value={searchParams.max_price}
          onChange={handleChange}
        />
      </div>

      <button className="search-btn" onClick={onSearch}>
        <Search size={20} />
        Search
      </button>
    </div>
  );
};

export default SearchBar;

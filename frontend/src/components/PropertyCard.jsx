import React from 'react';
import { Bed, Bath, Square, MapPin } from 'lucide-react';

const PropertyCard = ({ property }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="property-card">
      <div className="image-container">
        <img src={property.image_url} alt={property.title} className="card-image" />
        <span className="card-badge">{property.type}</span>
        <span className="card-price">{formatPrice(property.price)}</span>
      </div>
      
      <div className="card-content">
        <h3 className="card-title">{property.title}</h3>
        <p className="card-location">
          <MapPin size={16} />
          {property.city}
        </p>
        
        <div className="card-features">
          <div className="feature">
            <Bed size={18} className="feature-icon" />
            <span>{property.bedrooms} Beds</span>
          </div>
          <div className="feature">
            <Bath size={18} className="feature-icon" />
            <span>{property.bathrooms} Baths</span>
          </div>
          <div className="feature">
            <Square size={18} className="feature-icon" />
            <span>{property.area_sqft} sqft</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;

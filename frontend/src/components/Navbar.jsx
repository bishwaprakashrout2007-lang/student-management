import React from 'react';
import { Building2 } from 'lucide-react';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="nav-content">
        <a href="/" className="logo">
          <Building2 size={32} />
          <span>Roof Hunt</span>
        </a>
      </div>
    </nav>
  );
};

export default Navbar;

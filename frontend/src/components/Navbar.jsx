function Navbar() {
  return (
    <header className="navbar">

      <a href="#home" className="navbar-brand">
        <span className="brand-icon">🌾</span>

        <div>
          <strong>
            Smart Crop <span>AI</span>
          </strong>

          <small>
            Intelligent Agriculture
          </small>
        </div>
      </a>

      <nav className="navbar-links">
        <a href="#home">Home</a>
        <a href="#predict">Predict</a>
        <a href="#about">About</a>
      </nav>

      <a
        href="#predict"
        className="navbar-button"
      >
        Predict Yield
      </a>

    </header>
  );
}

export default Navbar;
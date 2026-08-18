function Hero() {
  return (
    <section className="hero" id="home">

      <div className="hero-background-circle circle-one" />
      <div className="hero-background-circle circle-two" />

      <div className="hero-content">

        <div className="hero-badge">
          <span>✦</span>
          AI POWERED AGRICULTURE
        </div>

        <h1>
          Smart Crop Yield
          <span>Prediction System</span>
        </h1>

        <p>
          Predict crop yield using machine learning,
          historical agricultural data and climate
          information.
        </p>

        <div className="hero-actions">

          <a
            href="#predict"
            className="hero-primary-button"
          >
            🌱 Start Prediction
            <span>→</span>
          </a>

          <a
            href="#about"
            className="hero-secondary-button"
          >
            Learn More
          </a>

        </div>

        <div className="hero-stats">

          <div>
            <strong>252K+</strong>
            <span>Training Records</span>
          </div>

          <div>
            <strong>55</strong>
            <span>Crops</span>
          </div>

          <div>
            <strong>21</strong>
            <span>Years of Data</span>
          </div>

          <div>
            <strong>AI</strong>
            <span>CatBoost Model</span>
          </div>

        </div>

      </div>

    </section>
  );
}

export default Hero;
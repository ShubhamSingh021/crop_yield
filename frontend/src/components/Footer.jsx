function Footer() {
  return (
    <footer className="footer">

      <div className="footer-content">

        <div className="footer-brand">

          <span>🌾</span>

          <div>
            <strong>
              Smart Crop AI
            </strong>

            <small>
              Intelligent Agriculture
            </small>
          </div>

        </div>


        <div className="footer-tech">

          <span>
            CatBoost
          </span>

          <span>•</span>

          <span>
            Historical Climate
          </span>

          <span>•</span>

          <span>
            OpenWeather
          </span>

        </div>

      </div>


      <div className="footer-bottom">

        <span>
          © {new Date().getFullYear()} Smart Crop AI
        </span>

        <span>
          Machine Learning Based Crop Yield Prediction
        </span>

      </div>

    </footer>
  );
}

export default Footer;
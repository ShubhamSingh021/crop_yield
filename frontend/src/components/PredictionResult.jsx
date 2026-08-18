function PredictionResult({
  result,
  onPredictAnother,
}) {

  const climate =
    result?.climate_used_for_prediction;

  const weather =
    result?.current_weather;

  const location =
    result?.location;


  return (

    <section className="prediction-result">


      {/* =====================================================
          PREDICTION RESULT
      ===================================================== */}

      <div className="yield-card">

        <div className="yield-label">
          PREDICTION RESULT
        </div>


        <div className="yield-main">

          <span className="yield-icon">
            🌾
          </span>

          <span className="yield-value">
            {result?.predicted_yield ?? "-"}
          </span>

        </div>


        <div className="yield-unit">

          {result?.unit ||
            "dataset yield units"}

        </div>

      </div>


      {/* =====================================================
          STATUS
      ===================================================== */}

      <div className="prediction-status">

        ✓ Prediction Complete

      </div>


      {/* =====================================================
          BASIC INFORMATION
      ===================================================== */}

      <div className="prediction-info-grid">


        {/* CROP */}

        <div className="info-card">

          <div className="info-icon">
            🌱
          </div>

          <div className="info-content">

            <span className="info-label">
              Crop
            </span>

            <strong>
              {result?.crop || "-"}
            </strong>

          </div>

        </div>


        {/* LOCATION */}

        <div className="info-card">

          <div className="info-icon">
            📍
          </div>

          <div className="info-content">

            <span className="info-label">
              Location
            </span>

            <strong>
              {location?.district || "-"}
            </strong>

            <small>
              {location?.state || "-"}
            </small>

          </div>

        </div>


        {/* PREDICTION YEAR */}

        <div className="info-card">

          <div className="info-icon">
            📅
          </div>

          <div className="info-content">

            <span className="info-label">
              Prediction Year
            </span>

            <strong>
              {result?.prediction_year ?? "-"}
            </strong>

          </div>

        </div>


        {/* SEASON */}

        <div className="info-card">

          <div className="info-icon">
            🌦️
          </div>

          <div className="info-content">

            <span className="info-label">
              Season
            </span>

            <strong>
              {result?.season || "-"}
            </strong>

          </div>

        </div>


        {/* AREA */}

        <div className="info-card">

          <div className="info-icon">
            📐
          </div>

          <div className="info-content">

            <span className="info-label">
              Cultivated Area
            </span>

            <strong>
              {result?.area ?? "-"}
            </strong>

            <small>
              Dataset area units
            </small>

          </div>

        </div>

      </div>


      {/* =====================================================
          CLIMATE
      ===================================================== */}

      <div className="data-section climate-section">

        <div className="section-heading">

          <div>

            <h3>
              Climate Used for Prediction
            </h3>

            <p>
              Historical climate values used by
              the ML model
            </p>

          </div>

        </div>


        <div className="data-grid">


          {/* RAINFALL */}

          <div className="data-card">

            <div className="data-icon">
              🌧️
            </div>

            <div>

              <span>
                Rainfall
              </span>

              <strong>
                {climate?.rainfall_mm ?? "-"} mm
              </strong>

            </div>

          </div>


          {/* TEMPERATURE */}

          <div className="data-card">

            <div className="data-icon">
              🌡️
            </div>

            <div>

              <span>
                Temperature
              </span>

              <strong>
                {climate?.temperature_c ?? "-"} °C
              </strong>

            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          CURRENT WEATHER
      ===================================================== */}

      <div className="data-section weather-section">

        <div className="section-heading">

          <div>

            <h3>
              Current Weather
            </h3>

            <p>
              Current conditions from OpenWeather
            </p>

          </div>

        </div>


        <div className="weather-grid">


          {/* TEMPERATURE */}

          <div className="data-card">

            <div className="data-icon">
              🌡️
            </div>

            <div>

              <span>
                Temperature
              </span>

              <strong>
                {weather?.temperature_c ?? "-"} °C
              </strong>

            </div>

          </div>


          {/* RAINFALL */}

          <div className="data-card">

            <div className="data-icon">
              🌧️
            </div>

            <div>

              <span>
                Rainfall
              </span>

              <strong>
                {weather?.rainfall_mm_1h ?? 0} mm/h
              </strong>

            </div>

          </div>


          {/* CONDITIONS */}

          <div className="data-card">

            <div className="data-icon">
              ☁️
            </div>

            <div>

              <span>
                Conditions
              </span>

              <strong className="condition-text">
                {weather?.description || "-"}
              </strong>

            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          PREDICT ANOTHER CROP
      ===================================================== */}

      <div className="another-prediction">

        <button
          type="button"
          className="another-prediction-btn"
          onClick={() => {

            console.log(
              "Predict Another Crop clicked"
            );

            if (
              typeof onPredictAnother ===
              "function"
            ) {

              onPredictAnother();

            } else {

              console.error(
                "onPredictAnother is not a function"
              );

            }

          }}
        >

          🌱 Predict Another Crop

        </button>

      </div>


    </section>

  );
}


export default PredictionResult;
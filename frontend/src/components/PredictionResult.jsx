function PredictionResult({
  result,
  onPredictAnother,
}) {
  const climate = result?.climate_used_for_prediction;
  const weather = result?.current_weather;
  const location = result?.location;
  const suitability = result?.suitability;
  const confidence = result?.confidence;

  // =====================================================
  // FORMAT NUMBER
  // =====================================================

  const formatNumber = (value, decimals = 0) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "-";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
      return "-";
    }

    return number.toLocaleString("en-IN", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  // =====================================================
  // SUITABILITY CONFIGURATION
  // =====================================================

  const suitabilityLevel =
    suitability?.level?.toLowerCase() ||
    "unknown";

  const suitabilityConfig = {
    high: {
      icon: "✓",
      title: "High Historical Support",
      className: "suitability-high",
    },

    medium: {
      icon: "●",
      title: "Moderate Historical Support",
      className: "suitability-medium",
    },

    low: {
      icon: "⚠",
      title: "Low Historical Support",
      className: "suitability-low",
    },

    unknown: {
      icon: "?",
      title: "Historical Support Unavailable",
      className: "suitability-unknown",
    },
  };

  const currentSuitability =
    suitabilityConfig[suitabilityLevel] ||
    suitabilityConfig.unknown;

  // =====================================================
  // CONFIDENCE
  // =====================================================

  const confidenceValue =
    confidence?.score !== undefined &&
    confidence?.score !== null
      ? Number(confidence.score)
      : null;

  const confidencePercentage =
    confidenceValue !== null
      ? Math.min(
          100,
          Math.max(
            0,
            confidenceValue <= 1
              ? confidenceValue * 100
              : confidenceValue
          )
        )
      : null;

  // =====================================================
  // UI
  // =====================================================

  return (
    <section className="prediction-result">

      {/* ================================================
          MAIN YIELD RESULT
      ================================================= */}

      <div className="yield-card">

        <div className="yield-label">
          PREDICTED CROP YIELD
        </div>

        <div className="yield-main">

          <span className="yield-icon">
            🌾
          </span>

          <span className="yield-value">
            {formatNumber(
              result?.predicted_yield,
              2
            )}
          </span>

        </div>

        <div className="yield-unit">
          {result?.unit ||
            "Yield (tonnes/hectare"}
        </div>

      </div>


      {/* ================================================
          STATUS
      ================================================= */}

      <div className="prediction-status">
        ✓ Prediction Complete
      </div>


      {/* ================================================
          SUITABILITY
      ================================================= */}

      <div
        className={`suitability-card ${currentSuitability.className}`}
      >

        <div className="suitability-header">

          <div className="suitability-icon">
            {currentSuitability.icon}
          </div>

          <div className="suitability-title">

            <span className="suitability-label">
              PREDICTION RELIABILITY
            </span>

            <h3>
              {suitability?.label ||
                currentSuitability.title}
            </h3>

          </div>

        </div>


        <p className="suitability-reason">

          {suitability?.reason ||
            "Historical support information is not available for this prediction."}

        </p>


        <div className="suitability-details">

          <div className="suitability-detail">

            <span>
              📊 Historical Records
            </span>

            <strong>
              {formatNumber(
                suitability?.historical_records
              )}
            </strong>

          </div>


          <div className="suitability-detail">

            <span>
              🗂 Data Source
            </span>

            <strong>
              {suitability?.data_source ||
                "Not available"}
            </strong>

          </div>

        </div>

      </div>


      {/* ================================================
          CONFIDENCE
      ================================================= */}

      {confidence && (

        <div className="confidence-card">

          <div className="confidence-header">

            <div>

              <span className="confidence-label">
                MODEL CONFIDENCE
              </span>

              <h3>
                {confidence?.label ||
                  "Prediction Confidence"}
              </h3>

            </div>

            {confidencePercentage !== null && (

              <strong className="confidence-value">
                {formatNumber(
                  confidencePercentage,
                  0
                )}%
              </strong>

            )}

          </div>


          {confidencePercentage !== null && (

            <div className="confidence-bar">

              <div
                className="confidence-progress"
                style={{
                  width: `${confidencePercentage}%`,
                }}
              />

            </div>

          )}


          {confidence?.reason && (

            <p className="confidence-reason">
              {confidence.reason}
            </p>

          )}

        </div>

      )}


      {/* ================================================
          BASIC INFORMATION
      ================================================= */}

      <div className="prediction-info-grid">

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


        <div className="info-card">

          <div className="info-icon">
            📐
          </div>

          <div className="info-content">

            <span className="info-label">
              Cultivated Area
            </span>

            <strong>
              {formatNumber(result?.area)}
            </strong>

            <small>
              Hectares
            </small>

          </div>

        </div>

      </div>


      {/* ================================================
          CLIMATE
      ================================================= */}

      <div className="data-section climate-section">

        <div className="section-heading">

          <div>

            <h3>
              Climate Used for Prediction
            </h3>

            <p>
              Climate values used as input
              for the ML prediction
            </p>

          </div>

        </div>


        <div className="data-grid">

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


      {/* ================================================
          CURRENT WEATHER
      ================================================= */}

      <div className="data-section weather-section">

        <div className="section-heading">

          <div>

            <h3>
              Current Weather
            </h3>

            <p>
              Current weather conditions
              for the selected location
            </p>

          </div>

        </div>


        <div className="weather-grid">

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


      {/* ================================================
          PREDICT AGAIN
      ================================================= */}

      <div className="another-prediction">

        <button
          type="button"
          className="another-prediction-btn"
          onClick={() => {

            if (
              typeof onPredictAnother ===
              "function"
            ) {
              onPredictAnother();
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
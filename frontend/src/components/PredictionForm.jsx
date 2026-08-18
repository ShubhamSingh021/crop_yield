import CustomSelect from "./CustomSelect";
import PredictionResult from "./PredictionResult";

function PredictionForm({
  formData,
  options,
  handleChange,
  handleStateChange,
  handleSubmit,
  loading,
  error,
  result,
  onPredictAnother,
}) {

  // =====================================================
  // GET DISTRICTS FOR SELECTED STATE
  // =====================================================

  const districts =
    options?.districts?.[formData.State] || [];


  return (
    <section
      className="prediction-section"
      id="predict"
    >

      {/* =====================================================
          SECTION HEADING
      ===================================================== */}

      <div className="section-heading">

        <p className="section-tagline">
          CROP PREDICTION
        </p>

        <h2>
          Enter Agricultural Details
        </h2>

        <p>
          Provide the basic information about your
          crop and cultivation area.
        </p>

      </div>


      {/* =====================================================
          FORM CARD
      ===================================================== */}

      <div
        className={`prediction-card ${
            loading ? "prediction-loading" : ""
        }`}
        >
            
        {/* FORM HEADER */}

        <div className="prediction-card-header">

          <div className="prediction-card-icon">
            🌱
          </div>

          <div>

            <h3>
              Crop Information
            </h3>

            <p>
              Tell us about the crop you want to
              analyze.
            </p>

          </div>

        </div>


        {/* =================================================
            FORM
        ================================================= */}

        <form
          className="prediction-form"
          onSubmit={handleSubmit}
        >

          <div className="form-grid">


            {/* =================================================
                STATE
            ================================================= */}

            <div className="form-group">

              <label>
                State
              </label>

              <CustomSelect
                name="State"
                value={formData.State}
                onChange={handleStateChange}
                options={options?.states || []}
                placeholder="Choose a state"
              />

            </div>


            {/* =================================================
                DISTRICT
            ================================================= */}

            <div className="form-group">

              <label>
                District
              </label>

              <CustomSelect
                name="District"
                value={formData.District}
                onChange={handleChange}
                options={districts}
                placeholder={
                  formData.State
                    ? "Choose a district"
                    : "Select state first"
                }
                disabled={!formData.State}
              />

            </div>


            {/* =================================================
                CROP
            ================================================= */}

            <div className="form-group">

              <label>
                Crop
              </label>

              <CustomSelect
                name="Crop"
                value={formData.Crop}
                onChange={handleChange}
                options={options?.crops || []}
                placeholder="Choose a crop"
              />

            </div>


            {/* =================================================
                SEASON
            ================================================= */}

            <div className="form-group">

              <label>
                Season
              </label>

              <CustomSelect
                name="Season"
                value={formData.Season}
                onChange={handleChange}
                options={options?.seasons || []}
                placeholder="Choose a season"
              />

            </div>


            {/* =================================================
                CROP YEAR
            ================================================= */}

            <div className="form-group">

              <label>
                Crop Year
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  📅
                </span>

                <input
                  type="number"
                  name="Crop_Year"
                  value={formData.Crop_Year}
                  onChange={handleChange}
                  min="1997"
                  max="2100"
                  placeholder="2026"
                  required
                />

              </div>

              <small>
                Enter the year for which you want
                the prediction.
              </small>

            </div>


            {/* =================================================
                CULTIVATED AREA
            ================================================= */}

            <div className="form-group">

              <label>
                Cultivated Area
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  📐
                </span>

                <input
                  type="number"
                  name="Area"
                  value={formData.Area}
                  onChange={handleChange}
                  min="0.01"
                  step="0.01"
                  placeholder="Example: 5000"
                  required
                />

              </div>

              <small>
                Use the same area unit as the
                training dataset.
              </small>

            </div>

          </div>


          {/* =================================================
              ERROR
          ================================================= */}

          {error && (

            <div className="form-error">

              <span>
                ⚠
              </span>

              <div>

                <strong>
                  Prediction failed
                </strong>

                <p>
                  {error}
                </p>

              </div>

            </div>

          )}


          {/* =================================================
              PREDICT BUTTON
          ================================================= */}

          <button
            type="submit"
            className="predict-button"
            disabled={loading}
          >

            {loading ? (

              <>
                <span className="loading-spinner" />
                Predicting...
              </>

            ) : (

              <>
                🌾 Predict Crop Yield
                <span>→</span>
              </>

            )}

          </button>


          {/* =================================================
              FORM NOTE
          ================================================= */}

          <p className="form-note">

            Your prediction uses the trained CatBoost
            machine learning model with historical
            climate information.

          </p>

        </form>

      </div>


      {/* =====================================================
          RESULT
      ===================================================== */}

      {result && (

        <PredictionResult
          result={result}
          onPredictAnother={onPredictAnother}
        />

      )}

    </section>
  );
}

export default PredictionForm;
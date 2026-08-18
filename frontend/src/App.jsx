import { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import PredictionForm from "./components/PredictionForm";
import Footer from "./components/Footer";
import Loading from "./components/Loading";

import {
  getOptions,
  predictYield,
} from "./services/api";

import "./App.css";


function App() {

  // =====================================================
  // OPTIONS
  // =====================================================

  const [options, setOptions] = useState({
    states: [],
    districts: {},
    crops: [],
    seasons: [],
  });


  // =====================================================
  // FORM DATA
  // =====================================================

  const [formData, setFormData] = useState({
    State: "",
    District: "",
    Crop: "",
    Season: "",
    Crop_Year: new Date().getFullYear(),
    Area: "",
  });


  // =====================================================
  // UI STATE
  // =====================================================

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [optionsLoading, setOptionsLoading] =
    useState(true);

  const [error, setError] = useState("");


  // =====================================================
  // LOAD OPTIONS
  // =====================================================

  useEffect(() => {

    const loadOptions = async () => {

      try {

        const data = await getOptions();

        console.log("Options received:", data);

        setOptions({
          states: data?.states || [],
          districts: data?.districts || {},
          crops: data?.crops || [],
          seasons: data?.seasons || [],
        });

      } catch (err) {

        console.error(
          "Options loading error:",
          err
        );

        setError(
          "Could not connect to the prediction server."
        );

      } finally {

        setOptionsLoading(false);

      }

    };


    loadOptions();

  }, []);


  // =====================================================
  // HANDLE STATE CHANGE
  // =====================================================

  const handleStateChange = (event) => {

    const { value } = event.target;

    setFormData((previous) => ({
      ...previous,

      State: value,

      // State changed → reset district
      District: "",
    }));

    setResult(null);

    setError("");

  };


  // =====================================================
  // HANDLE OTHER INPUT CHANGES
  // =====================================================

  const handleChange = (event) => {

    const {
      name,
      value,
    } = event.target;

    setFormData((previous) => ({
      ...previous,

      [name]: value,
    }));

    // Remove previous prediction
    // when user changes an input.

    setResult(null);

    setError("");

  };


  // =====================================================
  // VALIDATION
  // =====================================================

  const validateForm = () => {

    // State

    if (!formData.State) {

      setError(
        "Please select a state."
      );

      return false;
    }


    // District

    if (!formData.District) {

      setError(
        "Please select a district."
      );

      return false;
    }


    // Crop

    if (!formData.Crop) {

      setError(
        "Please select a crop."
      );

      return false;
    }


    // Season

    if (!formData.Season) {

      setError(
        "Please select a season."
      );

      return false;
    }


    // Crop Year

    const year = Number(
      formData.Crop_Year
    );

    if (
      !formData.Crop_Year ||
      year < 1997 ||
      year > 2100
    ) {

      setError(
        "Please enter a valid crop year between 1997 and 2100."
      );

      return false;
    }


    // Area

    const area = Number(
      formData.Area
    );

    if (
      !formData.Area ||
      !Number.isFinite(area) ||
      area <= 0
    ) {

      setError(
        "Please enter a valid cultivated area."
      );

      return false;
    }


    return true;

  };


  // =====================================================
  // PREDICTION
  // =====================================================

  const handleSubmit = async (event) => {

    event.preventDefault();

    // Clear previous result/error
    setError("");
    setResult(null);


    // Validate form

    const isValid =
      validateForm();

    if (!isValid) {
      return;
    }


    setLoading(true);


    try {

      // =================================================
      // API PAYLOAD
      // =================================================

      const payload = {

        State:
          formData.State,

        District:
          formData.District,

        Crop:
          formData.Crop,

        Season:
          formData.Season,

        Crop_Year:
          Number(formData.Crop_Year),

        Area:
          Number(formData.Area),

      };


      console.log(
        "Prediction payload:",
        payload
      );


      // =================================================
      // CALL BACKEND
      // =================================================

      const data =
        await predictYield(payload);


      console.log(
        "Prediction response:",
        data
      );


      // =================================================
      // SAVE RESULT
      // =================================================

      setResult(data);


      // =================================================
      // SCROLL TO RESULT
      // =================================================

      setTimeout(() => {

        const resultElement =
          document.querySelector(
            ".prediction-result"
          );

        if (resultElement) {

          resultElement.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });

        }

      }, 100);


    } catch (err) {

      console.error(
        "Prediction error:",
        err
      );


      let message =
        "Prediction failed. Please try again.";


      // =================================================
      // FASTAPI ERROR
      // =================================================

      if (
        err?.response?.data?.detail
      ) {

        if (
          typeof err.response.data.detail ===
          "string"
        ) {

          message =
            err.response.data.detail;

        }

      }


      setError(message);

    } finally {

      setLoading(false);

    }

  };


  // =====================================================
  // PREDICT ANOTHER CROP
  // =====================================================

  const handlePredictAnother = () => {

    console.log(
      "Predict Another Crop clicked"
    );


    // Remove prediction

    setResult(null);


    // Remove error

    setError("");


    // Reset form

    setFormData({
      State: "",
      District: "",
      Crop: "",
      Season: "",
      Crop_Year:
        new Date().getFullYear(),
      Area: "",
    });


    // Stop loading

    setLoading(false);


    // Scroll back to prediction form

    setTimeout(() => {

      const formElement =
        document.querySelector(
          ".prediction-section"
        );

      if (formElement) {

        formElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

      } else {

        window.scrollTo({
          top: 0,
          behavior: "smooth",
        });

      }

    }, 50);

  };


  // =====================================================
  // LOADING SCREEN
  // =====================================================

  if (optionsLoading) {

    return <Loading />;

  }


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="app">

      {/* NAVBAR */}

      <Navbar />


      {/* HERO */}

      <Hero />


      {/* MAIN */}

      <main>

        <PredictionForm
          formData={formData}
          options={options}

          handleChange={
            handleChange
          }

          handleStateChange={
            handleStateChange
          }

          handleSubmit={
            handleSubmit
          }

          loading={loading}

          error={error}

          result={result}

          onPredictAnother={
            handlePredictAnother
          }
        />

      </main>


      {/* FOOTER */}

      <Footer />

    </div>

  );
}


export default App;
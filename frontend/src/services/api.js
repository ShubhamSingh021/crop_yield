import axios from "axios";

// =====================================================
// API URL
// =====================================================

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


// =====================================================
// AXIOS INSTANCE
// =====================================================

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});


// =====================================================
// GET OPTIONS
// =====================================================

export const getOptions = async () => {

  const response =
    await api.get("/options");

  return response.data;
};


// =====================================================
// PREDICT YIELD
// =====================================================

export const predictYield = async (data) => {

  const response =
    await api.post("/predict", data);

  return response.data;
};


export default api;
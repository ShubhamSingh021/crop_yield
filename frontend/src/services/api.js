import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

export const getOptions = async () => {
  const response = await api.get("/options");
  return response.data;
};

export const predictYield = async (data) => {
  const response = await api.post("/predict", data);
  return response.data;
};

export default api;
import axios from "axios";
import { API_BASE_URL } from "../config";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const healthCheck = () => api.get("/health");
export const getModelInfo = () => api.get("/model-info");
export const getFeatures = () => api.get("/features");
export const predict = (payload) => api.post("/predict", payload);
export const explain = (payload) => api.post("/explain", payload);

export default api;

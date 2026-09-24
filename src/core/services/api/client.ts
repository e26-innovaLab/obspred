import axios from 'axios';
import { env } from '../../config/env';

// Cliente HTTP único hacia la API interna (Backend).
// El contrato de endpoints se acuerda con Backend (principio 02 del roadmap).
export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15000,
});

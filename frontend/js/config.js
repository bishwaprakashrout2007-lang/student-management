/**
 * config.js  —  Frontend Configuration
 *
 * Set API_BASE_URL to your deployed backend URL on Vercel/Railway/Render.
 * For local development, it automatically falls back to localhost:5000.
 *
 * HOW TO USE:
 *   - Local dev  : leave as-is, it picks up http://localhost:5000
 *   - Production : replace the string below with your real backend URL
 *                  e.g. 'https://student-management-api.vercel.app'
 */

const API_BASE_URL =
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'          // Local development
    : 'https://YOUR-BACKEND-URL.vercel.app';  // ← Replace with your deployed backend URL

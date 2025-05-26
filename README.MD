# SolarRally - EV Charging Control & Monitoring System

A hybrid solar + grid-powered EV charging station with real-time control, monitoring, and billing via a web-based dashboard and backend services.

## Project Status (as of 2025-05-26)

We are currently progressing through the development roadmap outlined in `Project_Solar_Rally.txt`.

**Completed:**
*   **Phase 0 – Project Initialization:**
    *   Git repository and basic folder structure established.
    *   Environment configuration (`.env`) defined.
    *   Docker Compose setup for MQTT broker (Mosquitto).
*   **Phase 1 – Embedded Interface Mock:**
    *   MQTT message structure defined for telemetry.
    *   Dummy data publisher (`scripts/mock_publisher.py`) created and functional, simulating an ESP32.
    *   JSON data frame for telemetry (V, I, P, energy sources, status, timestamp) documented and implemented.

**In Progress / Next Steps:**
*   **Phase 0 – Project Initialization:**
    *   Finalize Docker Compose setup for Backend API and Database.
*   **Phase 2 – Backend API (FastAPI):**
    *   Scaffold `/sessions` REST endpoints.
    *   Implement WebSocket route `/live/{session_id}`.
    *   Develop cost computation logic.
    *   Integrate with PostgreSQL (TimescaleDB).
    *   Add JWT authentication.
*   **Phase 3 – Frontend Dashboard (React + Tailwind):**
    *   Begin UI development for the live dashboard and session summaries.

Further details can befound in `Project_Solar_Rally.txt` and the `docs/` directory. 
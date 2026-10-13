# Architecture
```mermaid
flowchart LR
  U[Browser] --> R[React + TypeScript UI]
  R --> A[FastAPI /api/v1]
  A --> D[Diagnostics services]
  A --> I[Incident service]
  A --> E[Report exporters]
  I --> S[(SQLite)]
  D --> O[OS / DNS / TCP APIs]
```
Diagnostics are isolated from HTTP and storage. System-dependent calls can be mocked. The API validates requests and returns stable error envelopes. React never invokes OS commands.

# Capability: Spatial LBS & Restaurant Retrieval
Capability Path: `openspec/specs/spatial-lbs/spec.md`

## Overview
Retrieves physical restaurant meals and convenience store options within physical walking radius using great-circle Haversine distance calculations.

---

### Requirement: Geospatial Distance Calculation
The system SHALL compute physical distance in kilometers and estimate walking duration.

#### Scenario: Distance and Time Calculation
- **GIVEN** user coordinates $(lat_1, lon_1)$ and restaurant coordinates $(lat_2, lon_2)$
- **WHEN** spatial query is executed
- **THEN** great-circle distance $d$ SHALL be computed via the Haversine formula
- **AND** walking time SHALL be estimated as $\lceil d \times 12 \rceil$ minutes

---

### Requirement: Graceful Search Radius Expansion
The system SHALL expand search radius if fewer than 4 candidates are located in the initial radius.

#### Scenario: Sparse location fallback
- **GIVEN** an initial search radius of $1.2\,\text{km}$ returning fewer than 4 meals
- **WHEN** retrieval executes
- **THEN** the search radius SHALL be automatically expanded to $2.5\,\text{km}$

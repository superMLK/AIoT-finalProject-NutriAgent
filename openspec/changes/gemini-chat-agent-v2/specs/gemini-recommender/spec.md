# Delta Spec: Gemini API Contextual Recommender & Conversational Agent
Capability Path: `openspec/changes/gemini-chat-agent-v2/specs/gemini-recommender/spec.md`

## Requirement: Gemini API Integration Replacing Neural Network
The system SHALL replace the PyTorch Deep Q-Network (`NutriQNetwork`) with a Gemini API-powered contextual recommender and conversational agent (`GeminiRecommender`), while maintaining online preference weight adaptation (`user_flavor_weights`).

### Scenario: Contextual Meal Ranking & Feedback Adaptation
- **GIVEN** a pool of clinically safe candidate meals and user context
- **WHEN** `rank_meals()` and `update_online()` are invoked
- **THEN** the system SHALL score candidates using user preference weights, semantic craving match, nutritional fit, and distance penalty
- **AND** negative feedback (`too_oily`) SHALL decrease savory weight and boost clean/light weight

## Requirement: Never Relax Clinical Gate on Empty Safe Pool
The system SHALL NOT relax clinical or allergen rules when the safe candidate pool is empty.

### Scenario: Empty Safe Candidate Pool
- **GIVEN** a user profile and location where all nearby meals violate clinical or allergen constraints
- **WHEN** `run_recommendation()` is executed
- **THEN** the system SHALL return zero unsafe recommendations (`CVR = 0.0%`, `AVR = 0.0%`) and provide `order_tips`

## Requirement: ChatGPT-Style Conversational Agent Interface
The web application SHALL provide a multi-turn conversational chat interface where users can converse with NutriAgent in natural language, view reasoning steps, and interact with recommended meal cards.

### Scenario: Conversational Recommendation & Follow-up
- **GIVEN** a user typing a natural language dietary request in the chat UI
- **WHEN** `/api/chat` processes the message
- **THEN** the agent SHALL parse intent, execute the 8-stage clinical/IoT/LBS pipeline, and return a grounded conversational response with Top-3 meal recommendations and reasoning trace

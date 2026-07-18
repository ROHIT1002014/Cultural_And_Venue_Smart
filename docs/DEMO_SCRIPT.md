# Step-by-Step Demonstration Script & UI Walkthrough

This document provides a step-by-step presentation script and visual walkthrough designed for technical evaluations, stakeholder demos, and system testing.

---

## 🎭 Presentation Flow

### Phase 1: Authentication & Role-Based Access Control (RBAC)
1. **Open the Web Application (`http://localhost:5173`)**:
   - The user lands on the modern, vibrant dark-mode login interface.
   - **Action**: Log in with administrator credentials (`admin@cultural-copilot.org` / `SecurePassword123!`).
   - **Visual Verification**: The top navigation bar displays a verified badge and unlocks the **Admin & Operations Dashboard** tab alongside the **AI Copilot Chat** and **Venue Map** tabs.

---

### Phase 2: Multi-Agent AI Chat & Streaming Tool Execution (`ChatUI`)
1. **Navigate to the AI Copilot Tab**:
   - The user opens the chat interface featuring language switcher (English / Spanish / Hindi) and voice input simulation toggle.
2. **Execute Multi-Agent Complex Query**:
   - **Input Query**: *"Where is the nearest wheelchair accessible restroom on the 2nd floor near Hall C, and can you check if Lot B has any available EV charging or accessible parking spots right now?"*
3. **Observing Real-Time Streaming & Tool Calling Visualization**:
   - The chat interface displays an active status badge: `🤖 Orchestrator routing query...`
   - Next, visual tool execution cards appear in real-time before the text streams:
     - 🧭 `NavigationAgent executing tool: find_poi(category="restroom", accessible=true, floor=2)`
     - 🚗 `ParkingAgent executing tool: check_parking_status(lot_name="Lot B")`
   - Finally, the grounded, helpful response streams cleanly via SSE:
     > *"The nearest accessible restroom on the 2nd floor is adjacent to Hall C (Room 204). Regarding parking, Lot B currently has 14 total spots available, including 3 accessible spaces right next to the North Entrance and 2 active EV fast chargers ready for use."*
   - A green safety badge confirms: `🛡️ Grounding Score: 0.96 | PII Protected | Verified by Gemini 1.5 Pro`

---

### Phase 3: Interactive Venue Navigation & Accessibility Map (`MapUI`)
1. **Switch to the Interactive Venue Map Tab**:
   - The map dynamically highlights Hall C, Room 204 (Restroom), and Lot B with custom SVG markers.
2. **Toggle Accessibility Route Layer**:
   - The user clicks the **"Wheelchair Accessible Route"** toggle. The map instantly redraws a step-by-step highlighted blue path avoiding escalators and directing via Elevator #2.

---

### Phase 4: Admin Operations, Crowd Density & Emergency Evacuation (`AdminDashboard`)
1. **Switch to Admin Operations Tab**:
   - Displays real-time charts: Live Crowd Density across Hall A, B, C, Volunteer Availability status, and API Request Throughput (`850 req/sec`).
2. **Simulate Priority Emergency Evacuation Alert**:
   - The administrator clicks the **"🚨 Trigger Emergency Evacuation"** button and confirms `Fire Alert in Hall B`.
   - **Result**: All active user chat sessions and map views instantly receive a high-priority, pulsing red WebSocket broadcast banner directing everyone to the nearest verified emergency exit (`Exit North-West`).

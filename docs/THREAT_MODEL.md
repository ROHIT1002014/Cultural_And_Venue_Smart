# Threat Model & Security Guide (STRIDE & Defense-In-Depth)

This document formalizes our threat assessment using the **STRIDE** methodology and details our security architecture designed to defend against web vulnerabilities, prompt injection attacks, and insider threats.

---

## 1. STRIDE Threat Analysis Matrix

| Threat Category | Potential Attack Vector | Mitigations & Architectural Controls |
| :--- | :--- | :--- |
| **Spoofing Identity** | Adversaries stealing JWT access tokens or forging refresh tokens to impersonate administrators. | • Short access token TTL (15m).<br>• Cryptographic verification of signed JWTs.<br>• Refresh token rotation on every use + Redis blacklisting of compromised tokens.<br>• Account locking after 5 failed login attempts. |
| **Tampering with Data** | Intercepting and altering AI prompts, RAG document chunks, or database records. | • TLS 1.3 enforced across all public endpoints.<br>• Signed JWT payloads.<br>• Strict Pydantic input validation preventing parameter injection.<br>• Parameterized SQLAlchemy queries preventing SQL tampering. |
| **Repudiation** | Malicious users or volunteers performing unauthorized actions (e.g., triggering false emergency alerts) and denying responsibility. | • Centralized, append-only `AUDIT_LOG` table tracking all mutations.<br>• Every log includes `user_id`, `ip_address`, `trace_id`, `action`, and precise timestamp.<br>• Audit logs written asynchronously to prevent transaction blocking. |
| **Information Disclosure** | Exposing PII (SSNs, emails, phone numbers) in AI responses or stack traces in error responses. | • `PIIDetector` automatically scans and masks sensitive data before sending prompts to external LLM providers (`Gemini` / `OpenAI`).<br>• Global exception handler converts internal stack traces into generic error messages (`500 Internal Server Error`). |
| **Denial of Service (DoS)** | Sending multi-gigabyte payloads or exhausting LLM token quotas via automated scripts. | • Nginx limits client body size to `10MB`.<br>• Redis sliding-window rate limiter enforces strict request quotas (`SlowAPI`).<br>• Token limits per prompt and strict circuit breakers for external AI API calls. |
| **Elevation of Privilege** | Normal users exploiting API endpoints or tool calls to gain `ADMIN` privileges. | • Granular Role-Based Access Control (`RBAC`) enforced at the presentation dependency level (`require_permissions(...)`).<br>• Least privilege database permissions in production containers. |

---

## 2. Prompt Injection & AI Safety Architecture

Because autonomous agents can execute functions (`Function Calling` / `Tool Calling`), an attacker attempting "indirect prompt injection" (e.g., embedding instructions inside a venue FAQ or user chat) could attempt to trick the agent into exfiltrating data or triggering unauthorized tools.

### Defense Strategy:
1. **Input Sanitization & Heuristic Blocking (`PromptGuard`)**:
   - Checks against known jailbreak patterns (`"DAN"`, `"Ignore previous instructions"`, `"You are now in developer mode"`).
   - Strips dangerous control characters and isolates user input within strict system delimiters (`<user_query>...</user_query>`).
2. **Strict Tool Calling Permissions**:
   - Even if an LLM is tricked into requesting a high-privilege tool execution (e.g., `trigger_emergency_alert`), the system intercepts the call and verifies that the authenticated user (`user.role`) possesses the required `emergency:trigger` permission before executing the domain service.
3. **Output Grounding (`HallucinationGuard`)**:
   - Evaluates the generated answer against retrieved RAG chunks. If the grounding score falls below `0.75`, the system discards the answer and returns a safe fallback message or requests human volunteer intervention.

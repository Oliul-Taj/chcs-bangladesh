I have updated the presentation file to "bangladesh centralized healthcare system.pdf". Based on this and the requirements below, I need to build a nationwide, Vercel-standard Centralized Healthcare System (CHCS) capable of handling millions of concurrent requests. Please execute the following tasks thoroughly without missing technical details.

### 1. Elevator Pitch (speech.md)
Prepare a high-impact, 1.5-minute elevator speech aimed at winning project funding. Focus on the scale, the problem it solves for Bangladesh, and the core innovative features. Save this output as `speech.md`.

### 2. System Architecture & Features
Please design and implement the system based on the following 6 core features, plus any missing critical features you see fit to add for a complete national healthcare ecosystem:

* **Feature 1: Government-Level Epidemic Portal (Disease Outbreak Tracking)**
    * Centralized admin portal for the Ministry of Health.
    * A "Pandemic Outbreak" button for doctors/hospitals to report immediate symptoms.
    * Automated AI clustering of disease similarity by geographical area based on doctor reports and patient counts.
    * System-generated prevention guidelines sourced from researchers and senior medical experts to contain outbreaks.
    * Cross-check verification loop across Hospital, Patient, and Government portals.

* **Feature 2: Dynamic Hospital Grading System**
    * Categorize hospitals into five tiers: **A+** (Top Notch), **A** (Good), **B** (Moderate), **N** (New), and **Z** (Worst Case/Warning).
    * Grades must be clearly displayed on patient reports based on automated surveys and parameters:
        1. Patient serving count (Daily, Weekly, Monthly, Yearly).
        2. Patient satisfaction (Staff behavior survey metrics).
        3. Cure rate vs. unnecessary follow-up session tracking.
        4. Quality of medical equipment (Testing, surgery, diagnosis).
        5. Expert doctor count, geo-location, and private hospital expertise branches.
        6. Cleanliness, food quality, and architectural infrastructure.

* **Feature 3: Strict Regulatory Lifecycle & Auditing**
    * Hospitals must register via license numbers and start at **N** (New) category for the first 6–12 months.
    * If no improvement, they drop to **Z** (Warning) and cannot operate for more than 12 months in Z.
    * Must maintain at least a **B** grade to operate long-term (max 5 years in B before needing to level up to **A**).
    * A designated, structured Auditor Team interface to evaluate parameters and issue certifications.

* **Feature 4: Patient Feedback & Continuous Monitoring**
    * Patient portal for reporting occurrences, malpractice, or poor service, generating a summary list for consumers.
    * Proactive health monitoring system: guides patients through recovery, detects if they are at risk of getting sick again, and suggests preventions.

* **Feature 5: NID/Passport Identity Management & Dummy Data**
    * Profile creation via NID/Passport. Since there is no live government API, create a simulated verification step. Once "verified", it auto-fetches Name, DOB, Father's, and Mother's name.
    * Child accounts *must* be linked to a mandatory Parent Account for authorization.
    * **Provide a list of usable dummy NID/Passport numbers in the response** so I can test login and profile creation immediately.

* **Feature 6: AI Medical Record Scanner & Personal Nurse AI**
    * Centralized reporting where old medical reports (PDFs/Scans) can be uploaded.
    * OCR/Pattern recognition to extract medical history and trends.
    * An AI Personal Nurse agent acting as a medical alarm for medicine reminders and lifestyle guidance.

### 3. Vercel Deployment & Backend Architecture Guide
* Provide a step-by-step guide to hosting this high-throughput system on Vercel.
* Detail how to handle millions of data requests simultaneously (e.g., Serverless/Edge functions, Redis caching layers, connection pooling).
* Guide me on how to structure and upload the backend dummy data files.

### 4. Project Documentation (Word/Markdown Report Structure)
Generate a comprehensive system report structure including:
* Full feature listing and operational user guide.
* System Architecture Diagram description (Scalable Microservices/Edge architecture).
* Coding features and technical stack.
* Placeholder image mappings utilizing the existing screenshots located in the `/CHCS/img/` parent folder.
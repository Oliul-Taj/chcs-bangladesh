# Command & System Specification: Centralized Healthcare System (CHCS) Bangladesh

Implement the nationwide, Vercel-standard Centralized Healthcare System (CHCS) capable of handling millions of concurrent requests. Process the entire set of engineering requirements below. Ensure all mock datasets match the specified directory structures, routing patterns, and data schemas perfectly.

---

## 1. Elevator Pitch (`speech.md`)
Prepare a high-impact, 1.5-minute elevator speech aimed at winning project funding. Focus on structural issues, systemic scalability, the revolutionary grading lifecycle, and saving lives in Bangladesh. Save this output directly to `speech.md`.

---

## 2. Core Features & Architectural Rules

### Feature 1: Government-Level Epidemic Portal (Disease Outbreak Tracking)
* **Interface:** Centralized admin portal for the Ministry of Health.
* **Mechanism:** A dedicated `"Pandemic Outbreak"` trigger button accessible by authorized hospitals/doctors.
* **Automation:** Automated AI clustering of spatial disease similarity based on diagnostic records, localized symptoms, and active patient volume.
* **Resolution:** Real-time generation of action items and prevention guidelines sourced dynamically from research databases and expert senior medical panels.
* **Security:** A secure multi-party verification loop syncing entries across the Patient, Hospital, and Ministry nodes.

### Feature 2: Dynamic Hospital Grading & Performance Matrix
* **Tiering System:** Classify all medical entities cleanly into **A+** (Top Notch), **A** (Good), **B** (Moderate), **N** (New), and **Z** (Critical/Warning).
* **Metrics Matrix:** Grading metrics must evaluate:
  1. Service Volume: Daily, Weekly, Monthly, and Annualized patient throughput.
  2. Public Feedback: Standardized patient metrics judging hospital staff behavior.
  3. Medical Integrity: Clinical recovery curves plotted against uncalled-for or excessive patient follow-up loops.
  4. Diagnostics & Asset Quality: Operating theatre capability, imaging, and lab calibration metrics.
  5. Infrastructure & Logistics: Sanitation, dietary delivery metrics, structural safety, medical specialist densities, and branch distributions.
* **Visibility:** Display active classifications directly on all exported patient summaries.

### Feature 3: Strict Regulatory Lifecycle & Auditing
* **Lifecycle:** New entities register using corporate license codes, placing them initially into the **N** (New) tier for 6–12 months.
* **Enforcement:** Failure to progress drops the institution to **Z** (Warning). Operational lifetime within a **Z** rating is strictly capped at 12 months. Establish a maximal stay of 5 years at a **B** tier; institutions must ascend to **A** or face strict enforcement.
* **Audit System:** An auditor dashboard built explicitly for field agents to execute structural evaluations, parameter logging, and digitally sign tier certifications.

### Feature 4: Patient Feedback, Continuous Care & Spatial Awareness
* **Feedback System:** Unified portal allowing patients to lodge institutional service logs, medical errors, or billing complaints, outputting aggregated consumer reports.
* **Proactive Monitoring:** Adaptive health triggers that track patient recovery trends post-discharge, logging individual risk alerts and rendering personalized preventative action items.
* **Spatial Navigation:** Geo-location tracking for patients to query localized medical facilities sorted by grading tier, including direct transit metrics and Map representations.

### Feature 5: Adaptive Identification Input & Identity Lifecycles
* **Input Architecture (Case Insensitive & Prefix Independent):** * The system must intelligently handle bare identity numbers without forcing users to input prefixes like `NID-`, `nid`, `Pass no`, or `BC -`.
  * The lookup engine must parse strings via regular expression matching or schema verification to determine identity type automatically based on format patterns (e.g., National ID, Birth Certificate, or Passport formats).
* **Identity Classes:**
  1. Adults: Standard National ID string (e.g., `1988102938475`) mapping to structural parameters (Name, DOB, Parent Fields).
  2. Minors: Standard Birth Certificate string (e.g., `2012582910294`) requiring mandatory explicit parent NID connection arrays for authorization.
  3. Foreign Nationals: Passport Number string format (e.g., `EB-007`) mapping to nationality, marital parameters, and tracking metadata.
* **Lifecycle Linkage:** When a child transitions to adulthood, system routing must link the historical Birth Certificate identifier tightly to their newly registered NID.

### Feature 6: AI-Driven Document OCR & Digital Nursing
* **OCR Ingestion:** Processing pipeline scanning unstructured legacy reports (PDF/Images) to normalize medical text.
* **Pattern Recognition:** Core medical logic identifying diagnostic history and trends.
* **AI Nurse Agent:** Patient-facing personal healthcare routine builder, running automated prescription alarms and medication scheduling alerts.

---

## 3. Data Infrastructure & Storage Schemas

Generate and save the system databases as structured CSV datasets directly under the following path layout: `/CHCS/Files/Datasets/`

### A. Folder: `Citizen's Profiles`
* **File:** `birth_certificates.csv`
  * *Columns:* `BC num`, `name`, `date of birth`, `father NID`, `mother NID`, `birth location (hospital name)`
* **File:** `nids.csv`
  * *Columns:* `NID num`, `names`, `DoB`, `contact number`, `Birth certificate num (not mandatory)`
* **File:** `foreigners_passports.csv`
  * *Columns:* `Passport num`, `nationality`, `DoB`, `if married then spouse name`, `spouse nid/passport name`

### B. Folder: `Doctor's profiles`
* **File:** `doctors_list.csv`
  * *Columns:* `Doctor ID`, `Name`, `BMDC License`, `Specialty`, `Assigned Hospital ID`

### C. Folder: `Hospital's profiles`
* **File:** `hospitals_list.csv`
  * *Columns:* `Hospital ID`, `Name`, `License Num`, `Category`, `Geo Location (Lat,Lon)`, `Daily Patient Serve Count`, `Free Medicine Stock Summary`

### D. Folder: `medicine dispensary shops`
* **File:** `dispensaries_list.csv`
  * *Columns:* `Dispensary ID`, `Name`, `License Num`, `Location`, `Medicine Stock Record`

### E. Folder: `patient's profiles's`
* **Data Privacy Rule (Data Siloing & Zero-Knowledge Routing):**
  * Store separate clinical medical histories in individualized files using the uniform identity number as the filename (e.g., `/CHCS/Files/Datasets/patient's profiles's/2012582910294.txt`).
  * **Role-Based Access Control (RBAC):**
    * *Doctors/Patients/Parents (for minors):* Full access to complete clinical history, prescriptions, diagnoses, and chronological medical summary summaries.
    * *Dispensaries:* Inputting a citizen's profile identifier grants zero insight into underlying diseases or diagnostic summaries. The pharmacy node must only extract the **medicine genre/specific name** and dosage schema linked to active prescriptions (`pres no.`).

---

## 4. Technical Architecture & Vercel Deployment Strategy

* **High-Concurrency Target:** Architect the service layer to process millions of concurrent data handshakes via Vercel Edge Networks and optimized connection pooling.
* **Document Deliverables:** Generate a detailed system architecture report outlining database layouts, backend deployment mechanics, user manuals, and placeholder mappings referencing assets in the `/CHCS/img/` folder.
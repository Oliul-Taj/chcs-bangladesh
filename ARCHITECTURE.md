# CHCS Bangladesh — System Architecture & Deployment Report

> **Version:** 1.0 | **Classification:** Internal Technical Document | **Scope:** National Rollout

---

## 1. System Overview

The **Centralized Healthcare Communication System (CHCS)** is a multi-portal, API-first web application providing Bangladesh's Ministry of Health, hospitals, doctors, pharmacies, and citizens a unified, real-time medical records and surveillance platform.

**Target Scale:** 170M+ citizens | 64 districts | 500+ public hospitals | Millions of concurrent requests

---

## 2. Database Layout

### Active SQLite Schema (`nchds.db`) — Local/Dev
| Table | Purpose |
|---|---|
| `nid_registry` | National Identity, BC, and Passport verification source |
| `patients` | Enrolled patient profiles linked to NHID |
| `doctors` | BMDC-licensed practitioners |
| `hospitals` | Facility metadata, grades, geolocation |
| `encounters` | Clinical visit records |
| `prescriptions` | Active medication orders |
| `disease_reports` | Outbreak symptom submissions |
| `outbreaks` | Aggregated epidemic cluster records |
| `malpractice_reports` | Patient complaint filings |
| `scanned_records` | OCR-extracted legacy documents |

### Production Target (Vercel + PlanetScale/Supabase PostgreSQL)
- Replace SQLite with PostgreSQL via connection pooling (PgBouncer)
- Read replicas per geographic node (Dhaka, Chittagong, Rajshahi, Sylhet)
- Write master in Dhaka datacenter; edge cache via Vercel KV (Redis)

---

## 3. Dataset File Structure

```
/CHCS/Files/Datasets/
├── Citizen's Profiles/
│   ├── birth_certificates.csv     — Minor BC registry
│   ├── nids.csv                   — Adult NID registry
│   └── foreigners_passports.csv   — Foreign national passports
├── Doctor's profiles/
│   └── doctors_list.csv           — BMDC-licensed practitioners
├── Hospital's profiles/
│   └── hospitals_list.csv         — Facility geo + grading data
├── medicine dispensary shops/
│   └── dispensaries_list.csv      — Pharmacy POS terminals
└── patient's profiles/
    ├── 1988102938475.txt           — Mir Oliul Pasha Taj (Full clinical)
    ├── 1995827392819.txt           — Sarah Jenkins (Full clinical)
    └── 2012582910294.txt           — Tasnim Ara (Minor, parent-gated)
```

> **RBAC Data Silo Rule:** Pharmacy nodes call `/api/pharmacy_prescriptions` — returns ONLY medicine name, brand, dosage, and quantity. Zero diagnosis, complaint, or clinical history is transmitted.

---

## 4. Identity Resolution Engine

The system accepts **any identity format** without forcing users to type prefixes:

| Input Example | Resolved Type | Action |
|---|---|---|
| `1988102938475` | NID (adult, born 1988) | Lookup in `nid_registry` as `NID-1988102938475` |
| `2012582910294` | Birth Certificate (born 2012, minor) | Lookup as `BC-2012582910294`, enforce parent NID |
| `EB-007` | Foreign Passport | Lookup in foreigners table |
| `NID-1988102938475` | Already prefixed NID | Direct lookup |
| `nid 1988102938475` | Case-insensitive + space | Normalized, then lookup |

---

## 5. Backend Deployment — Vercel Architecture

```
[ Browser / Mobile ]
        │
        ▼
[ Vercel Edge Network (CDN) ] ←── Static assets: /CHCS/static/, /CHCS/img/
        │
        ▼
[ Vercel Serverless Function ]  ←── /api/index.py (Flask WSGI via gunicorn)
        │
        ├──► /api/nid_verify          — Identity lookup
        ├──► /api/search_patient      — Full clinical profile (Doctor/Patient RBAC)
        ├──► /api/pharmacy_prescriptions — Medicine-only view (Pharmacy RBAC)
        ├──► /api/stats               — Ministry dashboard aggregate
        ├──► /api/outbreaks_geo       — GeoJSON outbreak markers
        ├──► /api/register_patient    — Enroll citizen
        ├──► /api/add_encounter       — Log clinical visit
        ├──► /api/hospital_grade      — Grade calculation
        └──► /api/scan_report         — OCR document ingestion
        │
        ▼
[ PostgreSQL (PlanetScale / Supabase) ] ←── Production database
[ Vercel KV (Redis) ]                   ←── Session cache, rate limiting
```

---

## 6. Portal Map

| Portal | URL Route | Users |
|---|---|---|
| Patient / Citizen | `/patient` | Citizens, patients |
| Hospital Admin | `/hospital` | Hospital clerks, admins |
| Doctor Clinical | `/doctor` | Physicians, specialists |
| Pharmacy POS | `/pharmacy` | Dispensary staff |
| Ministry Dashboard | `/ministry` | MoH officials, auditors |

---

## 7. Image Asset Placeholders (`/CHCS/img/`)

| Filename | Used In | Description |
|---|---|---|
| `img/logo.png` | All portals navbar | CHCS national branding logo |
| `img/bd_map_overlay.png` | Ministry epidemic map | Bangladesh district heat map overlay |
| `img/hospital_grade_chart.png` | Hospital grading docs | Grade tier infographic |
| `img/patient_timeline.png` | Patient portal docs | Longitudinal record timeline |
| `img/ai_nurse_icon.png` | Patient portal | Personal Nurse AI avatar |
| `img/ocr_pipeline.png` | Architecture docs | OCR ingestion pipeline diagram |

> Assets should be placed at the listed paths before production deployment.

---

## 8. Vercel Deployment Steps

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. From CHCS root directory
cd /home/oliul-taj/Downloads/CHCS

# 3. Initialize and deploy
vercel --prod

# 4. Set environment secrets
vercel env add DATABASE_URL   # PostgreSQL connection string
vercel env add SECRET_KEY     # Flask secret key

# 5. Verify deployment
vercel inspect --logs
```

---

## 9. Concurrency & Scalability Notes

- **Vercel Edge Functions** automatically scale to zero/cold-start model — no idle cost
- **Connection Pooling:** Use `psycopg2` + PgBouncer to handle 10,000+ concurrent DB connections
- **Rate Limiting:** Implement per-NID rate limits via Vercel KV (10 requests/minute per identity)
- **Static GeoJSON:** `static/bangladesh.geojson` served via CDN edge — zero compute cost
- **SQLite → PostgreSQL Migration:** Run `python3 migrate_to_pg.py` (to be generated in Phase 2)

---

*Report generated: 2026-06-27 | CHCS Bangladesh Technical Team*

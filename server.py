from flask import Flask, render_template, jsonify, request, g
import sqlite3
import os
import uuid
import datetime
import re

app = Flask(__name__)
DATABASE = 'nchds.db'

def resolve_identity(raw):
    """
    Intelligently classify and normalize any identity string.
    Returns (normalized_key, identity_type) where type is
    'nid', 'bc', 'passport', or 'nhid'.
    Strips all prefixes (NID-, BC-, PASS-, NHID-) case-insensitively.
    """
    s = raw.strip().upper()
    # Already prefixed NHID
    if re.match(r'^NHID[-\s]', s):
        return s.replace(' ', '-'), 'nhid'
    # Strip common prefixes
    clean = re.sub(r'^(NID[-\s]?|BC[-\s]?|BIRTH[-\s]?CERT[-\s]?|PASS[-\s]?NO[-\s]?|PASSPORT[-\s]?)', '', s).strip().replace(' ', '')
    # Passport format: letters + dash + digits, e.g. EB-007
    if re.match(r'^[A-Z]{1,3}-\d{3,}$', clean):
        return clean, 'passport'
    # Numeric only
    if re.match(r'^\d+$', clean):
        if len(clean) == 13:
            id_type = 'bc' if int(clean[:4]) >= 2006 else 'nid'
            return clean, id_type
        if len(clean) < 13:
            return clean, 'bc'
    return s, 'unknown'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    # Force rebuild database to update schema with new tables
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # 1. Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                nhid TEXT UNIQUE,
                nid TEXT UNIQUE,
                name TEXT,
                dob TEXT,
                gender TEXT,
                district TEXT,
                parent_nid TEXT
            )
        ''')
        
        # 2. Hospitals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospitals (
                id TEXT PRIMARY KEY,
                name TEXT,
                reg_num TEXT UNIQUE,
                rating TEXT,
                registered_date TEXT,
                years_in_grade INTEGER DEFAULT 0
            )
        ''')
        
        # 3. Doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id TEXT PRIMARY KEY,
                name TEXT,
                bmdc_num TEXT UNIQUE,
                specialization TEXT,
                hospital_id TEXT,
                FOREIGN KEY(hospital_id) REFERENCES hospitals(id)
            )
        ''')
        
        # 4. Encounters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encounters (
                id TEXT PRIMARY KEY,
                patient_id TEXT,
                hospital_id TEXT,
                doctor_id TEXT,
                timestamp TEXT,
                chief_complaint TEXT,
                diagnosis TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id),
                FOREIGN KEY(hospital_id) REFERENCES hospitals(id),
                FOREIGN KEY(doctor_id) REFERENCES doctors(id)
            )
        ''')
        
        # 5. Prescriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions (
                id TEXT PRIMARY KEY,
                encounter_id TEXT,
                patient_id TEXT,
                generic_name TEXT,
                brand_name TEXT,
                dosage TEXT,
                quantity INTEGER,
                dispensed INTEGER DEFAULT 0,
                pharmacy_id TEXT,
                FOREIGN KEY(encounter_id) REFERENCES encounters(id),
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
        ''')
        
        # 6. Pharmacies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pharmacies (
                id TEXT PRIMARY KEY,
                name TEXT,
                bin_tin TEXT UNIQUE,
                district TEXT
            )
        ''')

        # 7. NID Registry table (Simulated Govt database)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nid_registry (
                nid_passport TEXT PRIMARY KEY,
                name TEXT,
                dob TEXT,
                gender TEXT,
                father_name TEXT,
                mother_name TEXT,
                district TEXT
            )
        ''')

        # 8. Hospital Audits & Grading parameters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospital_audits (
                hospital_id TEXT PRIMARY KEY,
                patient_count_yearly INTEGER DEFAULT 0,
                satisfaction_score REAL DEFAULT 0.0,
                cure_rate REAL DEFAULT 0.0,
                equipment_score REAL DEFAULT 0.0,
                expert_doctor_count INTEGER DEFAULT 0,
                cleanliness_score REAL DEFAULT 0.0,
                food_score REAL DEFAULT 0.0,
                architecture_score REAL DEFAULT 0.0,
                FOREIGN KEY(hospital_id) REFERENCES hospitals(id)
            )
        ''')

        # 9. Malpractice & Feedback reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS malpractice_reports (
                id TEXT PRIMARY KEY,
                patient_id TEXT,
                hospital_id TEXT,
                doctor_id TEXT,
                incident_summary TEXT,
                rating INTEGER,
                timestamp TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id),
                FOREIGN KEY(hospital_id) REFERENCES hospitals(id),
                FOREIGN KEY(doctor_id) REFERENCES doctors(id)
            )
        ''')

        # 10. Epidemic Outbreak Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS epidemic_outbreaks (
                id TEXT PRIMARY KEY,
                hospital_id TEXT,
                doctor_id TEXT,
                disease TEXT,
                symptoms TEXT,
                district TEXT,
                lat REAL,
                lng REAL,
                timestamp TEXT,
                FOREIGN KEY(hospital_id) REFERENCES hospitals(id),
                FOREIGN KEY(doctor_id) REFERENCES doctors(id)
            )
        ''')

        # 11. Scanned Reports table (Mock OCR storage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scanned_records (
                id TEXT PRIMARY KEY,
                patient_id TEXT,
                filename TEXT,
                extracted_data TEXT,
                timestamp TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
        ''')

        # Seed Mock Data
        # Seed NID Registry
        nid_data = [
            ("NID-1995827392819", "Sarah Jenkins", "1995-04-12", "Female", "Robert Jenkins", "Mary Jenkins", "Mymensingh"),
            ("NID-1990472839401", "Michael Chen", "1990-09-25", "Male", "William Chen", "Linda Chen", "Rajshahi"),
            ("NID-2005482938492", "Abir Hasan", "2005-11-03", "Male", "Mahmudul Hasan", "Salma Begum", "Dhaka"),
            ("NID-1988102938475", "Mir Oliul Pasha Taj", "1988-06-15", "Male", "Mir Golam Pasha", "Laila Arjumand", "Rajshahi"),
            ("NID-1993472839102", "Jannatul Ferdous", "1993-01-20", "Female", "Abdul Khaleque", "Amena Begum", "Chittagong"),
            ("NID-2001582930192", "Sadia Islam", "2001-08-14", "Female", "Rafiqul Islam", "Nasrin Akter", "Khulna"),
            ("NID-1997482910293", "Naimur Rahman", "1997-03-30", "Male", "Mizanur Rahman", "Sultana Razia", "Sylhet"),
            ("NID-1992837461524", "Farhana Yasmin", "1992-12-05", "Female", "Fazlur Rahman", "Rokeya Begum", "Barisal"),
            ("NID-2008472910293", "Rashedul Islam", "2008-05-18", "Male", "Nurul Islam", "Monowara Begum", "Rangpur"),
            ("NID-2012582910294", "Tasnim Ara (Minor)", "2012-07-22", "Female", "Abul Kalam", "Ferdousi Begum", "Dhaka")
        ]
        cursor.executemany("INSERT OR IGNORE INTO nid_registry VALUES (?, ?, ?, ?, ?, ?, ?)", nid_data)

        # Seed Hospitals
        hospitals_data = [
            ("h1", "Mymensingh Medical College Hospital", "REG-MMCH-1002", "A+", "2020-01-10", 3),
            ("h2", "Rajshahi Medical College Hospital", "REG-RMCH-1005", "A", "2021-04-15", 2),
            ("h3", "Dhaka Medical College Hospital", "REG-DMCH-1001", "A+", "2018-09-01", 5),
            ("h4", "Warning Clinic Mymensingh", "REG-WCM-8291", "Z", "2025-06-01", 1),
            ("h5", "New Hope Health Clinic", "REG-NHHC-9920", "N", "2026-02-14", 0)
        ]
        cursor.executemany("INSERT OR IGNORE INTO hospitals VALUES (?, ?, ?, ?, ?, ?)", hospitals_data)

        # Seed Hospital Audits
        audits_data = [
            ("h1", 125000, 4.8, 92.5, 4.7, 120, 4.6, 4.4, 4.8),
            ("h2", 95000, 4.3, 85.0, 4.2, 85, 4.1, 4.0, 4.2),
            ("h3", 240000, 4.9, 95.0, 4.9, 210, 4.8, 4.6, 4.9),
            ("h4", 15000, 1.8, 45.0, 2.0, 4, 1.5, 1.2, 2.1),
            ("h5", 2000, 4.0, 75.0, 3.8, 8, 4.2, 4.0, 4.0)
        ]
        cursor.executemany("INSERT OR IGNORE INTO hospital_audits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", audits_data)

        # Seed Patients (Linked to NIDs)
        patients_data = [
            ("p1", "NHID-3849-1029-4820-2", "NID-1995827392819", "Sarah Jenkins", "1995-04-12", "Female", "Mymensingh", None),
            ("p2", "NHID-5928-3019-5820-9", "NID-1990472839401", "Michael Chen", "1990-09-25", "Male", "Rajshahi", None),
            ("p3", "NHID-8291-4920-5821-6", "NID-2005482938492", "Abir Hasan", "2005-11-03", "Male", "Dhaka", None),
            ("p4", "NHID-1029-3847-5820-1", "NID-1988102938475", "Mir Oliul Pasha Taj", "1988-06-15", "Male", "Rajshahi", None),
            ("p5", "NHID-4728-3910-2839-4", "NID-1993472839102", "Jannatul Ferdous", "1993-01-20", "Female", "Chittagong", None),
            ("p6", "NHID-5829-3019-2839-2", "NID-2001582930192", "Sadia Islam", "2001-08-14", "Female", "Khulna", None),
            ("p7", "NHID-4829-1029-3849-5", "NID-1997482910293", "Naimur Rahman", "1997-03-30", "Male", "Sylhet", None),
            ("p8", "NHID-2837-4615-2483-3", "NID-1992837461524", "Farhana Yasmin", "1992-12-05", "Female", "Barisal", None),
            ("p9", "NHID-4729-1029-3847-7", "NID-2008472910293", "Rashedul Islam", "2008-05-18", "Male", "Rangpur", None),
            ("p10", "NHID-5829-1029-4839-8", "NID-2012582910294", "Tasnim Ara (Minor)", "2012-07-22", "Female", "Dhaka", "NID-2005482938492")
        ]
        cursor.executemany("INSERT OR IGNORE INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?)", patients_data)
        
        # Seed Doctors
        doctors_data = [
            ("d1", "Dr. Sarah Jenkins", "BMDC-Cardio-8392", "Cardiologist", "h1"),
            ("d2", "Dr. Asif Rahman", "BMDC-Neuro-4729", "Neurologist", "h2"),
            ("d3", "Dr. Tasnim Ara", "BMDC-Pedia-1029", "Pediatrician", "h3")
        ]
        cursor.executemany("INSERT OR IGNORE INTO doctors VALUES (?, ?, ?, ?, ?)", doctors_data)
        
        # Seed Pharmacies
        pharmacies_data = [
            ("ph1", "Lazz Pharma Rajshahi", "BIN-10029384-TIN-839201", "Rajshahi"),
            ("ph2", "Model Pharmacy Mymensingh", "BIN-49201920-TIN-102938", "Mymensingh")
        ]
        cursor.executemany("INSERT OR IGNORE INTO pharmacies VALUES (?, ?, ?, ?)", pharmacies_data)
        
        # Seed Encounters
        encounters_data = [
            ("e1", "p2", "h1", "d1", "2026-05-10 10:30:00", "Chest tightness and palpitations", "Essential Hypertension"),
            ("e2", "p1", "h2", "d2", "2026-06-01 14:15:00", "Chronic migraine and visual aura", "Migraine with Aura"),
            ("e3", "p3", "h3", "d3", "2026-06-15 09:00:00", "Shortness of breath and wheezing", "Mild Asthma"),
            ("e4", "p4", "h2", "d2", "2026-05-20 11:30:00", "Recurrent throbbing headaches", "Migraine with Aura"),
            ("e5", "p4", "h1", "d1", "2026-06-18 10:15:00", "Elevated blood pressure measurements", "Essential Hypertension"),
            ("e6", "p5", "h3", "d3", "2026-06-20 14:30:00", "Sneezing and runny nose", "Allergic Rhinitis"),
            ("e7", "p6", "h1", "d1", "2026-06-22 16:00:00", "Increased thirst and frequent urination", "Type 2 Diabetes"),
            ("e8", "p7", "h2", "d2", "2026-06-23 09:45:00", "Persistent dry cough and fever", "Acute Bronchitis"),
            ("e9", "p8", "h3", "d3", "2026-06-24 11:00:00", "Nausea, vomiting and diarrhea", "Gastroenteritis"),
            ("e10", "p9", "h1", "d1", "2026-06-25 08:30:00", "High fever and body aches", "Viral Fever"),
            ("e11", "p10", "h3", "d3", "2026-06-26 13:00:00", "Sore throat and difficulty swallowing", "Tonsillitis")
        ]
        cursor.executemany("INSERT OR IGNORE INTO encounters VALUES (?, ?, ?, ?, ?, ?, ?)", encounters_data)
        
        # Seed Prescriptions
        prescriptions_data = [
            ("pr1", "e1", "p2", "Amlodipine", "Norvasc", "5mg - 1 daily", 30, 0, None),
            ("pr2", "e1", "p2", "Atorvastatin", "Lipitor", "10mg - 1 at night", 30, 0, None),
            ("pr3", "e2", "p1", "Sumatriptan", "Imitrex", "50mg - as needed", 6, 6, "ph1"),
            ("pr4", "e3", "p3", "Albuterol", "Ventolin", "90mcg inhaler - 2 puffs as needed", 1, 1, "ph2"),
            ("pr5", "e4", "p4", "Sumatriptan", "Imitrex", "50mg - as needed", 6, 6, "ph1"),
            ("pr6", "e5", "p4", "Amlodipine", "Norvasc", "5mg - 1 daily", 30, 30, "ph2"),
            ("pr7", "e7", "p6", "Metformin", "Glucophage", "500mg - 2 daily", 60, 60, "ph2"),
            ("pr8", "e8", "p7", "Azithromycin", "Zithromax", "500mg - 1 daily", 5, 5, "ph1"),
            ("pr9", "e9", "p8", "Ondansetron", "Zofran", "4mg - as needed", 10, 10, "ph2"),
            ("pr10", "e10", "p9", "Paracetamol", "Napa", "500mg - 3 daily", 15, 15, "ph2"),
            ("pr11", "e11", "p10", "Amoxicillin", "Moxacil", "250mg - 3 daily", 21, 21, "ph1")
        ]
        cursor.executemany("INSERT OR IGNORE INTO prescriptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", prescriptions_data)

        # Seed Outbreaks
        outbreaks_data = [
            ("o1", "h1", "d1", "Dengue Fever", "High fever, joint pain, rash", "Mymensingh", 24.7570, 90.4073, "2026-06-25 09:30:00"),
            ("o2", "h1", "d1", "Dengue Fever", "High fever, platelet drop", "Mymensingh", 24.7585, 90.4101, "2026-06-25 11:20:00"),
            ("o3", "h1", "d3", "Dengue Fever", "Severe headache, eye pain", "Mymensingh", 24.7610, 90.4012, "2026-06-26 14:05:00"),
            ("o4", "h2", "d2", "Cholera", "Watery diarrhea, vomiting", "Rajshahi", 24.3745, 88.6042, "2026-06-26 10:10:00")
        ]
        cursor.executemany("INSERT OR IGNORE INTO epidemic_outbreaks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", outbreaks_data)
        
        db.commit()
        print("Database initialized with updated CHCS Schema.")

# Initialize the db
init_db()

# --- WEB ROUTES ---
@app.route('/')
def route_landing():
    return render_template('landing.html')

@app.route('/ministry')
def route_ministry():
    return render_template('ministry.html')

@app.route('/hospital')
def route_hospital():
    return render_template('hospital.html')

@app.route('/doctor')
def route_doctor():
    return render_template('doctor.html')

@app.route('/patient')
def route_patient():
    return render_template('patient.html')

@app.route('/pharmacy')
def route_pharmacy():
    return render_template('pharmacy.html')

# --- API ENDPOINTS ---
@app.route('/api/stats')
def api_stats():
    db = get_db()
    cursor = db.cursor()
    
    total_patients = cursor.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    total_doctors = cursor.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    total_hospitals = cursor.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
    total_encounters = cursor.execute("SELECT COUNT(*) FROM encounters").fetchone()[0]
    total_prescriptions = cursor.execute("SELECT COUNT(*) FROM prescriptions").fetchone()[0]
    
    # Live outbreaks aggregation (AI disease similarity / geographic cluster logic)
    raw_outbreaks = cursor.execute("SELECT disease, district, COUNT(*) as count FROM epidemic_outbreaks GROUP BY disease, district").fetchall()
    disease_mapping = []
    for row in raw_outbreaks:
        disease_mapping.append({
            "disease": row["disease"],
            "district": row["district"],
            "count": row["count"]
        })
        
    # Medicine consumption projections
    medicine_consumption = [
        {"generic": "Metformin", "current_month": 45000, "projected_next": 48000},
        {"generic": "Atorvastatin", "current_month": 32000, "projected_next": 34000},
        {"generic": "Paracetamol", "current_month": 120000, "projected_next": 150000},
        {"generic": "Amlodipine", "current_month": 28000, "projected_next": 30000}
    ]
    
    return jsonify({
        "summary": {
            "patients": total_patients,
            "doctors": total_doctors,
            "hospitals": total_hospitals,
            "encounters": total_encounters,
            "prescriptions": total_prescriptions,
            "live_births_today": 345,
            "live_deaths_today": 89
        },
        "diseases": disease_mapping,
        "medicines": medicine_consumption
    })

@app.route('/api/nid_verify')
def api_nid_verify():
    raw = request.args.get('nid', '')
    clean, id_type = resolve_identity(raw)
    db = get_db()
    cursor = db.cursor()
    # Try exact match first, then with NID- prefix, then bare number
    candidates = [clean, f'NID-{clean}', f'BC-{clean}', f'PASS-{clean}']
    row = None
    for candidate in candidates:
        row = cursor.execute("SELECT * FROM nid_registry WHERE UPPER(nid_passport) = ?", (candidate,)).fetchone()
        if row:
            break
    if row:
        return jsonify({"success": True, "record": dict(row), "identity_type": id_type})
    return jsonify({"success": False, "message": "NID/Passport details not found in NID database."})

@app.route('/api/register_patient', methods=['POST'])
def api_register_patient():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    p_id = str(uuid.uuid4())
    nhid = "NHID-" + str(uuid.uuid4().int)[:15]
    # Check parent NID if minor (under 18)
    # DOB format: YYYY-MM-DD
    try:
        dob_year = int(data['dob'].split('-')[0])
        current_year = datetime.datetime.now().year
        age = current_year - dob_year
        parent_nid = data.get('parent_nid')
        if parent_nid:
            parent_nid = parent_nid.strip().upper()
            
        if age < 18 and not parent_nid:
            return jsonify({"success": False, "message": "Child account registration requires a mandatory parent NID."})
            
        cursor.execute('''
            INSERT INTO patients (id, nhid, nid, name, dob, gender, district, parent_nid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p_id, nhid, data['nid'].strip().upper(), data['name'], data['dob'], data['gender'], data['district'], parent_nid))
        db.commit()
        return jsonify({"success": True, "nhid": nhid})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/search_patient')
def api_search_patient():
    raw = request.args.get('query', '')
    clean, id_type = resolve_identity(raw)
    db = get_db()
    cursor = db.cursor()

    # Build candidate lookups: bare number, NID- prefixed, BC- prefixed, name search
    candidates_exact = [clean, f'NID-{clean}', f'BC-{clean}', f'NHID-{clean}']
    patient = None
    for c in candidates_exact:
        patient = cursor.execute(
            "SELECT * FROM patients WHERE UPPER(nhid) = ? OR UPPER(nid) = ?",
            (c, c)
        ).fetchone()
        if patient:
            break
    # Fallback: name LIKE search
    if not patient:
        patient = cursor.execute(
            "SELECT * FROM patients WHERE UPPER(name) LIKE ?",
            (f"%{clean}%",)
        ).fetchone()

    if patient:
        p_dict = dict(patient)
        encounters = cursor.execute('''
            SELECT e.*, d.name as doctor_name, h.name as hospital_name, h.rating as hospital_rating 
            FROM encounters e
            JOIN doctors d ON e.doctor_id = d.id
            JOIN hospitals h ON e.hospital_id = h.id
            WHERE e.patient_id = ?
            ORDER BY e.timestamp DESC
        ''', (p_dict['id'],)).fetchall()
        p_dict['history'] = [dict(enc) for enc in encounters]

        prescriptions = cursor.execute(
            "SELECT * FROM prescriptions WHERE patient_id = ?",
            (p_dict['id'],)
        ).fetchall()
        p_dict['prescriptions'] = [dict(pr) for pr in prescriptions]

        return jsonify({"success": True, "patient": p_dict})
    return jsonify({"success": False, "message": "Patient not found"})

@app.route('/api/pharmacy_prescriptions')
def api_pharmacy_prescriptions():
    """
    RBAC Pharmacy-Safe Endpoint.
    Returns ONLY medicine names, dosages, and prescription IDs.
    Zero clinical data (diagnosis, complaints, history) is exposed.
    """
    raw = request.args.get('query', '')
    clean, id_type = resolve_identity(raw)
    db = get_db()
    cursor = db.cursor()

    candidates = [clean, f'NID-{clean}', f'BC-{clean}']
    patient = None
    for c in candidates:
        patient = cursor.execute(
            "SELECT id, name, nhid FROM patients WHERE UPPER(nhid) = ? OR UPPER(nid) = ?",
            (c, c)
        ).fetchone()
        if patient:
            break

    if not patient:
        return jsonify({"success": False, "message": "Patient not found"})

    prescriptions = cursor.execute('''
        SELECT id, generic_name, brand_name, dosage, quantity, dispensed
        FROM prescriptions WHERE patient_id = ?
    ''', (patient['id'],)).fetchall()

    return jsonify({
        "success": True,
        "patient_name": patient['name'],
        "nhid": patient['nhid'],
        "prescriptions": [dict(p) for p in prescriptions]
    })



@app.route('/api/add_encounter', methods=['POST'])
def api_add_encounter():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    encounter_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute('''
            INSERT INTO encounters (id, patient_id, hospital_id, doctor_id, timestamp, chief_complaint, diagnosis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (encounter_id, data['patient_id'], data['hospital_id'], data['doctor_id'], timestamp, data['chief_complaint'], data['diagnosis']))
        
        if 'prescriptions' in data:
            for pr in data['prescriptions']:
                pr_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO prescriptions (id, encounter_id, patient_id, generic_name, brand_name, dosage, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (pr_id, encounter_id, data['patient_id'], pr['generic_name'], pr['brand_name'], pr['dosage'], int(pr['quantity'])))
                
        db.commit()
        return jsonify({"success": True, "encounter_id": encounter_id})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/report_outbreak', methods=['POST'])
def api_report_outbreak():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    outbreak_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Assign mock coordinates based on district to support mapping
    district_coords = {
        "Mymensingh": (24.7570, 90.4073),
        "Rajshahi": (24.3745, 88.6042),
        "Dhaka": (23.8103, 90.4125),
        "Chittagong": (22.3569, 91.7832),
        "Khulna": (22.8456, 89.5403)
    }
    district = data.get('district', 'Dhaka')
    base_coords = district_coords.get(district, (23.8103, 90.4125))
    
    # Add minor noise to disperse locations visually in map clusters
    import random
    lat = base_coords[0] + random.uniform(-0.015, 0.015)
    lng = base_coords[1] + random.uniform(-0.015, 0.015)
    
    try:
        cursor.execute('''
            INSERT INTO epidemic_outbreaks (id, hospital_id, doctor_id, disease, symptoms, district, lat, lng, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (outbreak_id, data.get('hospital_id', 'h1'), data.get('doctor_id', 'd1'), data['disease'], data['symptoms'], district, lat, lng, timestamp))
        db.commit()
        return jsonify({"success": True, "outbreak_id": outbreak_id})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/outbreaks_geo')
def api_outbreaks_geo():
    db = get_db()
    cursor = db.cursor()
    outbreaks = cursor.execute("SELECT * FROM epidemic_outbreaks").fetchall()
    return jsonify([dict(o) for o in outbreaks])

@app.route('/api/hospital_grade')
def api_hospital_grade():
    h_id = request.args.get('hospital_id', '')
    db = get_db()
    cursor = db.cursor()
    
    h_details = cursor.execute("SELECT * FROM hospitals WHERE id = ?", (h_id,)).fetchone()
    h_audits = cursor.execute("SELECT * FROM hospital_audits WHERE hospital_id = ?", (h_id,)).fetchone()
    
    if h_details and h_audits:
        return jsonify({
            "success": True,
            "details": dict(h_details),
            "audits": dict(h_audits)
        })
    return jsonify({"success": False, "message": "Hospital audit profile not found."})

@app.route('/api/submit_audit', methods=['POST'])
def api_submit_audit():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    h_id = data['hospital_id']
    try:
        # Calculate grade dynamically based on average scores
        # scores range from 1 to 5.
        avg_score = (data['cleanliness_score'] + data['food_score'] + data['architecture_score'] + data['satisfaction_score'] + data['equipment_score']) / 5.0
        
        # Grading bounds
        if avg_score >= 4.5:
            new_rating = "A+"
        elif avg_score >= 3.8:
            new_rating = "A"
        elif avg_score >= 2.8:
            new_rating = "B"
        elif avg_score >= 1.5:
            new_rating = "N"
        else:
            new_rating = "Z"
            
        # Update hospital details
        cursor.execute('''
            UPDATE hospitals SET rating = ? WHERE id = ?
        ''', (new_rating, h_id))
        
        # Update hospital audits table
        cursor.execute('''
            UPDATE hospital_audits 
            SET patient_count_yearly = ?, satisfaction_score = ?, cure_rate = ?, equipment_score = ?, expert_doctor_count = ?, cleanliness_score = ?, food_score = ?, architecture_score = ?
            WHERE hospital_id = ?
        ''', (data['patient_count_yearly'], data['satisfaction_score'], data['cure_rate'], data['equipment_score'], data['expert_doctor_count'], data['cleanliness_score'], data['food_score'], data['architecture_score'], h_id))
        
        db.commit()
        return jsonify({"success": True, "new_rating": new_rating})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/submit_malpractice', methods=['POST'])
def api_submit_malpractice():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    rep_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute('''
            INSERT INTO malpractice_reports (id, patient_id, hospital_id, doctor_id, incident_summary, rating, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rep_id, data['patient_id'], data['hospital_id'], data.get('doctor_id'), data['incident_summary'], int(data['rating']), timestamp))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/malpractice_list')
def api_malpractice_list():
    db = get_db()
    cursor = db.cursor()
    
    reports = cursor.execute('''
        SELECT r.*, p.name as patient_name, h.name as hospital_name, d.name as doctor_name
        FROM malpractice_reports r
        JOIN patients p ON r.patient_id = p.id
        JOIN hospitals h ON r.hospital_id = h.id
        LEFT JOIN doctors d ON r.doctor_id = d.id
        ORDER BY r.timestamp DESC
    ''').fetchall()
    
    return jsonify([dict(r) for r in reports])

@app.route('/api/scan_report', methods=['POST'])
def api_scan_report():
    # Mock OCR report scanner
    data = request.json
    filename = data.get('filename', 'report.pdf')
    patient_id = data.get('patient_id')
    
    # Check for keywords in mock text
    content = data.get('content', '').lower()
    
    extracted = {
        "diagnosis": "Unspecified Condition",
        "medications": []
    }
    
    if "cholera" in content:
        extracted["diagnosis"] = "Cholera Outbreak Strain"
        extracted["medications"] = ["Oral Rehydration Salts (ORS)", "Azithromycin 500mg"]
    elif "diabetes" in content or "metformin" in content:
        extracted["diagnosis"] = "Diabetes Mellitus Type 2"
        extracted["medications"] = ["Metformin 850mg", "Empagliflozin 10mg"]
    elif "dengue" in content:
        extracted["diagnosis"] = "Dengue Fever"
        extracted["medications"] = ["Paracetamol 500mg"]
    else:
        extracted["diagnosis"] = "Chronic Gastrointestinal Irritation"
        extracted["medications"] = ["Omeprazole 20mg"]
        
    db = get_db()
    cursor = db.cursor()
    rec_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    import json
    ext_json = json.dumps(extracted)
    
    try:
        cursor.execute('''
            INSERT INTO scanned_records (id, patient_id, filename, extracted_data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (rec_id, patient_id, filename, ext_json, timestamp))
        db.commit()
        return jsonify({"success": True, "extracted": extracted})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/dispense_prescription', methods=['POST'])
def api_dispense_prescription():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            UPDATE prescriptions
            SET dispensed = quantity, pharmacy_id = ?
            WHERE id = ?
        ''', (data['pharmacy_id'], data['prescription_id']))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

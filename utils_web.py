import re,json
import difflib
from curd_web import saveStooldata,saveUrinedata,saveCBCdata
#,saveLipidProfileData,saveGlucoseData

def getpatientInfo(ocr_text):

        data = {}
        data['Registration Id'] = re.search(r'Registration Id\s*:\s*(\d+)', ocr_text)
        data['Registration Date/Time'] = re.search(r'Registration Date/Time\s*:\s*([0-9/:\sAPMapm]+)', ocr_text)
        data['Patient Name'] = re.search(r'Patient Name\s*;?\s*([A-Za-z\s\.]+)\s+\d+', ocr_text)
        data['Collection Date/Time'] = re.search(r'Collection Date/Time\s*:\s*([0-9/:\sAPMapm]+)', ocr_text)
        data['Reporting Date/Time'] = re.search(r'Reporting Date/Time\s*:\s*([0-9/:\sAPMapm]+)', ocr_text)
        data['Referred By'] = re.search(r'Referred By\s*;?\s*(.*)', ocr_text)
        data['Age/Sex'] = re.search(r'Age\s*/Sex\s*:\s*([0-9]+.*?)\s*$', ocr_text, re.MULTILINE)
        return data


def extract_urine_routine_data(ocr_text,report_name,output_save_path,empId,report_date):
    #data = {}

    # Extract patient metadata
   
    #data['report name']=report_name   
    data=getpatientInfo(ocr_text)

    # Clean up metadata
    for key in data:
        match = data[key]
        data[key] = match.group(1).strip() if match else ""

    # Extract urine test values
    test_results = {}

    test_patterns = [
    ("Quantity", r'Quantity\s*[:>]*\s*([0-9a-zA-Z.]+)'),
    ("Colour", r'Colour\s*[:‘]?\s*([A-Z ]+)'),
    ("Appearance", r'Appearance\s*[:=]?\s*([A-Z ]+)'),
    ("Deposit", r'Deposit\s*[:>]*\s*([A-Z ]+)'),
    ("pH", r'pH\s*[:=]*\s*[=:]*\s*([0-9.]+)'),
    ("Specific Gravity", r'Specific\s+Gravity\s*[=:.\s]*([0-9.]+)'),
    ("Albumin", r'Albumin\s*[:>]*\s*(\w+)'),
    ("Sugar", r'Sugar\s*[:>]*\s*(\w+)'),
    ("Ketone Bodies", r'Ketone Bodies\s*[:>]*\s*(\w+)'),
    ("Nitrite", r'Nitrite\s*[:>]*\s*(\w+)'),
    ("Blood", r'Blood\s*[:>]*\s*(\w+)'),
    ("Bile Pigments", r'Bile Pigments\s*[:>]*\s*(\w+)'),
    ("Bile Salts", r'Bile Salts\s*[:>]*\s*(\w+)'),
    ("Urobilinogen", r'Urobilinogen\s*[:>]*\s*(\w+)'),
   ("Epithelial Cells", r'Epithelial Cells\s*[:=]*\s*([A-Za-z0-9\-\/]+)[\s]*([a-zA-Z0-9\-\/ ]+)?'),
    ("Pus Cells", r'Pus Cells.*?:\s*([A-Za-z0-9\-\/]+)[\s]*([0-9\- ]+ cells/hpf)?'),
    ("Red Blood Cells", r'(?:Red\s*)?Blood Cells\s*[:=]*\s*([A-Za-z]+)[\s]*([0-9\- ]+ cells/hpf)?'),
    ("Casts", r'Casts\s*[:=]*\s*([A-Z]+)'),
    ("Crystals", r'Crystals\s*[:=>]*\s*([A-Z]+)'),
    ("Amorphous Materials", r'Amorphous Materials\s*[:=]*\s*([A-Z]+)'),
    ("Bacteria", r'Bacteria\s*[:=]*\s*([A-Z]+)'),
    ("Yeast Cells", r'Yeast Cells\s*[:=]*\s*([A-Z]+)'),
    ("Mucus", r'Mucus\s*[:=]*\s*([A-Za-z]+)')
]


    for test_name, pattern in test_patterns:
        match = re.search(pattern, ocr_text)
        test_results[test_name] = match.group(1).strip() if match else ""

    # Combine all
    output = {
        "reportName": report_name,
        "PatientInfo": data,
        "UrineTestResults": test_results
    }
    saveUrinedata(report_name,data,test_results,output_save_path,empId,report_date)
    #return json.dumps(output, indent=4)  
    return None

def extract_stool_routine_data(ocr_text,report_name,output_save_path,empId,report_date):  
    
    data = {}
    
    # Basic Info
    
    data['Registration Id'] = re.search(r'Registration Id\s*:\s*(\d+)', ocr_text)
    data['Registration Date/Time'] = re.search(r'Registration Date/Time\s*[:\-]*\s*([\d/:\sAPMapm\.]+)', ocr_text)
    data['Patient Name'] = re.search(r'Patient Name\s*[\+;:]?\s*(Mr\.?\s*[A-Za-z\s]+)\s+\d+', ocr_text)
    data['Collection Date/Time'] = re.search(r'Collection Date/Time\s*[—:\-]*\s*([\d/:\sAPMapm\.]+)', ocr_text)
    data['Reporting Date/Time'] = re.search(r'Reporting Date/Time\s*[:\-]*\s*([\d/:\sAPMapm\.]+)', ocr_text)
    data['Referred By'] = re.search(r'Referred By\s*[=:;\-]*\s*(.*)', ocr_text, re.IGNORECASE)
    data['Age/Sex'] = re.search(r'Age\s*/Sex\s*[:\-]*\s*(\d+\s+Years\s*/\s*\w+)', ocr_text)

    # Clean basic fields
    for key, match in data.items():
        data[key] = match.group(1).strip() if match else ""

    # Initialize test result dictionary
    test_results = {}

    # Fields to look for
    expected_fields = [
        "Colour", "Consistency", "Reaction", "Blood", "Mucus", "Parasites",
        "Occult Blood", "Reducing Substances", "Red Blood Cells", "Epithelial Cells",
        "Pus Cells", "Fungal Organisms", "Vegetable Fibres", "Muscle Fibres",
        "Fat Globules", "Starch Granules", "Vegetative forms", "Cystic forms",
        "Larvae", "Ova"
    ]

    # Clean OCR lines
    lines = ocr_text.splitlines()
    test_results = {}

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        # Try to split at :, >, =, or ’ (curly apostrophe)
        match = re.split(r"[:>=’]", clean_line, maxsplit=1)
        if len(match) != 2:
            continue
        raw_field, value = match[0].strip(), match[1].strip()

        # Use fuzzy match to find the closest expected field name
        closest = difflib.get_close_matches(raw_field, expected_fields, n=1, cutoff=0.8)
        if closest:
            field_name = closest[0]
            test_results[field_name] = value

    # Fill missing fields
    for field in expected_fields:
        if field not in test_results:
            test_results[field] = ""

    # Combine all
    output = {
        "reportName": report_name,
        "PatientInfo": data,
        "stoolTestResults": test_results
    }
    saveStooldata(report_name,data,test_results,output_save_path,empId,report_date)
    #return json.dumps(output, indent=4) 
    return None
def extract_CBC_data(ocr_text,report_name,output_save_path,empId,report_date):
     saveCBCdata(report_name,output_save_path,empId,report_date)
     #return json.dumps(output, indent=4) 
     return None

def extract_lipid_profile_data(ocr_text,report_name,output_pdf_path):  
    
    patient = {}

    # Name
    match = re.search(r'Name\s*:\s*(.*)', ocr_text, re.IGNORECASE)
    if match:
        patient['Patient Name'] = match.group(1).strip().split("Ref")[0].strip()

    # Age
    match = re.search(r'Age\s*:\s*([\d]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Age'] = match.group(1).strip()

    # Sex
    match = re.search(r'Sex\s*:\s*([A-Za-z]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Sex'] = match.group(1).strip()

    # Corporate
    match = re.search(r'Corporate\s*:\s*([A-Z ]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Corporate'] = match.group(1).strip()

    # Reference By
    match = re.search(r'Ref\.?\s*by\s*:\s*(.*)', ocr_text, re.IGNORECASE)
    if match:
        patient['Referred By'] = match.group(1).strip()

    # Report Date
    match = re.search(r'Date\s*([0-9/]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Collection Date/Time'] = match.group(1).strip() 

    expected_fields = [
        "triglycerides", "total_cholesterol", "hdl_cholesterol", "ldl_cholesterol", "vldl", "ldl_hdl_ratio",
        "tcl_hdl_ratio"
    ]

    lipid_data = {}

    # Total Cholesterol
    match = re.search(r'TOTAL CHOLESTR(?:ROL|OL).*?(\d+)\s*[#]?\s*\w+/?\w*\s*[\[\(]?([<>]?\d{2,3}(?:[-–]\d{2,3})?)?', ocr_text, re.IGNORECASE)
    if match:
        lipid_data["total_cholesterol"] = match.group(1)

    # Triglycerides
    match = re.search(r'TRIGLYCERIDES.*?(\d+)\s*[#]?\s*\w+/?\w*\s*[\[\(]?([<>]?\d{2,3}(?:[-–]\d{2,3})?)?', ocr_text, re.IGNORECASE)
    if match:
        lipid_data["triglycerides"] = match.group(1)

    # HDL
    match = re.search(r'HDL\s*[-]?\s*CHOLESTEROL.*?(\d+)\s*\w+/?\w*\s*[\[\(]?([<>]?\d{2,3}(?:[-–]\d{2,3})?)?', ocr_text, re.IGNORECASE)
    if match:
        lipid_data["hdl_cholesterol"] = match.group(1)

    # VLDL
    match = re.search(r'VLDL\s*[-]?\s*Cholester[a-z]*\s*\(?.*?\)?\s*.*?(\d+)\s*[#]?\s*\w+/?\w*\s*[\[\(]?(10[-–]40|\d{2,3})?', ocr_text, re.IGNORECASE)
    if match:
        lipid_data["vldl"] = match.group(1)

    # LDL
    match = re.search(r'LDL\s*[-]?\s*CHOLESTEROL.*?(\d{2,4})\s*[#]?\s*\w+/?\w*\s*[\[\(]?([<>]?\d{2,3}(?:[-–]\d{2,3})?)?', ocr_text, re.IGNORECASE)
    if match:
        lipid_data["ldl_cholesterol"] = match.group(1)

   
    lipid_data["report_name"]=report_name
    lipid_data["output_pdf_path"]=output_pdf_path
    output = {
    "Patient Info": patient,
    "Lipid Profile": lipid_data
    }        
    #saveLipidProfileData(patient,lipid,report_name,expected_fields)
    #return json.dumps(output, indent=4) 
    return lipid_data




    

def extract_glucose_data(ocr_text,report_name,output_pdf_path):  
    
    patient = {}

    # Name
    match = re.search(r'Name\s*:\s*(.*)', ocr_text, re.IGNORECASE)
    if match:
        patient['Patient Name'] = match.group(1).strip().split("Ref")[0].strip()

    # Age
    match = re.search(r'Age\s*:\s*([\d]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Age'] = match.group(1).strip()

    # Sex
    match = re.search(r'Sex\s*:\s*([A-Za-z]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Sex'] = match.group(1).strip()

    # Corporate
    match = re.search(r'Corporate\s*:\s*([A-Z ]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Corporate'] = match.group(1).strip()

    # Reference By
    match = re.search(r'Ref\.?\s*by\s*:\s*(.*)', ocr_text, re.IGNORECASE)
    if match:
        patient['Referred By'] = match.group(1).strip()

    # Report Date
    match = re.search(r'Report Date\s*([0-9/]+)', ocr_text, re.IGNORECASE)
    if match:
        patient['Collection Date/Time'] = match.group(1).strip() 

    expected_fields = [
        "fasting_blood_glucose", "post_prandial_blood_glucose", "urine_sugar_fasting", "urine_sugar_postprandial"
    ]

    glucose = {}

    fasting_match = re.search(r'GLUCOSE[-\s]?Fasting.*?(\d+)\s*mg/dl', ocr_text, re.IGNORECASE)
    if fasting_match:
         glucose["fasting_blood_glucose"]  = int(fasting_match.group(1))

    

    # Extract postprandial glucose
    pp_match = re.search(r'GLUCOSE\s*-\s*PP.*?(\d+)\s*mg/dl', ocr_text, re.IGNORECASE)
    if pp_match:
        glucose["post_prandial_blood_glucose"] = int(pp_match.group(1))
   

    # Extract urine sugar (assume order: fasting, post)
    urine_sugars = re.findall(r"Urine sugar\s+([A-Z]+)", ocr_text, re.IGNORECASE)
    if len(urine_sugars) >= 2:
        glucose["urine_sugar_fasting"] = urine_sugars[0].upper()
        glucose["urine_sugar_postprandial"] = urine_sugars[1].upper()
    glucose["output_pdf_path"]=output_pdf_path
    glucose["report_name"]=report_name
    output = {
    #"Patient Info": patient,
    "glucose Detail": glucose
    }  
    output2 = {
    #"Patient Info": patient,
    "glucose Detail": glucose
    }        
    #saveGlucoseData(patient,glucose,report_name,expected_fields)
    #return json.dumps(output, indent=4) 
    return glucose

def extract_thyroid_data(ocr_text,report_name,output_pdf_path):
    result = {}
    # Manually extract lines containing test data
    #pattern = re.compile(r'^(Total T3.*?|Total T4.*?|Ultrasensitive TSH.*?)[>:]\s*([><]?\s*\d+\.?\d*)')
    pattern = re.compile(
    r'^(Total T3.*?|Total T4.*?|Ultrasensitive TSH.*?)[>:]?\s*([><]?\s*\d+[,.]?\d*)',
    re.IGNORECASE)
    key_mapping = {
    "Total T3 (Tri-iodothyronine)": "total_T3_Tri_iodothyronine",
    "Total T4 (Thyroxine)": "total_T4_Thyroxine",
    "Ultrasensitive TSH,Serum": "ultrasensitive_TSH_serum"
    }
    for line in ocr_text.splitlines():
        match = pattern.search(line)
        if match:
            original_key = match.group(1).strip()
            simplified_key = key_mapping.get(original_key, original_key)
            value = match.group(2).strip()
            result[simplified_key] = value.replace(',','.')
    result["output_pdf_path"]=output_pdf_path
    result["report_name"]=report_name
    # Print final dictionary
    return result

def extract_liver_data(ocr_text,report_name,output_pdf_path):
    result={}
    ocr_text = ocr_text.replace(',', '.').replace('}', ')').replace(']', ')').replace('{', '(').replace('[', '(')

    # Pattern to match test name and value
    pattern = r'([\w\s/().*-]+?)\s+(\d+\.?\d*)\s*[\w/%]*\s*\(.*?\)'

    # Find all matches
    matches = re.findall(pattern, ocr_text)
    key_mapping = {
    "Serum\nBILIRUBIN-TOTAL (Diazo)**": "bilirubin_total",
    "BILIRUBIN - DIRECT (Diazo)": "bilirubin_direct",
    "BILIRUBIN - INDIRECT (Calculated)": "bilirubin_indirect",
    "SGOT/ AST (without PSP. TFCC)":"sgot_ast",
    "s SGPT/ ALT (without PSP. 1FCC)":"sgpt_alt",
    "nal ALP (p-NPP.AMP Buffer-IFCC)*":"alp",
    "TOTAL PROTEIN (mod. Biuret)":"total_protein",
    "SERUM ALBUMIN (BCG-dye)":"serum_albumin",
    "SERUM GLOBULIN (Calculated)":"serum_globulin",
    "ALB/GLOB (A/G) Ratio(Caleulated)":"alb_glob_ratio",
    "GGT (GCNA-Iece)":"ggt"




    }

    # Print only test name and value
    for test, value in matches:
        original_key = test.strip()
        simplified_key = key_mapping.get(original_key, original_key)
        value_p = value
        result[simplified_key] = value_p #.replace(',','.')
        #print(f"{test.strip()}: {value}")
    result["output_pdf_path"]=output_pdf_path
    result["report_name"]=report_name    
    return result  

def extract_Pulmonary_data(ocr_text,report_name,output_pdf_path):
    data = {}

# Existing fields...
    """sex_match = re.search(r'Sex at Birth\s+(Male|Female)', ocr_text, re.IGNORECASE)
    if sex_match:
        data['Sex'] = sex_match.group(1)

    height_match = re.search(r'Height\s+(\d+)\s*cm', ocr_text)
    if height_match:
        data['Height_cm'] = int(height_match.group(1))

    weight_match = re.search(r'Weight\s+(\d+)\s*kg', ocr_text)
    if weight_match:
        data['Weight_kg'] = int(weight_match.group(1))

    bmi_match = re.search(r'BMI\s+([\d.]+)', ocr_text)
    if bmi_match:
        data['BMI'] = float(bmi_match.group(1))

    ethnicity_match = re.search(r'Ethnicity\s+(\w+)', ocr_text)
    if ethnicity_match:
        data['Ethnicity'] = ethnicity_match.group(1)"""

    fev1_match = re.search(r'Predicted:\s*(\d+)%', ocr_text)
    if fev1_match:
        data['FEV1_predicted'] = int(fev1_match.group(1))

    lung_age_match = re.search(r'Lung Age:\s*(\d+)', ocr_text)
    if lung_age_match:
        data['lung_age'] = int(lung_age_match.group(1))

    """ test_date_match = re.search(r'Test Date\s*\(([\d-]+\s+[\d:]+)\)', ocr_text)
    if test_date_match:
        data['Test_DateTime'] = test_date_match.group(1)

    btps_match = re.search(r'BTPS\s+\(IN/EX\)\s+(\d+)/(\d+)', ocr_text)
    if btps_match:
        data['BTPS_IN'] = int(btps_match.group(1))
        data['BTPS_EX'] = int(btps_match.group(2))"""

    fvc_best_match = re.search(r'FVC\s*\[L\)\s*(\d+\.\d+)', ocr_text)
    if fvc_best_match:
        data['FVC_Best_L'] = float(fvc_best_match.group(1))

    # ✅ Extract FEV1 Best [L] — the largest float in a line starting with FEV1
    fev1_line_match = re.search(r'(FEV1|FEVY)[^\n]*', ocr_text)
    if fev1_line_match:
     fev1_line = fev1_line_match.group(0)
    # Extract all float numbers like 2.98, 2.88 etc.
    float_values = re.findall(r'\d+\.\d+', fev1_line)
    if float_values:
        float_values = [float(val) for val in float_values]
        data['FEV1_Best_L'] = max(float_values)
    data["output_pdf_path"]=output_pdf_path
    data["report_name"]=report_name    
    return data  

def extract_ESR_data(ocr_text,report_name,output_pdf_path):
    data = {}  
    pattern = re.compile(
    r"(BSR\s*\(Automated/Modified Westergren\))\s+([\d.]+)\s*#?\s*([^\[]+)\[([\d.oO\-]+)\]"
)

    match = pattern.search(ocr_text)
    if match:
        test_name = match.group(1).strip()
        value = match.group(2).strip()
        unit = match.group(3).strip()
        ref_range = match.group(4).replace('o', '0').replace('O', '0').strip()

        data['ESR']=value
    data["output_pdf_path"]=output_pdf_path
    data["report_name"]=report_name    
    return data   
def extract_audiogram_data (ocr_text,report_name,output_pdf_path):
   data= {}
   data["output_pdf_path"]=output_pdf_path
   data["report_name"]=report_name  
   return data
        
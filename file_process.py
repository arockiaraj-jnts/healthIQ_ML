import pytesseract
from pdf2image import convert_from_path
from PIL import Image,ImageFilter, ImageOps
import os,cv2
import numpy as np
import platform
from datetime import datetime
from curd_web import saveNonTrenddata
from utils_web import extract_glucose_data,extract_audiogram_data,extract_thyroid_data,extract_Pulmonary_data,extract_ESR_data,extract_lipid_profile_data,extract_urine_routine_data,extract_stool_routine_data,extract_CBC_data,extract_liver_data
def process_pdf(empId,report_date,pdf_path,output_folder):
    print(f" Processing PDF: {pdf_path}")
    #image_paths = convert_pdf_to_images(pdf_path,output_folder)
    image_paths = ['samples/glucose_ml.jpg','samples/thyroid.png','samples/lipid.jpg','samples/kidney_ml.jpg','samples/urineRoutine_ml.jpg','samples/cbc_ml.jpg',
                   'samples/liver_ml.jpg','samples/spirometery.jpg','samples/ESR.jpg','samples/hearing.jpg','samples/HIV.jpg','samples/dental.jpg','samples/physicalreport.jpg',
                   'samples/opthomology.jpg','samples/bloodgroup.jpg','samples/ecg.jpg']
    #image_paths =['samples/ecg.jpg']
    all_extract_data=[]
    for image_path in image_paths:
        #if image_path!='page_7.png':
         #   continue
        print(f"\n--- Processing {image_path} ---")
        image = Image.open(image_path).convert("RGB")
        output_path = datetime.now().strftime("%d%m%y%H%M%S")
        output_pdf_path = os.path.join(output_folder, f"{output_path}.pdf")
        output_save_path =  f"{output_path}.pdf"
        image = Image.open(image_path).convert("RGB")
        image.save(output_pdf_path, "PDF")        
        check_resolution(image_path)        
        #check_for_hand_drawn_lines(image_path)
        extract_data= extract_text_with_tesseract(image_path,output_save_path,empId,report_date)
        #os.remove(image_path)  # Cleanup after processing
        all_extract_data.append(extract_data)
    print("*********")  
    
    #print(all_extract_data) 
    return  all_extract_data  

# === Step 1: Convert PDF to Images ===
def convert_pdf_to_images(pdf_path, output_folder, dpi=300):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, img in enumerate(images):
        img_filename = f"page_{i+1}.jpg"
        img_path = os.path.join(output_folder, img_filename)
        #img.save(img_path, 'PNG')
        img.save(img_path, 'JPEG')
        image_paths.append(img_path)

    return image_paths

# === Step 2: Check Image Resolution ===
def check_resolution(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        print(f" Resolution: {width}x{height}")
        # Load and convert to grayscale
        gray = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)

        # Standard deviation of pixel intensities
        std_dev = gray.std()

        print(f"Standard Deviation: {std_dev}")

        if width < 1000 or height < 1000:
            return " Warning: Low resolution - OCR accuracy may suffer.",False
        else:
            return " Resolution is good for OCR.",True

# === Step 3: OCR with Tesseract ===
def extract_text_with_tesseract(image_path,output_save_path,empId,report_date):
    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # Preprocess
    #image = Image.open(image_path).convert("L")
    #image = image.resize((image.width // 2, image.height // 2))
    #image = image.filter(ImageFilter.MedianFilter()) 
    #image = cv2.imread("samples/glucose_ml.jpg")
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)  
    #text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
    print("\n OCR Result:")
    print(text.strip())
    report_name=get_report_name(text.strip()).replace('&','')
    print(report_name)
    report_handlers = {
    "ROUTINE URINE ANALYSIS": lambda: extract_urine_routine_data(text.strip(), report_name,output_save_path,empId,report_date),
    "KIDNEY PROPILE": lambda: extract_stool_routine_data(text.strip(), report_name,output_save_path,empId,report_date),
    "Lipid Profile": lambda: extract_lipid_profile_data(text.strip(), report_name,output_save_path),
    "GLUCOSE-Fasting": lambda: extract_glucose_data(text.strip(), report_name,output_save_path),
    "Thyroid Function Test": lambda: extract_thyroid_data(text.strip(), report_name,output_save_path),
    "Liver Function Test": lambda: extract_liver_data(text.strip(), report_name,output_save_path),
    "Complete Blood Count": lambda: extract_CBC_data(text.strip(), report_name,output_save_path,empId,report_date),
    "FVC (ex only)": lambda: extract_Pulmonary_data(text.strip(), "Pulmonary Function Test",output_save_path),
    "ERYTHROCYTE SEDIMENTATION": lambda: extract_ESR_data(text.strip(), report_name,output_save_path),
    'Pure Tone Audiogram': lambda: extract_audiogram_data(text.strip(), report_name,output_save_path),
    'Hepatitis B surface Antigen':lambda: saveNonTrenddata( report_name,output_save_path,empId,report_date),
    "DENTAL CHECK REPORT":lambda: saveNonTrenddata( report_name,output_save_path,empId,report_date),
    "PHYSICIAN REPORT":lambda: saveNonTrenddata( report_name,output_save_path,empId,report_date),
    "UCVA":lambda: saveNonTrenddata( "Opthalmology Report",output_save_path,empId,report_date),
    "Blood Group  Rh typing":lambda: saveNonTrenddata(report_name,output_save_path,empId,report_date),
    "12 Lead":lambda: saveNonTrenddata("ECG Report",output_save_path,empId,report_date),
    }

    json_output = report_handlers.get(report_name, lambda: {"error": "Unknown report"})()
    #json_output =None
    NoTrendReports=['Stool Routine','Urine Routine']
    
    print(json_output) 
    if report_name not in NoTrendReports:
        return json_output

def get_report_name(ocr_text):
    known_reports = [
        "Urine Routine", "Complete Blood Count", "CBC", "Liver Function Test",
        "Thyroid Profile", "Blood Sugar", "Lipid Profile", "KIDNEY PROPILE",
        "Urine Culture", "Stool Routine", "Hematology", "Blood Test", "GLUCOSE-Fasting",
        "ROUTINE URINE ANALYSIS","FVC (ex only)","ERYTHROCYTE SEDIMENTATION",'Pure Tone Audiogram',
        "Hepatitis B surface Antigen","Cardiology (ECG)","DENTAL CHECK REPORT","PHYSICIAN REPORT",
        "UCVA","Blood Group & Rh typing","12 Lead"
    ]
    #, "glucose fasting & postprandial"

    lines = ocr_text.splitlines()
    clean_lines = [line.strip().lower() for line in lines if line.strip()]  # normalize to lowercase

    # Step 1: Match against known report names
    for line in clean_lines[:40]:
        for report in known_reports:
            if report.lower() in line:
                return report  # return original casing from list

    # Step 2: Heuristic fallback — standalone lines with title case
    for line in lines:
        clean_line = line.strip()
        if (
            clean_line.istitle() and
            1 <= len(clean_line.split()) <= 4 and
            ':' not in clean_line and
            not any(word in clean_line.lower() for word in ['name', 'date', 'patient', 'age'])
        ):
            return clean_line

    return "Unknown Report"    
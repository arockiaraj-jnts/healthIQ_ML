import pytesseract
from PIL import Image, ImageEnhance, ImageOps

# Configure tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """
    Convert image to grayscale and increase contrast for better OCR accuracy.
    """
    img = Image.open(image_path)

    # Convert to grayscale
    img = ImageOps.grayscale(img)

    # Increase contrast (factor >1.0 = more contrast)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(5.0)  # 2.0 is a good start

    return img

def is_ecg_report(image_path):
    """
    Reads an image and determines if it's likely an ECG report.
    """
    try:
        # Preprocess image
        img = preprocess_image(image_path)

        # OCR to extract text
        extracted_text = pytesseract.image_to_string(img)

        # Normalize text for case-insensitive matching
        text_lower = extracted_text.lower()
        print (text_lower)
        # Keywords to identify ECG reports
        ecg_keywords = [
            "12 lead",
            "ecg",
            "qrs",
            "qt",
            "pr interval",
            "ventricular rate",
            "atrial rate",
            "p axis",
            "t axis"
        ]

        # Check if any keyword exists in the text
        found_keywords = [kw for kw in ecg_keywords if kw in text_lower]

        if found_keywords:
            print(f"✅ This is likely an ECG report. Found keywords: {found_keywords}")
            return True
        else:
            print("❌ This does not appear to be an ECG report.")
            return False

    except Exception as e:
        print(f"Error processing image: {e}")
        return False

# Example usage:
image_file = "samples/ecg.jpg"  # Replace with your image path
is_ecg_report(image_file)
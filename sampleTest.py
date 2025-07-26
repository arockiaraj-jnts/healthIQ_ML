import cv2
import pytesseract
from PIL import Image
import numpy as np

# Load image
image = cv2.imread("samples/glucose_ml.jpg")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply threshold to enhance text
thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Optional: Denoising (if needed)
# thresh = cv2.medianBlur(thresh, 3)

# OCR
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(thresh, config=custom_config)

print(text)

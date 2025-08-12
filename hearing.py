import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
import re

# Load full image (1115x1650)
image = cv2.imread("samples/hearing.jpg")

# Resize (optional, improves OCR)
image = cv2.resize(image, None, fx=1.2, fy=1.2)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# === 1️⃣ CROP AUDIOGRAM TABLE AREA ===
# Coordinates: y from 850 to 1250, x from 130 to 1000
cropped = gray[850:1250, 130:1200]

# Show cropped region
plt.imshow(cropped, cmap="gray")
plt.title("Cropped Audiogram Table")
plt.axis("off")
plt.show()

# === 2️⃣ OCR ===
# Thresholding
thresh = cv2.adaptiveThreshold(
    cropped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 31, 2
)
# Invert threshold for finding digits (white on black)
inverted = cv2.bitwise_not(thresh)

# Find contours
contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours by left to right
contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

valid_values = []

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if h > 10 and w > 5:  # filter small noise
        roi = thresh[y:y+h, x:x+w]
        digit = pytesseract.image_to_string(roi, config='--psm 10 -c tessedit_char_whitelist=0123456789')
        digit = re.sub(r'[^\d]', '', digit)
        if digit.isdigit():
            val = int(digit)
            if 0 <= val <= 120:
                valid_values.append(val)

print("🔍 Filtered dB Values from bounding boxes:", valid_values)

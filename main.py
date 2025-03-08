import os
from datetime import datetime
from tkinter import Tk, filedialog
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image, ImageDraw


def pdfToImage(pdf_path, output_folder, saveName):
    """Converts a PDF into images and saves them in the output folder."""
    images = convert_from_path(pdf_path)
    image_paths = []

    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"{saveName}_p{i + 1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

def imageComparison_overload(image1_path, image2_path, output_path):
    """Detects differences and marks them in two colors based on their value: green for > 0, blue for < 0."""
    image1 = Image.open(image1_path).convert("RGB")
    image2 = Image.open(image2_path).convert("RGB")

    if image1.size != image2.size:
        image2 = image2.resize(image1.size)

    # Create a new image to draw the highlights
    highlighted_image = image1.copy()
    highlighted_image = highlighted_image.convert("RGBA")  # Add an alpha channel

    width, height = image1.size

    for y in range(height):
        for x in range(width):
            # Get the RGB values of both images at the current pixel position
            r1, g1, b1 = image1.getpixel((x, y))
            r2, g2, b2 = image2.getpixel((x, y))

            # Compare the pixels by each color channel
            diff_r = r2 - r1
            diff_g = g2 - g1
            diff_b = b2 - b1

            # If the difference is positive, it means pdf2 has more content here, mark green
            if abs(diff_r) > 10 or abs(diff_g) > 10 or abs(diff_b) > 10:
                if diff_r > 0 or diff_g > 0 or diff_b > 0:
                    highlighted_image.putpixel((x, y), (255, 0, 0, 100))
                else:
                    highlighted_image.putpixel((x, y), (0, 128, 128, 100))

    # Save the resulting image
    highlighted_image.save(output_path)
    print(f"Saved highlighted image: {output_path}")

def imageComparison_boundingBox(image1_path, image2_path, output_path):
    """Detects differences and marks them with bounding boxes."""

    # Open images and convert to numpy arrays
    image1 = Image.open(image1_path).convert("RGB")
    image2 = Image.open(image2_path).convert("RGB")

    if image1.size != image2.size:
        image2 = image2.resize(image1.size)

    img1_np = np.array(image1)
    img2_np = np.array(image2)

    # Compute absolute difference
    diff = cv2.absdiff(img1_np, img2_np)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

    # Threshold to highlight changes
    _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours of the changed areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Convert back to PIL image
    highlighted_image = image1.copy()
    draw = ImageDraw.Draw(highlighted_image)

    # Draw bounding boxes around detected changes
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

    # Save output image
    highlighted_image.save(output_path)
    print(f"Saved highlighted image with bounding boxes: {output_path}")


def compare_pdfs(pdf1_path, pdf2_path, output_folder):
    """Compares two PDFs page by page and highlights differences in pdf1 with two colors."""
    os.makedirs(output_folder, exist_ok=True)

    images1 = pdfToImage(pdf1_path, output_folder, "pdf1")
    images2 = pdfToImage(pdf2_path, output_folder, "pdf2")

    if len(images1) != len(images2):
        print("Warning: PDFs have different page counts! Some pages may not be compared.")

    for i, (img1, img2) in enumerate(zip(images1, images2)):
        output_diff_path = os.path.join(output_folder, f"compareResult_p{i + 1}.png")
        imageComparison_boundingBox(img1, img2, output_diff_path)

    print("Comparison complete. Differences saved in:", output_folder)


# Open file dialog to select PDFs
def select_pdf(title):
    root = Tk()
    root.withdraw()  # Hide the Tkinter window
    file_path = filedialog.askopenfilename(title=title, filetypes=[("PDF Files", "*.pdf")])
    root.destroy()  # Close Tkinter properly
    return file_path


# Main execution
pdf1 = select_pdf("Select the previous document")
if not pdf1:
    print("No file selected. Exiting.")
    exit(1)

pdf2 = select_pdf("Select the current document")
if not pdf2:
    print("No file selected. Exiting.")
    exit(1)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outputFolder = os.path.join("result", timestamp)

compare_pdfs(pdf1, pdf2, outputFolder)

import os
import platform
import subprocess
from datetime import datetime
from tkinter import Tk, filedialog

import cv2
import numpy as np
from PIL import Image, ImageDraw
from pdf2image import convert_from_path
from tqdm import tqdm


def pdfToImage(pdfFilePath, saveFolderPath, saveName):
    imageList = convert_from_path(pdfFilePath)
    imagePathList = []
    for i, image in enumerate(imageList):
        imagePath = os.path.join(saveFolderPath, f"{saveName}_p{i + 1}.png")
        image.save(imagePath, "PNG")
        imagePathList.append(imagePath)
    return imagePathList


def imageComparison_overlay(image1Path, image2Path, saveFolderPath, pageIdx):
    image1 = Image.open(image1Path).convert("L")
    image2 = Image.open(image2Path).convert("L")
    if image1.size != image2.size:
        print("Warning: image1 and image2 have different sizes!")
        image2 = image2.resize(image1.size)

    image1 = np.array(image1, dtype=np.int16)
    image2 = np.array(image2, dtype=np.int16)
    diff = image2 - image1
    result = np.zeros((*image1.shape, 3), dtype=np.uint8)
    result[diff > 0, 0] = 255  # r
    result[diff < 0, 1] = 128  # g
    result[diff == 0] = np.dstack([image1[diff == 0].astype(np.uint8)] * 3)
    result = Image.fromarray(result)

    '''
    # slower
    width, height = image1.size
    result = Image.new("RGB", (width, height))
    progressBar = tqdm(total=width * height, desc="Processing pixels")
    for x in range(width):
        for y in range(height):
            l1 = int(image1.getpixel((x, y)))
            l2 = int(image2.getpixel((x, y)))
            dl = l2 - l1
            if dl > 0:
                result.putpixel((x, y), (255, 0, 0))
            elif dl < 0:
                result.putpixel((x, y), (0, 128, 0))
            else:
                result.putpixel((x, y), (l1, l1, l1))
            progressBar.update(1)
    progressBar.close()
    '''

    resultPath = os.path.join(saveFolderPath, f"result_p{pageIdx + 1}.png")
    result.save(resultPath)


def imageComparison_boundingBox(image1Path, image2Path, saveFolderPath, pageIdx):
    image1 = Image.open(image1Path).convert("L")
    image2 = Image.open(image2Path).convert("L")
    if image1.size != image2.size:
        print("Warning: image1 and image2 have different sizes!")
        image2 = image2.resize(image1.size)
    diff_raw = cv2.absdiff(np.array(image1), np.array(image2))
    _, diff_thresh = cv2.threshold(diff_raw, 0, 255, cv2.THRESH_BINARY)
    contourList, _ = cv2.findContours(diff_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result1, result2 = Image.open(image1Path).convert("RGB"), Image.open(image1Path).convert("RGB")
    draw1, draw2 = ImageDraw.Draw(result1), ImageDraw.Draw(result2)
    for contour in tqdm(contourList, desc="Processing contours"):
        x, y, w, h = cv2.boundingRect(contour)
        if w > 2 and h > 2:  # filter too small bounding boxes
            draw1.rectangle([x, y, x + w, y + h], outline="red", width=2)
            draw2.rectangle([x, y, x + w, y + h], outline="red", width=2)
    result1Path = os.path.join(saveFolderPath, f"result1_p{pageIdx + 1}.png")
    result2Path = os.path.join(saveFolderPath, f"result2_p{pageIdx + 1}.png")
    result1.save(result1Path)
    result2.save(result2Path)


def pdfComparison(pdf1FilePath, pdf2FilePath, saveFolderPath, compareMode="bounding box"):
    os.makedirs(saveFolderPath, exist_ok=False)
    imageList1 = pdfToImage(pdf1FilePath, saveFolderPath, "pdf1")
    imageList2 = pdfToImage(pdf2FilePath, saveFolderPath, "pdf2")
    if len(imageList1) != len(imageList2):
        print("Warning: PDFs have different page counts!")
    for i, (image1, image2) in enumerate(zip(imageList1, imageList2)):
        print(f"Processing page No.{i + 1}")
        if compareMode == "bounding box":
            imageComparison_boundingBox(image1, image2, saveFolderPath, i)
        elif compareMode == "overlay":
            imageComparison_overlay(image1, image2, saveFolderPath, i)
    print(f"Comparison ({compareMode}) result saved in: ", saveFolderPath)


def pdfSelect(title):
    root = Tk()
    root.withdraw()  # hide the Tkinter window
    filePath = filedialog.askopenfilename(title=title, filetypes=[("PDF Files", "*.pdf")])
    root.destroy()  # close Tkinter properly
    return filePath


def openFolder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux and others
        subprocess.run(["xdg-open", path])


if __name__ == "__main__":
    pdf1 = pdfSelect("Select pdf1")
    if not pdf1:
        print("No file selected. Exiting.")
        exit(1)
    pdf2 = pdfSelect("Select pdf2")
    if not pdf2:
        print("No file selected. Exiting.")
        exit(1)
    compareMode = input("Input comparison mode (bounding box / overlay): ").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    resultFolderPath = os.path.join("result", timestamp)
    if compareMode == "overlay":
        pdfComparison(pdf1, pdf2, resultFolderPath, compareMode)
    else:  # default is bounding box
        pdfComparison(pdf1, pdf2, resultFolderPath)
    openFolder(resultFolderPath)

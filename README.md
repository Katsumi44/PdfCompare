# Compare two PDF files

This code compares two PDF files and marks their differences, saving the comparison results in the `./result` folder (which will be created upon first use). 

## Installation

System requirements: Windows 10, Python 3.9.6

Install dependencies: `pip install -r requirements.txt`

## Usage

1.  Open and run [`main.py`](main.py).
2.  Select two PDF files consecutively in the pop-up windows.
3.  Enter comparison mode:
    - `bounding box` (default): mark the differing areas using red bounding boxes over the original PDF images.
    - `overlay`: overlay each group of images from the two PDFs into a single image; mark new content in pdf1 with red and in pdf2 with green.
4.  Check the results in the `./result` folder (which will be created upon first use and marked with the current timestamp). The folder will also open automatically after the process completes.

## Author

Yutong Zhang (email: 1150763693@qq.com)
"""
Generate OCR text for the MathVista images using EasyOCR.

Reference: https://github.com/JaidedAI/EasyOCR 
"""

# ! pip install easyocr

import os
import easyocr
import json
import tqdm

from mathvista.runtime import data_root, prepared_context

if __name__ == "__main__":

    image_dir = data_root()
    data_files = [image_dir / name for name in ("testmini.json", "test.json")]
    output_file = prepared_context() / "ocrs_easyocr.json"

    data = {}
    for data_file in data_files:
        with data_file.open(encoding='utf-8') as stream:
            data.update(json.load(stream))

    pids = list(data.keys())
    print("number of images: ", len(pids))

    reader = easyocr.Reader(['en']) # ocr reader

    results = {
        "model": "easyocr",
        "url": "https://github.com/JaidedAI/EasyOCR",
        "version": "1.1.8",
        "date": "2023-04-06",
        "texts": {}
    }
    for pid in tqdm.tqdm(pids):
        image_file = os.path.join(image_dir, data[pid]["image"])

        try:
            result = reader.readtext(image_file)
        except Exception as e:
            print(image_file, e)
            result = ""
        
        results["texts"][pid] = str(result)
        # print(result)
        # break

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
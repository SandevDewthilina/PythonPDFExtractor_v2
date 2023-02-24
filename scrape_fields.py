import requests
import os
from pdf2image import convert_from_path
from PIL import Image
from pytesseract import pytesseract

tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_text_of_area(body):
    url = body['file_url']
    file_name = body['file_name']
    upload_name = str(body['upload_name'])
    regex_components = body['regexComponents']

    upload_directory_path = os.path.join('upload_directory', upload_name)
    upload_file_path = os.path.join(upload_directory_path, file_name)
    pages_directory_path = os.path.join(upload_directory_path, 'pages')
    section_directory_path = os.path.join(upload_directory_path, 'sections')

    # create directory for the upload
    if not os.path.exists(upload_file_path):

        os.mkdir(upload_directory_path)
        os.mkdir(pages_directory_path)
        os.mkdir(section_directory_path)

        # download file from url
        response = requests.get(url)

        # write file
        try:
            # save the file in directory
            with open(upload_file_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(e)

    # save pages as jpg
    images = convert_from_path(upload_file_path)
    # images = convert_from_path(upload_file_path, size=(page_width, page_height))

    for i in range(len(images)):
        file = 'page' + str(i) + '.jpg'
        image_path = os.path.join(pages_directory_path, file)
        images[i].save(image_path, 'JPEG')

    # initialize pytesseract
    pytesseract.tesseract_cmd = tesseract_path
    results = []
    # cut and save each area
    for regex in regex_components:
        try:
            key = regex['Key']
            left, upper, right, lower, page_no = regex['Area'].split(',')[:5]
            left, upper, right, lower, page_no = int(left), int(upper), int(right), int(lower), int(page_no)

            jpg_path = os.path.join(pages_directory_path, f'page{page_no - 1}.jpg')
            section_path = os.path.join(section_directory_path, f'{key}.jpg')

            img = Image.open(jpg_path)
            # left, upper, right, lower
            box = (left, upper, right, lower)
            img2 = img.crop(box)
            img2.save(section_path)

            # extract text from each section
            extracted_text = pytesseract.image_to_string(img2, lang='eng')
            results.append({'key': key, 'text': extracted_text})
        except Exception as e:
            print(e)
    return results

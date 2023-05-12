import requests
import os
import io
from pdf2image import convert_from_path
from PIL import Image
from pytesseract import pytesseract
from google.cloud import vision
import cv2
import numpy as np

tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_boundary_and_save(img, image_path):
    # if i != 0:
    #   continue
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), cv2.BORDER_WRAP)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    box = []
    # Get the height and width of the image
    parent_height, parent_width, channels = img.shape

    my_contoure = []

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            rect = cv2.minAreaRect(approx)
            area = cv2.contourArea(approx)

            height = int(rect[1][1])
            width = int(rect[1][0])

            real_width = width
            real_height = height

            if height > width:
                real_width = height
                real_height = width

            if area > max_area and parent_width - 5 > real_width and parent_height - 5 > real_height:
                max_area = area
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                my_contoure = approx
    # cv2.drawContours(img, [box], -1, (0,0,255), 3)
    x, y, w, h = cv2.boundingRect(my_contoure)
    cropped_img = img[y:y + h, x:x + w]
    new_width = 3000
    new_height = int(h * (new_width / w))
    resized = cv2.resize(cropped_img, (new_width, new_height))
    cv2.imwrite(image_path, resized)


def get_text_of_area(body):
    url = body['file_url']
    file_name = body['file_name']
    upload_name = str(body['upload_name'])
    regex_components = body['regexComponents']

    client = vision.ImageAnnotatorClient()

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
        images[i].save(image_path)
        extract_boundary_and_save(images[i], image_path)

    # initialize pytesseract
    pytesseract.tesseract_cmd = tesseract_path

    output = []
    # cut and save each area
    for page_no in range(len(images)):
        results = []
        for regex in regex_components:
            try:
                key = regex['Key']
                isGoogleVision = regex['IsGoogleVision']
                left, upper, right, lower = regex['Area'].split(',')[:4]
                left, upper, right, lower = int(left), int(upper), int(right), int(lower)

                jpg_path = os.path.join(pages_directory_path, f'page{page_no}.jpg')
                section_path = os.path.join(section_directory_path, f'{key}.jpg')

                img = Image.open(jpg_path)
                # left, upper, right, lower
                box = (left, upper, right, lower)
                img2 = img.crop(box)
                img2.save(section_path)

                # extract text from each section
                if isGoogleVision:
                    img_byte_arr = io.BytesIO()
                    img2.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    image = vision.Image(content=img_byte_arr)

                    response = client.text_detection(image=image)
                    texts = response.text_annotations

                    text = texts[0]
                    # print('\n"{}"'.format(text.description))

                    # vertices = (['({},{})'.format(vertex.x, vertex.y)
                    #             for vertex in text.bounding_poly.vertices])

                    # print('bounds: {}'.format(','.join(vertices)))

                    if response.error.message:
                        raise Exception(
                            '{}\nFor more info on error messages, check: '
                            'https://cloud.google.com/apis/design/errors'.format(
                                response.error.message))

                    results.append({'key': key, 'text': text.description})
                else:
                    extracted_text = pytesseract.image_to_string(img2, lang='eng')
                    results.append({'key': key, 'text': extracted_text})
            except Exception as e:
                print(e)
        output.append(results)
        print(output)
    return output

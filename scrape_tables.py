import camelot
import os
import requests
import uuid
from flask import send_file, jsonify


def get_upload_directory_path(upload_name):
    return os.path.join('upload_directory', upload_name)


def get_pages_directory_path(upload_name):
    return os.path.join(get_upload_directory_path(upload_name), 'pages')


def get_section_directory_path(upload_name):
    return os.path.join(get_upload_directory_path(upload_name), 'sections')


def get_upload_file_path(upload_name, file_name):
    return os.path.join(get_upload_directory_path(upload_name), file_name)


def get_camelot_table(body):
    # pdf configs
    page_no = body['page_no']
    flavor = body['flavor']
    split_text = body['split_text']
    edge_tol = body['edge_tol']
    row_tol = body['row_tol']
    table_areas = body['table_areas']
    if table_areas == '':
        table_areas = None
    flag_size = body['flag_size']

    file_name = body['file_name']
    upload_name = str(body['upload_name'])
    url = body['file_url']

    upload_directory_path = get_upload_directory_path(upload_name)
    upload_file_path = get_upload_file_path(upload_name, file_name)
    section_directory_path = get_section_directory_path(upload_name)
    pages_directory_path = os.path.join(upload_directory_path, 'pages')

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

    return camelot.read_pdf(upload_file_path, flavor=flavor, split_text=split_text, edge_tol=edge_tol,
                            table_areas=[table_areas], row_tol=row_tol, backend="poppler", page=page_no,
                            flag_size=flag_size)


def get_table_detection(body):
    tables = get_camelot_table(body)
    return tables[0].df.to_dict(orient='records')


def get_detection_area(body):
    tables = get_camelot_table(body)

    temp_file_name = f'{str(uuid.uuid4())}.png'
    temp_file_path = os.path.join('temp_image_directory', temp_file_name)

    # create temp file
    camelot.plot(tables[0], kind='contour', filename=temp_file_path)

    return send_file(temp_file_path)

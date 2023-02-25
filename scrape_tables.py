import camelot
import os
import requests
import uuid
from flask import send_file
from threading import Timer


def get_upload_directory_path(upload_name):
    return os.path.join('upload_directory', upload_name)


def get_pages_directory_path(upload_name):
    return os.path.join(get_upload_directory_path(upload_name), 'pages')


def get_section_directory_path(upload_name):
    return os.path.join(get_upload_directory_path(upload_name), 'sections')


def get_upload_file_path(upload_name, file_name):
    return os.path.join(get_upload_directory_path(upload_name), file_name)


def remove_file(path):
    os.remove(path)


def get_camelot_table(body):
    # pdf configs
    page_no = body['page_no']
    flavor = body['flavor']
    split_text = body['split_text']
    edge_tol = body['edge_tol']
    row_tol = body['row_tol']
    table_areas = body['table_areas']
    flag_size = body['flag_size']
    columns = body['columns']
    if columns is None:
        columns = ''
    file_name = body['file_name']
    upload_name = str(body['upload_name'])
    url = body['file_url']

    upload_directory_path = get_upload_directory_path(upload_name)
    upload_file_path = get_upload_file_path(upload_name, file_name)
    section_directory_path = get_section_directory_path(upload_name)
    pages_directory_path = os.path.join(upload_directory_path, 'pages')

    # create directory for the upload
    if not os.path.exists(upload_file_path):

        try:
            if not os.path.exists(upload_directory_path):
                os.mkdir(upload_directory_path)
            if not os.path.exists(pages_directory_path):
                os.mkdir(pages_directory_path)
            if not os.path.exists(section_directory_path):
                os.mkdir(section_directory_path)
        except Exception as e:
            print(e)

        # download file from url
        response = requests.get(url)

        # write file
        try:
            # save the file in directory
            with open(upload_file_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(e)

    if flavor == 'stream':
        if not table_areas == '' and table_areas:
            return camelot.read_pdf(upload_file_path, flavor=flavor, split_text=split_text, edge_tol=edge_tol,
                                    table_areas=[table_areas], row_tol=row_tol, backend="poppler", pages=page_no,
                                    flag_size=flag_size, columns=[columns])
        else:
            return camelot.read_pdf(upload_file_path, flavor=flavor, split_text=split_text, edge_tol=edge_tol,
                                    row_tol=row_tol, backend="poppler", pages=page_no,
                                    flag_size=flag_size, columns=[columns])
    else:
        if not table_areas == '' and table_areas:
            return camelot.read_pdf(upload_file_path, flavor=flavor, split_text=split_text,
                                    table_areas=[table_areas], backend="poppler", pages=page_no,
                                    flag_size=flag_size, process_background=True)
        else:
            return camelot.read_pdf(upload_file_path, flavor=flavor, split_text=split_text,
                                    backend="poppler", pages=page_no,
                                    flag_size=flag_size, process_background=True)


def get_table_detection(body):
    tables = get_camelot_table(body)
    return tables[0].df.values.tolist()


def get_detection_area(body):
    tables = get_camelot_table(body)
    if len(tables) > 0:
        temp_file_name = f'{str(uuid.uuid4())}.png'
        temp_file_path = os.path.join('temp_image_directory', temp_file_name)

        # create temp file
        camelot.plot(tables[0], kind='contour', filename=temp_file_path)

        t = Timer(30.0, remove_file, args=[temp_file_path])
        t.start()
        return send_file(temp_file_path)
    else:
        return None

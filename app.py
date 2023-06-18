from flask import Flask, request, send_from_directory
from flask_cors import CORS
from scrape_fields import get_text_of_area
from scrape_tables import get_detection_area, get_table_detection
import os

app = Flask(__name__)
CORS(app)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'macho-389811-4308ddc9b7fc.json'


@app.route('/reports/<path:path>')
def send_report(path):
    return send_from_directory('upload_directory', path)


@app.route('/getTextOfArea', methods=['POST'])
def get_area_text():
    return get_text_of_area(request.json)


@app.route('/checkDetectionArea', methods=['POST'])
def get_detection_area_image():
    return get_detection_area(request.json)


@app.route('/detectTableOfArea', methods=['POST'])
def get_table_data():
    try:
        return get_table_detection(request.json)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True, port=9200)

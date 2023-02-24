from flask import Flask, request
from flask_cors import CORS
from scrape_fields import get_text_of_area
from scrape_tables import get_detection_area, get_table_detection

app = Flask(__name__)
CORS(app)


# @app.route('/')
# def index():
#     return render_template('index.html')

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
    app.run(debug=True, port=8200)

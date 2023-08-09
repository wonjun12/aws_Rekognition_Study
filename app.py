from flask import Flask
from flask_restful import Api

from resources.rekognition import DetectFacesResource, CompareFacesResource


app = Flask(__name__)
api = Api(app)

api.add_resource( DetectFacesResource , '/detectFaces')
api.add_resource( CompareFacesResource , '/compareFaces')

if __name__ == '__main__':
    app.run()
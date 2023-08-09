from flask_restful import Resource
from flask import request
from utils import createFileName, uploadS3, detect_face, compare_faces

class DetectFacesResource(Resource):
    def post(self):
        photo = request.files['photo']

        try:
            photo_name = createFileName()

            uploadS3(photo, photo_name)

            result = detect_face(photo_name)
            
            return {
                'result' : result
            }

        except Exception as e:
            return {
                'error' : str(e)
            }

        


class CompareFacesResource(Resource):
    def post(self):
        photo_source = request.files['photo_source']
        photo_target = request.files['photo_target']

        try:
            photo_source_name = createFileName()
            photo_target_name = createFileName()

            uploadS3(photo_source, photo_source_name)
            uploadS3(photo_target, photo_target_name)

            result = compare_faces(photo_source_name, photo_target_name)

            return {
                'result' : result
            }

        except Exception as e:
            return {
                'error' : str(e)
            }
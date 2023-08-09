from config import Config
import io

from datetime import datetime
import boto3
from PIL import Image, ImageDraw, ImageFont

def uploadS3(image, image_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
    )

    s3.upload_fileobj(
        image,
        Config.S3_BUCKET,
        image_name,
        ExtraArgs = {
                    'ACL' : 'public-read',
                    'ContentType' : 'image/jpeg'
                }
    )

def detect_face(photo, bucket = Config.S3_BUCKET):
    client = boto3.client(
        'rekognition',
        'us-east-1',
        aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
    )

    # 이미지 불럼오기
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image= Image.open(stream)


    response = client.detect_faces(
        Image = {
            'S3Object' : {
                'Bucket' : bucket,
                'Name' : photo
            }
        },
        Attributes = ['ALL']
    )

    # 이미지 경계선 그리기
    imgWidth, imgHeight = image.size  
    draw = ImageDraw.Draw(image)  

   
    for faceDetail in response['FaceDetails']:
        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)

        )

        draw.line(points, fill='#00d400', width=2)

    image.show()
    # 이미지 경계선 그리기 종료

    return response


def compare_faces(sourceFileName, targetFile):
    client = boto3.client(
        'rekognition',
        'us-east-1',
        aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
    )

    
    # imageSource=open(sourceFile,'rb')
    # imageTarget=open(targetFile,'rb')
    imageSource = s3Imageload(sourceFileName)

    targetFileSource = s3Imageload(targetFile)

    stream = io.BytesIO(targetFileSource)
    image= Image.open(stream)
    
    #imageSource = open(s3Imageload(sourceFileName), 'r')
    # imageTarget = s3Imageload(targetFileName)

    imgWidth, imgHeight = image.size  
    draw = ImageDraw.Draw(image) 
    fnt = ImageFont.truetype("NanumSquareB.ttf", 30, encoding="UTF-8")
    

    response=client.compare_faces(
        SimilarityThreshold=80,
        SourceImage={
            'Bytes': imageSource
            },
        TargetImage={
            'Bytes': targetFileSource
            })
    
    faceMath = {

    }
 
    for faceDetail in response['FaceMatches']:
        similarity = faceMath.get('Similarity')
        similStr = faceDetail['Similarity']

        if similarity is None or faceDetail['Similarity'] > similarity:
            faceMath['Similarity'] = similStr
            faceMath['BoundingBox'] = faceDetail['Face']['BoundingBox']
            
        silmilFormat = f"{int(similStr)}%"
        box = faceDetail['Face']['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        height = imgHeight * box['Height']
        draw.text((left , top + height), silmilFormat, font=fnt, fill="red")

    box = faceMath['BoundingBox']
    left = imgWidth * box['Left']
    top = imgHeight * box['Top']
    width = imgWidth * box['Width']
    height = imgHeight * box['Height']

    points = (
        (left,top),
        (left + width, top),
        (left + width, top + height),
        (left , top + height),
        (left, top)

    )
    draw.line(points, fill='#00d400', width=2)
    image.show()

    # imageSource.close()
    # imageTarget.close()

    return response

def s3Imageload(imageName, bucket = Config.S3_BUCKET):
    # # 이미지 불럼오기
    # # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, imageName)
    s3_response = s3_object.get()

    # stream = io.BytesIO(s3_response['Body'].read())
    # return Image.open(stream)
    # return s3_response['Body']
    return s3_response['Body'].read()


def createFileName():
    return datetime.now().isoformat().replace(':','_').replace('.', '_') + '.jpg'
    
from linebot import LineBotApi
import logging


#google-cloud設定
PROJECT_ID = 'face-swap-206808'
KIND='FaceSwap'

#LINE_BOT_API Channel
#LINE_BOT_API = LineBotApi('dlM9ES901PPug6JBOA7DANMgVnwnzitqoTcuzR8z8n3SKqzI3D8p9+wxw3Vz1EAYdJ/NrUmjak3fg+9WoRkj29InM56jaQe+3QAo3gB+L+kssItxKT8NTzI1u3UbQA3PhRy3PNsMT536uXTGRyMCiwdB04t89/1O/w1cDnyilFU=')
LINE_BOT_API = LineBotApi('dummyToken','http://localhost:8080')
LINE_CHANNEL_SECRET="b4b2cd344572197cfbc503aea94d2db9"

#FaceAPI設定
FACE_API_SUBSCRIPTION_KEY="9b386e76643345bf9a3de504121a17f7"
FACE_API_PERSON_GROUP = "kimono_search"
FACE_API_BASE_END_POINT = "https://japaneast.api.cognitive.microsoft.com/face/v1.0/"
FACE_API_PERSONGROUP_END_POINT = "persongroups/"
#FACE_API_PERSONGROUP_END_POINT = "largepersongroups/"

#FaceAPI 類似度の基準値
CONFIDENCE_THRESHOLD = 0.5

#FaceAPI 最大取得数
MAX_NUM_OF_CANDIATES_RETURNED = 10

#google-cloud設定
DATASET='face-swap-206808'
PROJECT_ID='face-swap-206808'
KIND = 'kimono_search'

IMG_BASE_URL = "https://storage.googleapis.com/kimono_search/"

#ごめんね画像
GOMENNE_IMAGE = "https://storage.googleapis.com/kimono_search/gomenne.jpg"

#Logging Level
LOGGING_LEVEL = logging.DEBUG
#LOGGING_LEVEL = logging.INFO


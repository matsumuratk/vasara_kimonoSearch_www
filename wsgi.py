import config

import requests
import json

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent,CarouselContainer,FlexContainer
)

from google.cloud import datastore

import os
import logging
import logging.handlers
#from logging.handlers import RoatatingFileHandler


#google-cloud設定
PROJECT_ID = config.PROJECT_ID
KIND = config.KIND

#PARAMATER
NOFACE = 'noface'

application = Flask(__name__)

# Add RotatingFileHandler to Flask Logger

application.logger.setLevel(config.LOGGING_LEVEL)
#debug_file_handler = RotatingFileHandler("debug.log", "a+", maxBytes=3000, backupCount=5)
#debug_file_handler.setLevel(logging.DEBUG) 
#debug_file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
#application.logger.addHandler(debug_file_handler)

line_bot_api = config.LINE_BOT_API
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

@application.route("/")
def hello_world():
    return "hello world!"

@application.route("/kimono_search", methods=['POST'])
def kimono_search():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    application.logger.debug("Request body: " + body)

    # handle webhook body
    try:
        reply_token = json.loads(body)["events"][0]["replyToken"]
        handler.handle(body, signature)
    except LineBotApiError as e:
        application.logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            application.logger.error("  %s: %s" % (m.property, m.message))
    except InvalidSignatureError as e:
        application.logger.error(e)
        application.logger.error("InvalidSignatureError")
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=e))
        abort(400)
    """
    except Exception as e:
        application.logger.error(e)
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=e))
        abort(400)
    """

    return 'OK'


@handler.add(MessageEvent, message=ImageMessage)
def handler_image_message(event):
    """
    * LINE ImageMessage event
    * FaceAPIで類似の顔写真を探して返す。
    * @params
    - messageId{String}: LINE message id
    - replyToken{String}: LINE replyToken
    """
    
    #FaceAPI detect でFaceIdを取得
    faceInfo = getDetectFaceInfo(event.message.id,event.reply_token)
    if (len(faceInfo) == 0):
        application.logger.info("写真に顔がないね")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="写真に顔がないね"))
        return

    faceId = faceInfo[0]['faceId']
    #age = faceInfo[0]['faceAttributes']['age']
    #gender = faceInfo[0]['faceAttributes']['gender']

    #FaceAPI identify で似た顔の写真を取得
    personIdAndConfidence = getPersonIdAndConfidence(faceId,event.reply_token)
    application.logger.debug("prtsonIdAndConfidence length=" + str(len(personIdAndConfidence[0]['candidates'])))
    if(len(personIdAndConfidence[0]['candidates']) == 0):
        application.logger.info("似た画像が見つからなかったよ")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="似た画像が見つからなかったよ"))
        return

    #flex calouselの作成

    application.logger.debug("make flex calousel:")

    carousel_contents = []

    #Flex Messageで取得した画像分ループ
    application.logger.debug("person_len=" + str(len(personIdAndConfidence[0]['candidates'])))
    for candidate in personIdAndConfidence[0]['candidates']:
        personId = candidate['personId']
        confidence = candidate['confidence']

        personInfo = getPersonInfomation(personId)

        #personInfo.name
        #personInfo.userData

        title = '一致度： ' +  str(confidence) 

        #carousel content作成
        bubble = BubbleContainer(
            hero = ImageComponent(
                size="full",
                aspectRatio="20:13",
                aspectMode="cover",
                url=config.IMG_BASE_URL + personInfo["name"]
            ),
            body=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    TextComponent(
                        text=personInfo["name"],
                        wrap=True,
                        weight="bold",
                        size="xl"
                    ),
                    BoxComponent(
                        layout="baseline",
                        contents=[
                            TextComponent(
                                text=title,
                                wrap=True,
                                weight="bold",
                                size="xl",
                                flex=0
                            )
                        ]   
                    )
                ]   
            ),
            footer=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    ButtonComponent(
                        style="primary",
                        action=URIAction(
                            label="VIEW IMAGE",
                            uri=config.IMG_BASE_URL + personInfo["name"]
                        )
                    )
                ]
            )
        )

        #作成したカルーセルコンテントを追加
        carousel_contents.append(bubble)



    #作成されたcarousel_contentsよりCarouselContainerを作成    
    container = CarouselContainer(contents=carousel_contents)
    message = FlexSendMessage(alt_text="hello", contents=container)

    application.logger.debug("return message:" )

    line_bot_api.reply_message(event.reply_token, message)
 

@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
    application.logger.info("画像じゃないよ。顔写真を送ってね")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="画像じゃないよ。顔写真を送ってね"))

@handler.add(MessageEvent, message=(StickerMessage,LocationMessage, VideoMessage, AudioMessage))
def handle_other_message(event):
    application.logger.info("画像じゃないよ。顔写真を送ってね")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="画像じゃないよ。顔写真を送ってね"))


#FaceAPI detect
def getDetectFaceInfo(messageId, replyToken):
    """
    * LINE message.Idから画像を取得し、FaceAPI より似た写真を返す
    * faceIdを取得します
    * @params
    - messageId{String}: LINE message id
    - replyToken{String}: LINE replyToken
    """
    application.logger.debug("call getDetectFaceInfo:")

    #LINEからファイルを取得
    message_content = line_bot_api.get_message_content(messageId)

    url = config.FACE_API_BASE_END_POINT + 'detect'
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': config.FACE_API_SUBSCRIPTION_KEY,
    }
    params ={
        'returnFaceId': 'true',  # The default value is true.
        'returnFaceLandmarks': 'false', # The default value is false.
        'returnFaceAttributes': 'age,gender', # age, gender, headPose, smile, facialHair, and glasses.
    }
    
    try:
        res = requests.post(url ,headers = headers,params = params,data = message_content.content)
        if res.status_code != 200:
            txt="この写真には顔がないよ。もう一度送ってね"
            application.logger.info(txt)
            line_bot_api.reply_message(
                replyToken,
                TextSendMessage(text=txt))
            abort(200)
        else:

            application.logger.debug("return getDetectFaceInfo: ")
            return res.json()

    except Exception as e:
        application.logger.error(e)
        line_bot_api.reply_message(
                replyToken,
                TextSendMessage(text=e))
        abort(200)

#FaceAPI identify
def getPersonIdAndConfidence(faceId,replyToken):
    """
    * faceIdから、personIdとconfidenceを取得します
    * @params
    - faceId{String}: 画像から検出されたfaceId
    - replyToken{String}: LINE replyToken
    * @return
    - personIdAndoConfidence{array}
     - personId
     - confidence
    """

    application.logger.debug("call getPersonAndConfidence: faceId=" + faceId)
    url = config.FACE_API_BASE_END_POINT + 'identify'
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': config.FACE_API_SUBSCRIPTION_KEY,
    }
    faceIds = [faceId]
    payload = {
        "PersonGroupId": config.FACE_API_PERSON_GROUP,
        "faceIds": faceIds,
        "maxNumOfCandidatesReturned": config.MAX_NUM_OF_CANDIATES_RETURNED,
        "confidenceThreshold": config.CONFIDENCE_THRESHOLD
    }

    try:
        res = requests.post(url ,json=payload,headers = headers)
        if res.status_code != 200:
            txt="似た写真はないね"
            application.logger.info(txt)
            line_bot_api.reply_message(
                replyToken,
                TextSendMessage(text=txt))
            abort(200)
        else:
            application.logger.debug("return getPersonAndConfidence:")
            return res.json()
    
    except Exception as e:
        application.logger.error(e)
        line_bot_api.reply_message(
            replyToken,
            TextSendMessage(text=e))
        abort(200)



def getPersonInfomation(personId):
    """
    * personIdからpersonInformationを取得
    * @ param
    *  - personId: Face APIで学習したpersonID
    * @return
     - name
     - userData

    """
    application.logger.debug("call getPersonInfo: personId=" + personId)
    url = config.FACE_API_BASE_END_POINT + config.FACE_API_PERSONGROUP_END_POINT + config.FACE_API_PERSON_GROUP + '/persons/' + personId

    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': config.FACE_API_SUBSCRIPTION_KEY,
    }

    try:
        res = requests.get(url, headers = headers)
        if res.status_code != 200:
            txt="status=" + str(res.status_code)
            application.logger.info(txt)
            line_bot_api.reply_message(
                replyToken,
                TextSendMessage(text=txt))
            abort(200)
        else:
            return res.json()
    
    except Exception as e:
        application.logger.error(e)
        line_bot_api.reply_message(
            replyToken,
            TextSendMessage(text=e))
        abort(200)


if __name__ == '__main__':                                                      
    application.run(debug=True)                                 

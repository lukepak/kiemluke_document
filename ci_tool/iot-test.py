import os
import json
import boto3
import logging
import requests
from subprocess import call

AIR_KEY = os.environ['AIR_KEY']
SLACK_ICM_WEBHOOK = os.environ['SLACK_ICM_WEBHOOK']

MSG = {
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Have a nice day* :sunglasses: \n\n*Cau Giay, Hanoi's weather:*"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ""
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ""
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ""
			}
		},
		{
			"type": "image",
			"alt_text": "marg",
			"image_url": ""
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Cau Giay, Hanoi's pollution:*"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ""
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ""
			}
		}
	]
}

TP = 'Temperature: {}°C'
HU ='Humidity: {}%'
WS = 'Wind speed: {} m/s'
IC = 'https://airvisual.com/images/{}.png'
AQIUS = 'AQI: {}'
AQIUS_LEVEl = 'AQI level: {}'

logger = logging.getLogger(__name__)

def lambda_handler(event, context):

    # TODO implement
    logger.info('Start')
    response = requests.get(f'http://api.airvisual.com/v2/city?city=Cau%20Giay&state=Hanoi&country=Vietnam&key={AIR_KEY}')
    
    try:
        res_json = response.json()
    except Exception as e:
        logger.error('Cann\'t convert response to json')
        return 1
    
    # print(json.dumps(res_json))
    
    # Sample data
    # res_json = {
    #     "status": "success",
    #     "data": {
    #         "city": "Cau Giay",
    #         "state": "Hanoi",
    #         "country": "Vietnam",
    #         "location": {
    #             "type": "Point",
    #             "coordinates": [
    #                 105.78276157,
    #                 21.03092148
    #             ]
    #         },
    #         "current": {
    #             "weather": {
    #                 "ts": "2020-11-04T06:00:00.000Z",
    #                 "tp": 24,
    #                 "pr": 1018,
    #                 "hu": 50,
    #                 "ws": 2.6,
    #                 "wd": 10,
    #                 "ic": "04d"
    #             },
    #             "pollution": {
    #                 "ts": "2020-11-04T05:00:00.000Z",
    #                 "aqius": 82,
    #                 "mainus": "p2",
    #                 "aqicn": 48,
    #                 "maincn": "p1"
    #             }
    #         }
    #     }
    # }
    
    # Check return success
    if res_json['status'] != 'success':
        logger.info('Response status: ', res_json.status)
        return 1
    
    # Weather
    # "tp": temperature in Celsius
    # "pr": atmospheric pressure in hPa
    # "hu": humidity %
    # "ws": wind speed (m/s)
    # "wd": wind direction, as an angle of 360° (N=0, E=90, S=180, W=270)
    # "ic": weather icon code, see below for icon index
    # 
    # Pollution
    # "aqius": AQI value based on US EPA standard
    # "mainus": main pollutant for US AQI
    # "aqicn": AQI value based on China MEP standard
    # "maincn": main pollutant for Chinese AQI
    
    if 'data' not in res_json or 'current' not in res_json['data']:
        logger.info('Data unavailable')
        return 1
    
    if 'weather' not in res_json['data']['current']:
        logger.info('Weather data unavailable')
        return 1
    
    if 'pollution' not in res_json['data']['current']:
        logger.info('Pollution data unavailable')
        return 1
    
    # Weather
    MSG['blocks'][2]['text']['text'] = TP.format(res_json['data']['current']['weather']['tp'])
    MSG['blocks'][3]['text']['text'] = HU.format(res_json['data']['current']['weather']['hu'])
    MSG['blocks'][4]['text']['text'] = WS.format(res_json['data']['current']['weather']['ws'])
    MSG['blocks'][5]['image_url'] = IC.format(res_json['data']['current']['weather']['ic'])
    
    # Pollution
    MSG['blocks'][8]['text']['text'] = AQIUS.format(res_json['data']['current']['pollution']['aqius'])
    MSG['blocks'][9]['text']['text'] = AQIUS_LEVEl.format(caculateAQILevel(res_json['data']['current']['pollution']['aqius']))
    
    # Send message to Slack
    # print(json.dumps(MSG))
    
    try:
        requests.post(
            SLACK_ICM_WEBHOOK,
            data=json.dumps(MSG),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        logger.error('Cann\'t send message to slack')
        return 1
    
    logger.info('Completed')
    return 0

def caculateAQILevel(value):
    '''Caculation of AQI level
    Keyword arguments:
    value -- AQI index get by API
    Returns: string
    '''
    
    if value <= 50:
        return 'Good'
    elif 50 < value and value <= 100:
        return 'Moderate'
    elif 100 < value and value <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif 150 < value and value <= 200:
        return 'Unhealthy'
    elif 200 < value and value <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'
    

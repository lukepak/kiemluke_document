import os
import json
import boto3
from threading import Thread
from datetime import datetime

REGION = 'ap-northeast-1'
SNS = "arn:aws:sns:ap-northeast-1:012881927014:CheckNetworkConnection"
UNAVAILABLE_NETS = []

#####
def lambda_handler(event, context):
    file = open("gl-dast-2.json")
    
    data = json.load(file)
    
    file.close()
    
    results = process_dumplicate(data.get("vulnerabilities", []))
    print(len(results))
    return 0
    
    # print(json.dumps(results))
    
    for item in results:
        details = item.get("details")
        
        if details is not None:
            href_url = get_url(details)
        else:
            href_url = item.get("url")
        # print(item.get("message"))
        print(href_url)
        

def get_url(details):
    urls = details.get("urls")
    url_item = urls.get("items")
    href = [item['href'] for item in url_item]
    return ','.join(href)


# class Worker(Thread):
#     def __init__(self, name, ip):
#         Thread.__init__(self)
#         self.name = name
#         self.ip = ip

#     def run(self):
#         response = os.system("ping -c 1 " + self.ip)
#         try_count = 5
#         while response != 0:
#             try_count -= 1
#             if try_count == 0:
#                 UNAVAILABLE_NETS.append((self.name, self.ip))
#                 return
#             response = os.system("ping -c 1 " + self.ip)


# def get_ips():
#     ips = {}
#     with open("gl-dast.json") as f:
#         for line in f.readlines():
#             line = line.strip()
#             data = line.split(":")
#             if len(data) != 2 or len(data[1]) < 7:
#                 continue
#             ips[data[0].strip()] = data[1].strip()

#     return ips

def process_dumplicate(datas):
    results = []
    
    distinct_messages = []

    for data in datas:
        if data.get("message") not in distinct_messages:
            distinct_messages.append(data.get("message"))
        else:
            continue
    
    for message in distinct_messages:
        items = [ d for d in datas if d.get("message") == message]

        result = {
            "description" : items[0].get("description"),
            "confidence": items[0].get("confidence"),
            "severity": items[0].get("severity"),
            "message": items[0].get("message"),
            "solution": items[0].get("solution"),
            "cve": items[0].get("cve"),
            "links": items[0].get("links"),
            "details": items[0].get("details"),
        }

        url = []
        
        for item in items:
            url.append(item.get("evidence").get("request").get("url"))
        
        result["url"] = ",".join(url)
        
        results.append(result)
    
    return results

def send_email():
    sns = boto3.resource('sns', region_name=REGION)
    topic = sns.Topic(SNS)
    now = datetime.now()
    message = f"Unavailable IPs: {now.strftime('%D %H:%M:%S')}\n"
    for name, ip in UNAVAILABLE_NETS:
        message += f"{name} - {ip} \n"
    topic.publish(Message=message)


import requests
import json

######### Receive group chat message #####################
# url = "https://api.p.2chat.io/open/whatsapp/groups/messages/WAG07950917-6608-461f-8d10-1eea6c1ba01d?page_number=0"

# payload = ""
# headers = {
#   'X-User-API-Key': 'UAKab3401ad-1a9f-4ecb-822a-cb960f89903c'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)

########## Send message to group ######################
# url = "https://api.p.2chat.io/open/whatsapp/send-message"

# payload = json.dumps({
# #   "to_number": "+19128185591",
#   "from_number": "+353873326005",
#   "to_group_uuid": "WAG07950917-6608-461f-8d10-1eea6c1ba01d",
#   "text": "Test from 2Chat API",
#   "url": "https://uploads-ssl.webflow.com/6281a9c52303343ff7c3b269/62a1648ee0273340bf38e3a9_logo-2C.svg"
# })
# headers = {
#   'X-User-API-Key': 'UAKab3401ad-1a9f-4ecb-822a-cb960f89903c',
#   'Content-Type': 'application/json'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)

##################### List all participalte  ########################
url = "https://api.p.2chat.io/open/whatsapp/group/WAG07950917-6608-461f-8d10-1eea6c1ba01d"

payload = ""
headers = {
  'X-User-API-Key': 'UAKab3401ad-1a9f-4ecb-822a-cb960f89903c'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

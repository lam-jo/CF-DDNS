import requests
import sys
from datetime import datetime
import time
import json

config = open('config.json','r').read()
config_json = json.loads(config)
domain = config_json['domain']
name = config_json['name']
token = config_json['token']

current_ipv4 = requests.get("https://api.ipify.org").text
#get ipv4

header = {"Authorization": "Bearer %s" % token}
url = "https://api.cloudflare.com/client/v4/"
verify_url = 'user/tokens/verify'
list_zone_url = "zones"

verify_result = requests.get(url+verify_url, headers = header)
verify_result_json = json.loads(verify_result.text)

if(verify_result_json['success']):
    print('Token valid')
else:
    print('Token verify faild')
    print(verify_result.text)
    quit()
#verify token    

zone_param = {"name": domain}

zone_list = requests.get(url + list_zone_url, headers=header, params=zone_param)
zone_identifier = json.loads(zone_list.text)['result'][0]['id']
#get zone_identifier

dns_param = {'per_page' :  5000}
dns_list_url = "zones/%s/dns_records" % zone_identifier
dns_list = requests.get(url + dns_list_url, headers=header, params = dns_param)
json_dns_list = json.loads(dns_list.text)
for i in json_dns_list['result']:
    if(i['name'] != name+'.'+domain):
        continue
    else:
        dns_identifier = i['id']
        print(i['name'])
        break
# find dns identifier

update_url = "zones/%s/dns_records/%s" % (zone_identifier, dns_identifier)
dns_detail = requests.get(url+update_url, headers = header, params = dns_param)
dns_detail_json = json.loads(dns_detail.text)
ipv4_record = dns_detail_json['result']['content']
#find specific details of the dns

print("currently updating to: "+dns_detail_json['result']['name'])

if current_ipv4 != ipv4_record:
    print("current ipv4 doesn't match with current dns record")
    print("update now? (y/n)")
    ans = ''
    while ans != 'y' and  ans != 'n':
        ans = input()
    if(ans == 'y'):
        data = {'type' : 'A', 'name' : name, 'content' : current_ipv4, 'ttl' : 60}
        update_result = requests.put(url + update_url, headers = header, json = data)
        if(update_result.status_code == 200):
            print('successfully updated')
            ipv4_record = current_ipv4
        else:
            print('error')
            with open('error.json', 'w') as err:
                print(update_result.text, file=err)
    else:
        quit()

while 1:
    current_time = datetime.now()
    print(current_time.strftime('%H:%M:%S'))
    current_ipv4 = requests.get("https://api.ipify.org").text

    if current_ipv4 != ipv4_record:
        data = {"type": "A", "name": name, "content": current_ipv4, "ttl": 60}
        update_result = requests.put(url + update_url, headers=header, json=data)
        ipv4_record = current_ipv4
        print('updata status code: ', end = '')
        print(update_result.status_code)
        i=60
        while(i>0):
            if(i!=60):
                if(i>=9):
                    print('\b\b', end = '', flush = True)
                else:
                    print('\b', end = '', flush = True)
            print(i, end = '', flush = True)
            time.sleep(1)
            i-=1
    else:
        print("ipv4 hasn't changed!")
        i=60
        while(i>0):
            if(i!=60):
                print('\b\b', end = '', flush = True)
            if(i>9):
                print(i, end = '', flush = True)
            else:
                print(i, end = ' ', flush = True)
            time.sleep(1)
            i-=1
        print('\r', end = '', flush = True)

import discord
import os
import requests
import json
from discord.ext import commands
import dns.resolver

ipv4_api = 'https://api.ipify.org'

config = open('config.json','r').read()
config_json = json.loads(config)
domain = config_json['domain']
name = config_json['name']
cf_token = config_json['token']
TOKEN = config_json['Discord_Token']

header = {"Authorization": "Bearer %s" % cf_token}
cf_url = 'https://api.cloudflare.com/client/v4/'
cf_verify_url = 'user/tokens/verify'
cf_list_zone_url = 'zones'

zone_param = {"name": domain}
zone_list = requests.get(cf_url + cf_list_zone_url, headers=header, params=zone_param)
zone_identifier = json.loads(zone_list.text)['result'][0]['id']
#get zone_identifier

dns_param = {'per_page' :  5000}
cf_dns_list_url = "zones/%s/dns_records" % zone_identifier
dns_list = requests.get(cf_url + cf_dns_list_url, headers=header, params = dns_param)
json_dns_list = json.loads(dns_list.text)
for i in json_dns_list['result']:
    if(i['name'] != name+'.'+domain):
        continue
    else:
        dns_identifier = i['id']
        break
# find dns identifier
cf_update_url = "zones/%s/dns_records/%s" % (zone_identifier, dns_identifier)



intents = discord.Intents.default()
intents.message_content = True

bot = discord.ext.commands.Bot(command_prefix = '!',intents = intents)

#dns query 
def dnsquery(name, query_type):
    resolver = dns.resolver.Resolver()
    try:
        result_message = resolver.resolve(name,query_type)
    except dns.resolver.NXDOMAIN:
        result = 'Non-existing domain!'
    except dns.resolver.NoAnswer:
        result = 'No records!'
    except dns.resolver.LifetimieTimeout:
        result = 'Time out!'
    except dns.rdatatype.UnknownRdatatype:
        result = 'Unknown DNS record type!'
    else:
        result = result_message.rrset
    return result


@bot.command()
async def verify(ctx):
    verify_result = requests.get(cf_url + cf_verify_url, headers = header)
    if(verify_result.status_code == 200):
        await ctx.reply('Token valid!')
    else:
        await ctx.reply(verify_result.text)


@bot.command()
async def check(ctx):
    current_ipv4 = requests.get(ipv4_api).text
    await ctx.reply('Current ipv4: '+current_ipv4)
    await ctx.reply(dnsquery(name+'.'+domain, 'A'))

@bot.command()
async def update(ctx):
    current_ipv4 = requests.get(ipv4_api).text 
    update_data = {'type' : 'A', 'name' : name, 'content' : current_ipv4, 'ttl' : 60}
    update_result = requests.put(cf_url + cf_update_url, headers = header, json = update_data)
    if(update_result.status_code == 200):
        await ctx.reply('successfully updated')
    else:
        await ctx.reply(update_result)


@bot.listen()
async def on_ready():
    print('ready!')

@bot.command()
async def clear(ctx):
    deleting_messages = []
    async for message in ctx.message.channel.history():
        deleting_messages.append(message)
    await ctx.message.channel.delete_messages(deleting_messages)


bot.run(TOKEN)

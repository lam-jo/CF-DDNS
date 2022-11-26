# How to use:
download all the files in the same dir, fill in the config,  
make sure relied packages are installed.  
works with only one domain.  
Install requests, json, datetime, time first.  
# config.json:
token: cloudflare api token.  
domain: SLD domain.  
name: subdomain name without SLD domain, if no, leave blank.  
Discord_Token: discord bot otken. 

# Demo.py:
relys: requests, sys, datetime, time, json. 

reads config.json as config - must be in same dir. 
checks public ip every 200 seconds, updates dns record when needed.  
while true dead loop. 

# discord_bot.py:
uses config.json as well as demo.py. 
Hears messages from every channel, so don't put the bot in public channels! Keep you bot secret!  

!check:
returns current public ip and current dns record. 

!verify:
verify cloudflare token. 

!update:
updates dns record regardless of if the ip has changed. 

!clear:  
clears all messages in the channel, be careful!  


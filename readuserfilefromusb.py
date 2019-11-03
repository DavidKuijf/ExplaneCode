import os
import json
import getpass

def readuserfilefromusb():
  for l in os.listdir('/media/'+getpass.getuser()+'/'):
    print(l)
    for usbfile in os.listdir('/media/'+getpass.getuser()+'/'+l):
      if(usbfile == "usersettings.json"):
        with open('/media/'+getpass.getuser()+'/'+l+'/usersettings.json') as usersettingsjsonfile:
          usersettings = json.load(usersettingsjsonfile)
      return usersettings

  return False




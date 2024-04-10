import requests
import json
import pandas as pd
import datetime
from io import StringIO

filepath = "yourFilepath"
#authenticate with username and password, get token 
def authenticate(username, password): 
    api_url = "https://api.aqmeshdata.net/api/Authenticate"
    auth = {"username":username,"password":password}
    header =  {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(auth), headers=header)
    date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    with open('log.txt', 'a') as f:
            f.write("\n "+date+" auth: "+str(response.status_code))
    if(response.status_code == 200):
        print("authentification successful")
        token = response.json()['token']
        #print(token)
        with open('token.txt', 'w') as f:  #save token in file
            f.write(token)
        return token
    else:
        print(response.status_code)
        print("authentification not successful!")
        return 0


#read token from token.txt file
def readToken():
    with open('token.txt','r') as f:  
        for line in f:
            token =  line.strip()
    return token


#get informations about AQMesh Pods and save in .csv
def getAssets(token):
    api_url = "https://api.aqmeshdata.net/api/pods/Assets"
    header =  {'Authorization': 'bearer {}'.format(token)}
    response = requests.get(api_url, headers=header)
    print(response.status_code)
    #print(json.dumps(response.json(), indent=4))
    try:
        df = pd.DataFrame(response.json())
        date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        df.to_csv('AQMesh_pods_'+date+'.csv', encoding='utf-8', sep=';', decimal=",", index=False)
        print("AQMesh_pods.csv updated")
    except Exception as e:
        print("AQMesh_pods.csv not updated")
        print(e)
    return(response.json())

#repeat gas reading, same output as last 'Next' call
def getGasReadingRepeat(token, loc_number, param):
    api_url = "https://api.aqmeshdata.net/api/LocationData/Repeat/"+loc_number+param
    header =  {'Authorization': 'bearer {}'.format(token)}
    response = requests.get(api_url, headers=header)
    print(response.status_code)
    with open('log.txt', 'a') as f:
        f.write(" repeat: "+str(response.status_code))
   # print(json.dumps(response.json(), indent=4))
    try:
        df = pd.DataFrame(response.json())
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename =filepath+loc_number+'_'+date+'.csv'
        df.to_csv(filename, encoding='utf-8', sep=';', decimal=",", index=False)
        print(filename+" updated")
    except Exception as e:
        print(filename+" not updated")
        print(e)
    return(response.json())




#get next gas reading and append to large .csv file
def getGasReadingAppend(token, loc_number, param):
    api_url = "https://api.aqmeshdata.net/api/LocationData/Next/"+loc_number+param
    header =  {'Authorization': 'bearer {}'.format(token)}
    response = requests.get(api_url, headers=header)
    print(response.status_code)
    #print(json.dumps(response.json(), indent=4))
    date = datetime.datetime.now().strftime("%Y-%m")
    filename =filepath+loc_number+'_output_'+date+'.csv'
    with open('log.txt', 'a') as f:
        f.write(" append: "+str(response.status_code))
    try:
        df = pd.DataFrame(response.json())
        df.to_csv(filename, encoding='utf-8', sep=';', decimal=",", index=False, mode="a")
        print(filename+" updated")
    except Exception as e:
        print(filename+" not updated")
        print(e)
    return(response.json())


token = authenticate("yourUsername", "yourPassword")
token = readToken()
myPods = getAssets(token)


loc_number = "3741" #location_number of pod
param = "/1/00" #param /1 gas; /0/ particles; /00 - celcius, ppb /01 - celcius, µg/m3
#gasReading = getGasReadingNext(token, loc_number, param)

gasReading = getGasReadingAppend(token, loc_number, param) #appends Next Gas Reading to AQMesh_loc#_output_year-month.csv
gasReading = getGasReadingRepeat(token, loc_number, param) #creates new file with timestamp

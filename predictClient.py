import json
import numpy as np
import requests
import time
from concurrent.futures import ThreadPoolExecutor

rServiceUrl = 'http://127.0.0.1:12800/api/rService/1.0'
rtServiceUrl = 'http://127.0.0.1:12800/api/rtService/1.0'

def consume_regular(token, payload):
    #print("consuming...")
    service_url = rServiceUrl
    header = {'Authorization': 'Bearer ' + token, 'Content-Type':'application/json'}
    # payload request with 100 requests
    res = requests.post(service_url, data=json.dumps(payload), headers=header)
    #print("Request completed successfully." + res.content)

def consume(token, payload):
    #print("consuming...")
    service_url = rtServiceUrl
    header = {'Authorization': 'Bearer ' + token, 'Content-Type':'application/json'}
    # payload request with 100 requests
    res = requests.post(service_url, data=json.dumps(payload), headers=header)
    #print("Request completed successfully." + res.content)

# authenticate with MRS Operationalization
login_url = 'http://127.0.0.1:12800/login'
header = {'content-type': 'application/json'}
payload = {'username':'admin', 'password':'Jup$ter16'}
res = requests.post(login_url, data=json.dumps(payload), headers=header)
token = json.loads(res.content.decode("utf-8"))["access_token"]

print("\n\nAuthenticated with the MRS Operationalization server: " + login_url + "\n")


print("===================================================================================================")
print("[LOCAL] Consuming Flexible R service using POST on url: "+rServiceUrl)
print("===================================================================================================")

numOfReq = 100
numOfThreads = 200
total_reqs = numOfReq * numOfThreads

revol_util = np.repeat(0, numOfReq).tolist()
int_rate = np.repeat(9.01, numOfReq).tolist()
annual_inc_joint = np.repeat("NA", numOfReq).tolist()
total_rec_prncp = np.repeat(49.04, numOfReq).tolist()

payload = {"inputData":{"revol_util": revol_util, "int_rate": int_rate, "mths_since_last_record": revol_util, "annual_inc_joint": annual_inc_joint, "dti_joint": annual_inc_joint, "total_rec_prncp": total_rec_prncp, "all_util": annual_inc_joint, "is_bad": revol_util}}

for it in range(0, 5):
  pool = ThreadPoolExecutor(numOfThreads)
  for i in range(0, numOfThreads):
      pool.submit(consume_regular, token, payload)

  s=time.clock()
  pool.shutdown(True)
  e=time.clock()

  time_taken = (e-s)
  print("Iteration {2}: Number of Requests: {3}, Time taken = {0} sec, Throughput = {1} scores/sec.".format(round(time_taken, 3), "{:,}".format(int(total_reqs/time_taken)), it, total_reqs))

print("\n\n")

numOfReq = 100
numOfThreads = 200
total_reqs = numOfReq * numOfThreads

revol_util = np.repeat(0, numOfReq).tolist()
int_rate = np.repeat(9.01, numOfReq).tolist()
annual_inc_joint = np.repeat("NA", numOfReq).tolist()
total_rec_prncp = np.repeat(49.04, numOfReq).tolist()

payload = {"inputData":{"revol_util": revol_util, "int_rate": int_rate, "mths_since_last_record": revol_util, "annual_inc_joint": annual_inc_joint, "dti_joint": annual_inc_joint, "total_rec_prncp": total_rec_prncp, "all_util": annual_inc_joint, "is_bad": revol_util}}

print("===================================================================================================")
print("[LOCAL] Consuming Realtime service using POST on url: "+rtServiceUrl)
print("===================================================================================================")
for it in range(0, 5):
  pool = ThreadPoolExecutor(numOfThreads)
  for i in range(0, numOfThreads):
      pool.submit(consume, token, payload)

  s=time.clock()
  pool.shutdown(True)
  e=time.clock()

  time_taken = (e-s)
  print("Iteration {2}: Number of Requests: {3}, Time taken = {0} sec, Throughput = {1} scores/sec.".format(round(time_taken, 3), "{:,}".format(int(total_reqs/time_taken)), it, total_reqs))



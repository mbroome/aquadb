from __future__ import print_function
from pprint import pprint
import os
import json
import time
import datetime
import traceback
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

import urllib
import json

elasticsearchCluster = 'XXXXXXXXXX'

print('Loading function')

indexDoc = {
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
      }
    }

esIndexName = 'aquadb'

def connectES(esEndPoint):
   print ('Connecting to the ES Endpoint {0}'.format(esEndPoint))
   try:

      access_key = os.getenv('AWS_ACCESS_KEY_ID')
      secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
      session_token = os.getenv('AWS_SESSION_TOKEN')
      region = os.getenv('AWS_REGION')

      auth = AWSRequestsAuth(aws_access_key=access_key,
                             aws_secret_access_key=secret_access_key,
                             aws_token=session_token,
                             aws_host=esEndPoint,
                             aws_region=region,
                             aws_service='es')

      esClient = Elasticsearch(host=esEndPoint,
                               port=443,
                               use_ssl=True,
                               connection_class=RequestsHttpConnection,
                               http_auth=auth)

      return esClient
   except Exception as E:
      print("Unable to connect to {0}".format(esEndPoint))
      print(E)
      exit(3)

def createIndex(esClient):
   try:
      res = esClient.indices.exists(esIndexName)
      if res is False:
         esClient.indices.create(esIndexName, body=indexDoc)

      return(1)
   except Exception as E:
      print("Unable to Create Index {0}".format(esIndexName))
      print(E)
      exit(4)

def indexDocElement(esClient, message):
   try:
      indexKey = message['alert']['alertId']
   except Exception as E:
      print("Error building indexKey.  Message in wierd format?")
      return(1)

   try:
      action = message['action']
   except Exception as E:
      print("Error finding action type.  Message in wierd format?")
      return(1)

   try:
      doc = {
             '@timestamp': datetime.datetime.now(),
             action: message
            }
      if action == 'Create':
         doc['@start'] = datetime.datetime.now()
      elif action == 'Acknowledge':
         doc['@ack'] = datetime.datetime.now()
      elif action == 'Close':
         doc['@end'] = datetime.datetime.now()

      retval = esClient.update(index=esIndexName, 
                               doc_type='alert',
                               id=indexKey,
                               body={
                                     'doc': doc,
                                     'doc_as_upsert':True
                                    }
                              )
      return(retval)

   except Exception as E:
      print("Error adding document to index: ", E)
      print(traceback.format_exc())
      exit(5)	
	  


def lambda_handler(event, context):
   print("Received event: " + json.dumps(event, indent=2))
   esClient = connectES(elasticsearchCluster)
   createIndex(esClient)
   message = {}
   data = event['Records'][0]['Sns']['Message']
   try:
      message = json.loads(data)
   except Exception as e:
      print(e)
      raise e

   print(message)
   try:
      response = indexDocElement(esClient, message)
      return response
   except Exception as e:
      print(e)
      print('Error getting adding object to elasticsearch: {0}.'.format(message))
      raise e


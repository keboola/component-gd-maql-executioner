import json
import logging
import os
import sys
import time
from kbc.client_base import HttpClientBase


class MAQLClient(HttpClientBase):

    def __init__(self, username, password, projectId, baseGoodDataUrl):

        self.paramUsername = username  # don't forget to lower this
        self.paramPassword = password
        self.paramProjectId = projectId
        self.paramBaseGoodDataUrl = baseGoodDataUrl

        HttpClientBase.__init__(
            self, base_url=self.paramBaseGoodDataUrl, max_retries=10)

        self._getSstToken()

    def _getSstToken(self):

        reqHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        reqBody = json.dumps({
            "postUserLogin": {
                "login": self.paramUsername,
                "password": self.paramPassword,
                "remember": 1,
                "verify_level": 2
            }
        })

        reqUrl = os.path.join(self.base_url, 'gdc/account/login')

        respObj = self.post_raw(url=reqUrl, headers=reqHeaders, data=reqBody)
        respSc, respJs = respObj.status_code, respObj.json()

        if respSc == 200:

            self.varSstToken = respJs['userLogin']['token']
            logging.info("SST token obtained.")

        else:

            logging.error("Could not obtain SST token.")
            logging.error("Received: %s - %s." % (respSc, respJs))
            sys.exit(1)

    def _getTtToken(self):

        reqHeaders = {
            'Accept': 'application/json',
            'X-GDC-AuthSST': self.varSstToken
        }

        reqUrl = os.path.join(self.base_url, 'gdc/account/token')

        respObj = self.get_raw(url=reqUrl, headers=reqHeaders)
        respSc, respJs = respObj.status_code, respObj.json()

        if respSc == 200:

            self.varTtToken = respJs['userToken']['token']

        else:

            logging.error("There was an error, when obtaining TT token.")
            logging.error("Received: %s - %s" % (respSc, respJs))
            sys.exit(2)

    def _buildHeader(self):

        self._getTtToken()

        _headerTemplate = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-GDC-AuthTT': self.varTtToken
        }

        self.reqHeader = _headerTemplate

    def sendQuery(self, query):

        self._buildHeader()

        reqBody = json.dumps({
            'manage': {
                'maql': query
            }
        })

        reqUrl = os.path.join(self.base_url, f'gdc/md/{self.paramProjectId}/dml/manage')
        logging.info("Executing query \"%s\"." % query)

        respObj = self.post_raw(url=reqUrl, headers=self.reqHeader, data=reqBody)
        respSc, respJs = respObj.status_code, respObj.json()

        if respSc == 200:

            return respJs['uri'].split('/')[-1]

        else:

            logging.error("Could not start an ETL task.")
            logging.error("Received: %s - %s." % (respSc, respJs))
            logging.error("Application failed at query: %s" % query)
            sys.exit(1)

    def checkEtlStatus(self, integrationId):

        self._buildHeader()

        reqUrl = os.path.join(self.base_url, f'gdc/md/{self.paramProjectId}/etltask/{integrationId}')
        jobRunning = True

        logging.info("Checking job info at %s." % reqUrl)
        startTime = time.time()

        while jobRunning is True:

            respJs = self.get(url=reqUrl, headers=self.reqHeader)

            taskStateMsg = respJs['taskState']['msg']
            taskStateStatus = respJs['taskState']['status']

            if taskStateStatus == 'RUNNING':

                time.sleep(5)

            elif taskStateStatus == 'ERROR':

                logging.error("There was an error for ETL task %s." % integrationId)
                logging.error("Received: %s - %s." % (taskStateMsg, taskStateStatus))
                sys.exit(1)
                jobRunning = False

            elif taskStateStatus == 'OK':

                endTime = time.time()
                elapsedTime = int(endTime - startTime)
                logging.info("Task successful. Elapsed time: %ss." % elapsedTime)
                jobRunning = False

            else:

                logging.error("Unhandled exception.")
                logging.error("Exception: %s - %s." % (taskStateStatus, taskStateMsg))
                sys.exit(2)

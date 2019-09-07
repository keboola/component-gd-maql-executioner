import csv
import json
import logging
import re
import sys
from lib.client import MAQLClient
from kbc.env_handler import KBCEnvHandler


KEY_USERNAME = 'username'
KEY_PASSWORD = '#password'
KEY_PROJECTID = 'projectId'
KEY_CUSTOMDOMAIN = 'customDomain'
KEY_QUERY = 'query'
KEY_GDURL = 'gooddataUrl'

MANDATORY_PARAMETERS = [KEY_USERNAME, KEY_PASSWORD, KEY_PROJECTID, KEY_QUERY]


class MAQLComponent(KBCEnvHandler):

    def __init__(self):

        KBCEnvHandler.__init__(self, MANDATORY_PARAMETERS)
        self.validate_config(MANDATORY_PARAMETERS)

        self.paramUsername = self.cfg_params[KEY_USERNAME]
        self.paramPassword = self.cfg_params[KEY_PASSWORD]
        self.paramProjectId = self.cfg_params[KEY_PROJECTID]
        self.paramCustomDomain = self.cfg_params[KEY_CUSTOMDOMAIN]
        self.paramQuery = self.cfg_params[KEY_QUERY]
        self.paramGooddataUrl = self.image_params[KEY_GDURL]

        self._processAndValidateParameters()
        self._getInputTables()

        self.client = MAQLClient(username=self.paramUsername,
                                 password=self.paramPassword,
                                 projectId=self.paramProjectId,
                                 baseGoodDataUrl=self.paramGooddataUrl)

    def _processAndValidateParameters(self):

        custDomain = re.sub(r'\s', '', self.paramCustomDomain)

        if custDomain != '':

            rxgString = r'https://.*\.gooddata\.com/*'
            rgxCheck = re.fullmatch(rxgString, custDomain)

            if rgxCheck is None:

                logging.error("%s is not a valid GoodData domain." %
                              custDomain)
                sys.exit(1)

            else:

                self.paramGooddataUrl = custDomain

        logging.info("Using domain %s." % self.paramGooddataUrl)

        maqlQuery = re.sub(r'\s', ' ', self.paramQuery).strip()

        if maqlQuery == '':

            logging.error("No query was specified.")
            sys.exit(1)

        else:

            self.paramQuery = maqlQuery

    def _getInputTables(self):

        if '{{ROW}}' in self.paramQuery:

            inputTables = self.configuration.get_input_tables()
            logging.debug(inputTables)

            if len(inputTables) == 0:

                logging.error("No input tables provided.")
                sys.exit(1)

            elif len(inputTables) > 1:

                logging.error("Multiple input tables provided. Please specify a single table.")
                sys.exit(1)

            inputTablePath = inputTables[0]['full_path']

            with open(inputTablePath + '.manifest') as manFile:

                manifest = json.load(manFile)

            inputTableColumns = manifest['columns']

            if len(inputTableColumns) != 1:

                logging.error("Please specify only one column in the input table.")
                sys.exit(1)

            else:

                self.varInputTablePath = inputTables[0]['full_path']

        else:

            self.varInputTablePath = None

    def run(self):

        if self.varInputTablePath is not None:

            with open(self.varInputTablePath) as inFile:

                reader = csv.reader(inFile)
                next(reader)

                for row in reader:

                    maqlQuery = re.sub('{{ROW}}', row[0], self.paramQuery)
                    logging.debug("Query:")
                    logging.debug(maqlQuery)

                    integrationId = self.client.sendQuery(maqlQuery)
                    self.client.checkEtlStatus(integrationId)

        else:

            integrationId = self.client.sendQuery(self.paramQuery)
            self.client.checkEtlStatus(integrationId)

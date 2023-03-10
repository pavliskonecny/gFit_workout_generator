"""
To start playing with Google Fit API visit: https://developers.google.com/fit/rest/v1/get-started
"""
from google_auth_oauthlib.flow import InstalledAppFlow


class _gFitAuth:
    # Additional scopes to apply when generating the refresh token
    # Check all available scopes at https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
    _SCOPES = "https://www.googleapis.com/auth/fitness.activity.read",\
        "https://www.googleapis.com/auth/fitness.location.read", \
        "https://www.googleapis.com/auth/fitness.body.read",\
        "https://www.googleapis.com/auth/fitness.activity.write"

    @staticmethod
    def get_tokens_old(oauth_client_id, oauth_client_secret):
        """
        Method to get Access + Refresh token. It makes sense only one time. Then store the token for reconnection.
        In case you change some SCOPE you need new tokens.
        :return: Refresh token and Refresh token for Google Fit API
        """
        client_config = {
            "installed": {
                "client_id": oauth_client_id,
                "client_secret": oauth_client_secret,
                "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, _gFitAuth._SCOPES)
        flow.run_local_server(host='localhost', port=8080,
                              authorization_prompt_message='Please visit this URL: {url}',
                              success_message='The auth flow is complete; you may close this window.',
                              open_browser=False)

        print("Access token: %s" % flow.credentials.token)
        refresh_token = flow.credentials.refresh_token
        print('\033[94m' + "GOOGLE FIT API REFRESH TOKEN: %s" % refresh_token + '\033[0m')
        return refresh_token

    @staticmethod
    def get_refresh_token(client_secret_file_name: str):
        """
        Refresh token makes sense to get only one time. Then store it and later change it for Access token.
        In case you change some SCOPE you need new token.
        :return: Refresh token for Google Fit API
        """
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file_name, _gFitAuth._SCOPES)
        credentials = flow.run_local_server(host='localhost',
                                            port=8080,
                                            authorization_prompt_message='Please visit this URL: {url}',
                                            success_message='The auth flow is complete; you may close this window.',
                                            open_browser=False)
        acc_token = credentials.token  # also in flow.credentials.token
        refresh_token = credentials.refresh_token  # also in flow.credentials.refresh_token
        print(f"\033[94m GOOGLE FIT API REFRESH TOKEN: {refresh_token} \033[0m")
        return refresh_token


import requests
import json
import time
import datetime
import others.my_files as my_files


class GoogleFit:
    _CLIENT_ID = ""
    _CLIENT_SECRET = ""
    _REFRESH_TOKEN = ""
    _API_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

    # Available dataType are at: https://developers.google.com/fit/datatypes/activity
    # for better results for steps you can replace dataSourceId by:
    # derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas
    # Also somebody recommend to remove value and key "dataSourceID".
    # To specify the request visit: https://developers.google.com/fit/rest/v1/reference/users/dataset/aggregate
    _READ_DATA = {
        "aggregateBy": [
            {
                "dataTypeName": "com.google.step_count.delta",   # steps
                "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
            },
        ],
        "bucketByTime": {"durationMillis": 86400000},                       # it is one day exactly
        "startTimeMillis": 1606086000000, "endTimeMillis": 1606341600000    # default value, will be replaced
    }

    _WRITE_DATA = {
            "dataSourceId": "derived:com.google.step_count.delta:1099052750196:Example Manufacturer:ExampleTablet:1000001:MyDataSource",
            "maxEndTimeNs": 1662008400000000000,
            "minStartTimeNs": 1662004800000000000,
            "point": [
                {
                    "dataTypeName": "com.google.step_count.delta",
                    "endTimeNanos": 1662008400000000000,
                    "originDataSourceId": "",
                    "startTimeNanos": 1662004800000000000,
                    "value": [
                        {
                            "intVal": 0
                        }
                    ]
                }
            ]
    }

    def __init__(self, client_secret_file_name: str, refresh_token: str):
        # Credentials from the Google Developers Console
        sec_file = json.loads(my_files.read_file(client_secret_file_name))

        self._CLIENT_ID = sec_file["installed"]["client_id"]
        self._CLIENT_SECRET = sec_file["installed"]["client_secret"]
        self._REFRESH_TOKEN = refresh_token

    def _get_access_token(self):
        """
        This function creates a new Access Token using the Refresh Token
        and also refreshes the ID Token (see comment below).
        :return: Access Token
        """
        authorization_url = "https://www.googleapis.com/oauth2/v4/token"
        params = {
            "grant_type": "refresh_token",
            "client_id": self._CLIENT_ID,
            "client_secret": self._CLIENT_SECRET,
            "refresh_token": self._REFRESH_TOKEN
        }

        response = requests.post(authorization_url, data=params)

        if response.ok:
            return response.json()['access_token']
        else:
            return None

    def get_data(self, date_from: datetime, date_to: datetime) -> dict:
        # Pass the new Access Token to Credentials() to create new credentials
        # credentials = google.oauth2.credentials.Credentials(access_token)
        access_token = self._get_access_token()

        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json;encoding=utf-8"
        }

        self._READ_DATA["startTimeMillis"] = GoogleFit.human_to_milli(date_from)
        self._READ_DATA["endTimeMillis"] = GoogleFit.human_to_milli(date_to)

        response = requests.post(self._API_URL, data=json.dumps(self._READ_DATA), headers=headers)

        # result = json.loads(response.text)
        result = response.json()
        return result

    def set_data(self, start_time: datetime, end_time: datetime, steps: int) -> dict:
        # Pass the new Access Token to Credentials() to create new credentials
        # credentials = google.oauth2.credentials.Credentials(access_token)
        access_token = self._get_access_token()

        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json;encoding=utf-8"
        }
        start_time_milli = GoogleFit.human_to_milli(start_time)
        end_time_milli = GoogleFit.human_to_milli(end_time)
        one_mill = 1000000
        self._WRITE_DATA["minStartTimeNs"] = start_time_milli * one_mill
        self._WRITE_DATA["maxEndTimeNs"] = end_time_milli * one_mill
        self._WRITE_DATA["point"][0]["startTimeNanos"] = start_time_milli * one_mill
        self._WRITE_DATA["point"][0]["endTimeNanos"] = end_time_milli * one_mill
        self._WRITE_DATA["point"][0]["value"][0]["intVal"] = steps

        url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/derived:com.google.step_count.delta:1099052750196:Example Manufacturer:ExampleTablet:1000001:MyDataSource/datasets/{start_time_milli}-{end_time_milli}"
        response = requests.patch(url, data=json.dumps(self._WRITE_DATA), headers=headers)

        # result = json.loads(response.text)
        result = response.json()
        return result

    def create_data_source(self, date_from: datetime, date_to: datetime, ac_t="") -> dict:
        # Pass the new Access Token to Credentials() to create new credentials
        # credentials = google.oauth2.credentials.Credentials(access_token)
        access_token = self._get_access_token()

        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json;encoding=utf-8"
        }

        data = {
          "dataStreamName": "MyDataSource",
          "type": "derived",
          "application": {
            "detailsUrl": "http://example.com",
            "name": "Foo Example App",
            "version": "1"
          },
          "dataType": {
            "field": [
              {
                "name": "steps",
                "format": "integer"
              }
            ],
            "name": "com.google.step_count.delta"
          },
          "device": {
            "manufacturer": "Example Manufacturer",
            "model": "ExampleTablet",
            "type": "tablet",
            "uid": "1000001",
            "version": "1.0"
          }
        }

        # self._WRITE_DATA["startTimeMillis"] = GoogleFit.human_to_milli(date_from)
        # self._WRITE_DATA["endTimeMillis"] = GoogleFit.human_to_milli(date_to)

        url = "https://www.googleapis.com/fitness/v1/users/me/dataSources"
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # result = json.loads(response.text)
        result = response.json()
        return result

    @staticmethod
    def get_refresh_token(client_secret_file_name: str):
        """
        Refresh token makes sense to get only one time. Then store it and later change it for Access token.
        In case you change some SCOPE you need new token.
        :return: Refresh token for Google Fit API
        """
        refresh_token = _gFitAuth.get_refresh_token(client_secret_file_name)
        return refresh_token

    @staticmethod
    def human_to_milli(date_time):
        """
        Convert human-readable time to mili seconds.
        """
        return int(time.mktime(date_time.timetuple()) * 1000)

    @staticmethod
    def milli_to_human(duration_in_ms: int):
        """
        Convert human-readable time to mili seconds.
        """
        return datetime.datetime.fromtimestamp(duration_in_ms / 1000.0).strftime('%D %H:%M:%S.%f')[:-3]

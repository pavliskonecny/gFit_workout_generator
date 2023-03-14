from gFit import GoogleFit
from datetime import datetime, timedelta
import json
import others.my_files as my_files

# Get client_secret file from google API console at: https://console.developers.google.com/apis/credentials
# Get refresh token from method GoogleFit.get_refresh_token(CLIENT_SECRET_FILE)
CLIENT_SECRET_FILE = "auth/client_secret.json"
REFRESH_TOKEN_FILE = "auth/refresh_token.txt"


def write_data(data=None):
    j_son = json.dumps(data, ensure_ascii=False, indent=2)
    name = "data.json"
    with open(name, mode='w') as outfile:
        print(j_son, file=outfile)


if __name__ == "__main__":
    # get refresh token
    if not my_files.exist_file(REFRESH_TOKEN_FILE):
        # Not necessary get refresh token every time. Just in case of reauthorization or change SCOPES
        gf_refresh_token = GoogleFit.get_refresh_token(CLIENT_SECRET_FILE)
        my_files.write_file(REFRESH_TOKEN_FILE, gf_refresh_token)
    else:
        gf_refresh_token = my_files.read_file(REFRESH_TOKEN_FILE)

    gf = GoogleFit(CLIENT_SECRET_FILE, gf_refresh_token)

    start_time = datetime(year=2023, month=3, day=1, hour=5)
    end_time = datetime(year=2023, month=3, day=1, hour=6)

    print("Getting data from Google Fit...")
    # data = gf.get_data(start_time=start_time, end_time=end_time)
    # data = gf.create_data_source(start_time=start_time, end_time=end_time)
    data = gf.set_data(start_time=start_time, end_time=end_time, steps=2000)
    write_data(data)

    print(f"\033[94m *** DONE ***")

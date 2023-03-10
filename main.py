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

    #date_to = datetime.today()
    #date_from = date_to.replace(hour=0, minute=0, second=0) - timedelta(days=30) # it's necessary to remove the time
    date_from = datetime(year=2022, month=11, day=13) #25.10. Todo Error when this value
    date_to = datetime(year=2022, month=11, day=14) #26.10. Todo error when this value

    print("Getting data from Google Fit...")
    data = gf.get_data(date_from=date_from, date_to=date_to, ac_t="ya29.a0AVvZVsppfotZ3mtx7VMLq746hP-JGR9kYMuQHnXyNssJseyPUV4ntF43lPz_lZguEm3LPJVA0sZkK4w_5KQkcZX3NSTONw-LfAZriGPYacAa-xi2WUCySw-7NL3lD0BsYbMUJjTKz93sqvonPTRLl6-SeMy13yYaCgYKAWkSARASFQGbdwaIt29vnaRbC6tXDumOYZmPHg0166")
    #data = gf.get_data(date_from=date_from, date_to=date_to)
    write_data(data)

    print(f"\033[94m *** DONE ***")

from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

# Define the scope of access you require
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def save_credentials(creds):
    with open('token.pkl', 'wb') as token:
        pickle.dump(creds, token)

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    save_credentials(creds)
    print("Token generated and saved to token.pkl")

if __name__ == '__main__':
    main()

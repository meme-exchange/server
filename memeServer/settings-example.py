# ! IMPORTANT !
# Create a copy called settings.py

# Mongo connection info
DATABASE = {
    "name":"memes-tests", # Just in case this gets run on production, it won't wipe out the DB
    "host":"mongo"
}

# Number of seconds to keep cache.
LAG_ALLOWED=1.5
# Generate this once, and only change it when you want to forece everyone to be logged out.
SECRET_KEY="EXAMPLE" 
# Amount of money to give new users
INITIAL_MONEY=1000.0
# Length in characters of the generated API key.
API_KEY_LENGTH=32
# Number of memes per page for pagination
STOCKS_PER_PAGE=50
# Number of memebucks a referral gets you.
MONEY_PER_REFERRAL=300
# Number of history entries to return
MAX_HISTORY_LENGTH=2000
# A passphrase that sparkpost can pass to my application
WEBHOOK_ID='CHANGE'
DONATION_DOMAIN='donations.memetrades.com'
CHARITY_DATA = {
    "email_from": "CHANGE",
    "subject": ["CHANGE"],
}

# Get this from developers.facebook.com 
FACEBOOK = {
    "APP_ID":"CHANGE",
    "APP_SECRET":"CHANGE",
  # "ACCESS_TOKEN":"CHANGE" # Not ucrrently used
}

#Used to tell facebook where to redirect
SERVER_NAME="http://my_server_name"

# Under no circumstances should these words be included...
BANLIST = []

# Maximum rate for levels of operations
EXPENSIVE_DB_OPERATION_LIMIT = '2/s'
INEXPENSIVE_DB_OPERATION_LIMIT = '5/s'
NO_DB_LIMIT = '10/s'

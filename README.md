# Bloque_5
## Previous requirements
### Once you have succesfully cloned the repository into your computer,to make sure it works perfectly, some non-default libraries need to be installed before executing the main .py program apuestas_webscraping.py All these indispensable libraries are included in a requirements.txt file, specifying the versions.

## Now you can download all the libraries by running the following command in your terminal.

pip install -r requirements.txt

### Moreover, you also need to change in apuestas_webscraping.py line 406 to include your API key. To obtain the API key you need to create an account in the web https://sportsdata.io/ and subscribe to the NBA-API. The API key will be sent to you by email or you´ll be able to find it in here  https://sportsdata.io/developers/api-documentation/nba 
### The config.txt file can be edited and left with this format:

{
    'api-key': '<your_api_key>'
}
### But it is just for you to remember, because when implementing it I thought it would be easier to just change it in the main .py, than having to use a config.txt file  and reading the content.


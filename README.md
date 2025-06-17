# FortiAuthenticator Serial Number Retrieval

Utilizing the FortiAuthenticator [REST API](https://docs.fortinet.com/document/fortiauthenticator/6.6.4/rest-api-solution-guide/927310/introduction) to retrieve the serial number of multiple FortiAuthenticator (FAC) instances. 

## Mechanics

A python script reads the IP addresses of the FAC instances from a file and makes the API request to retrieve the [systeminfo](https://docs.fortinet.com/document/fortiauthenticator/6.6.4/rest-api-solution-guide/671411/system-information-systeminfo). The json output is parsed to retrive the serial number. 

The results are written to a CSV file and reiterated from the list of IP addresses.

## Setting up the environment

2 files need to be modified in order to run the script

1. `ip_list.csv` - list of FAC IP addresses. These IP addresses must be reachable from the client machine executing the script
2. `password.txt` - username and password of admin which has RESP API access
> The admin user must be given explicit API Web Service Access in order to access the REST API. More details: https://docs.fortinet.com/document/fortiauthenticator/6.6.4/rest-api-solution-guide/999573/initializing-the-rest-api

## Executing the script

Issue the following command
```bash
python serials.py
```
The script will output progress and write the results to `results.csv`


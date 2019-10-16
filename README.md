# scigateway-auth
Authentication API for the SciGateway web application

## Contents
- [scigateway-auth](#scigateway-auth)
  - [Contents](#contents)
  - [Requirements](#requirements)
  - [Setup and running the API](#setup-and-running-the-api)
  - [Project structure](#project-structure)
  - [Running Tests](#running-tests)
  

## Requirements
All requirements can be installed with `pip install -r requirements.txt`

## Setup and running the API  
To run the apple, you must first create a `config.json` in the same level as `config.json.example`.
Then api may be ran by using `python scigateway-auth/app.py`


## Project structure
The project consists of 2 main packages, and app.py. The config, constants and exceptions are in the common
package and the endpoints and authentication logic are in src. The api is setup in app.py. A directory tree 
is shown below


`````
─── scigateway-auth
    ├── scigateway-auth  
    │   ├── common
    │   │   ├── config.py
    │   │   ├── constants.py
    │   │   └── exceptions.py
    │   ├── src
    │   │   ├── auth.py
    │   │   └── endpoints.py
    │   ├── test
    │   └── app.py
    ├── config.json
    ├── README.md
    ├── requirements.in
    └── requirements.txt
 `````

  
  
## Running Tests
To run the tests use `python -m unittest discover`

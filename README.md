# TinyRestCallbackService

A tiny HTTP RESTful service for executing callbacks (webhooks) whenever a specific REST endpoint is getting called.

## Features
* Configure arbitrarily named endpoints.
* Call(back) a webhook when an endpoint is getting called.
    * Attach a body, optionally supplemented by information from the original request.
    * This functionality can be used to virtually trigger any action, since only a webhook-wrapper is needed for that.
* Set a HTML message getting returned to the caller.
* Redirect to another site, just like a link shortener.
* Log the request attempt.
* Can be used either standalone or dockerized.

# Table of Contens
1. [Installation and starting the service](#installation-and-starting-the-service)
    1. [Standalone](#standalone)
    2. [Docker](#docker)
2. [Usage](#usage)
    1. [Config file](#config-file)
    2. [Database](#database)
3. [Purpose ](#purpose)
4. [License](#license)

# Installation and starting the service
You can either run the service standalone or in a Docker container.

## Standalone
- Install `python3`.
- Install `python3-pip`.
- Execute `pip3 install -r requirements.txt` to install all required python packages.
- Execute `./run.sh service <path/to/config.toml>` or `python3 tinyrestcallbackservice.py <path/to/config.toml>`.
    - The default config lies in `./data/config.toml`.

## Docker
- For building the image from scratch, use `docker compose build`.
- Alternatively, this will automatically be done when executing `docker compose up -d service` for the first time, which starts the main service in a docker container.
- If you want to also spin up the `webhook-testservice` for testing purposes (which only prints out the request data into the console), you can start that service via `docker compose up -d webhook-testservice`.

# Usage
For configuring this service, you only need to take a look at a single configuration file and a very simple database scheme.

## Config file
The default config file lies in `data/config.toml`. If you use multiple config files at once (for instance if you're running multiple instances of the TinyRestCallbackService), you just have to make sure that you apply to the following mandatory entries:

| Field | Type | Purpose | Default value |
| --- | --- | --- | --- |
| `HOST` | String | Host / Interface to bind the service to | "0.0.0.0" |
| `PORT` | Number | Port to bind the service to | 5080 |
| `PATH_PREFIX` | String | Path prefix to prepend to all endpoints | "" |
| `DATABASE` | String | Path to the database to be used. <br>In case the database doesn't exist yet, it's getting created on the fly. | "./data/tinyrestcallbackservice.db" |
| `SCHEMA` | String | Schema to use. <br>The tables and fields defined in `schema.sql` have to be present for the service to work properly. | "./schema.sql" |
| `DEFAULT_MESSAGE` | String | Default message getting returned to a requester, in case the endpoint called is not defined. | "Endpoint not found." |

## Database
The database follows the schema defined in `schema.sql`. The tables and fields defined in `schema.sql` have to be present for the service to work properly. Apart from that, you can enhance the schema according to your needs.

The table `ENDPOINT_CONFIG` holds all endpoint configurations to which the service responds, and the table `LOG` holds all logged request activites from users.

For entering new endpoint configurations, there are generally two methods:
- Use the helper script via `./run.sh add-endpoint <databasePath> [<schemaFile>]` or `python3 tools/add_endpoint_config.py <databasePath> [<schemaFile>]`, with the `schemaFile` being optional.
    - In case the database not existing yet, it's getting created on the fly.
- Use the `sqlite3`-CLI, or any other tool of your choice, to populate and edit endpoint configurations.

A brief description of the fields in `ENDPOINT_CONFIG`:

| Field | Datatype | Mandatory? | Purpose | Examples / Option(s) |
| --- | --- | --- | --- | --- |
| `ENDPOINT` | TEXT | y | Path to the endpoint. | Example: <br>test, test/2, t/e/s/t |
| `METHOD` | TEXT | y | Method the endpoint is listening to. | Options: <br>GET, POST, PUT, PATCH, DELETE |
| `LOG` | BOOLEAN | y | Whether to log the request attempt or not. | Options: <br>TRUE, FALSE |
| `MESSAGE` | TEXT | n | HTML message to be returned to the sender.<br>Cane be supplied with placeholders. | Example: <br>\<h1>you dun goofed!\</h1> |
| `REDIRECT_URL` | TEXT | n | URL to redirect to when calling the endpoint.<br>Can be supplied with placeholders. | Example: <br>https://bitcoin.org/ |
| `REDIRECT_WAIT` | INTEGER | n | Wait (in ms) until redirecting. | Options: <br>Value >= 0 |
| `WEBHOOK_URL` | TEXT | n | Webhook URL to call when the endpoint is getting called.<br>Can be supplied with placeholders. | Example: <br>http://localhost:5081/ |
| `WEBHOOK_METHOD` | TEXT | n | Method to call the webhook with. | Options: <br>GET, POST, PUT, PATCH, DELETE |
| `WEBHOOK_BODY` | TEXT | n | Body to deliver to the webhook.<br>Can be supplied with placehoders. | `time = <<timestamp>>`,<br>results in: `time = 133769420` |

Each endpoint is distinguised by the endpoint and a method in conjunction - no combination can appear twice.

### Placeholders
As mentioned in the previous table, the fields `MESSAGE`, `REDIRECT_URL`, `WEBHOOK_URL` & `WEBHOOK_BODY` can be supplied with placeholders.
<br>Possible placeholders:
| Placeholder | Resulting data | Datatype | Example |
| --- | --- | --- | --- |
| `<<endpoint>>` | Endpoint name called | String | `<<endpoint>>` -> `test` |
| `<<method>>` | Method used to call the endpoint | String | `<<method>>` -> `GET` |
| `<<host>>` | Host(-Interface) and Port the method has been called on | String | `<<host>>` -> `172.27.0.3:5080` |
| `<<requestUrl>>` | Complete request URL of the call. | String | `<<requestUrl>>` -> `http://172.27.0.3:5080/test` |
| `<<remoteIp>>` | Remote IP of the caller. | String | `<<remoteIp>>` -> `172.27.0.1`|
| `<<userAgent>>` | User Agent string of the caller. | String | `<<userAgent>>` -> `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.15.10 Chrome/87.0.4280.144 Safari/537.36 Konqueror (WebEnginePart)`|
| `<<timestamp>>` | Timestamp | Integer | `<<timestamp>>` -> `133769420` |

### Example Endpoint Configuration

| Field Name | Content |
| --- | --- |
| `ENDPOINT` | `test` |
| `METHOD` | `GET` |
| `LOG` | `true` |
| `MESSAGE` | `<h1>endpoint: <<endpoint>><br>time: <<timestamp>><br>host: <<host>><br>requestUrl: <<requestUrl>><br>remoteIp: <<remoteIp>><br>userAgent: <<userAgent>></h1>` |
| `REDIRECT_URL` | `https://test.service/<<endpoint>>` |
| `REDIRECT_WAIT` | `2000` |
| `WEBHOOK_URL` | `http://localhost:5081/<<endpoint>>` |
| `WEBHOOK_METHOD` | `POST` |
| `WEBHOOK_BODY` | `time = <<timestamp>>, userAgent = <<userAgent>>` |

# Purpose
This tiny service was originally intended to track whether specific QR-codes have been scanned. For instance: In case a link has been called, a series of actions, such as notifications, can be triggered in order to inform about such an event.

Feel free to abuse for any other purposes that come to your mind. I bet there are some more specific than what I've just described. ;)

# License
```
   Copyright 2022 Jan-Eric Schober

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

# TinyHttpCallbackService

A tiny service for executing callbacks whenever a HTTP request is received.

# SerialPortGateway
The SerialPortGateway functions as a gateway to serial devices, which can each be adressed by a unique device ID.

Features:
* Auto discovery of new serial devices
* Processing of incoming messages from the devices
    * Easy to use message format for communicating with serial devices
* Sending messages/commands to specific devices or all devices at once
* Automatic handling of IO Errors
* Logging of all actions
* Designed as a base class for other applications to be build upon
    * Callbacks for easily handling different events (New messages, devices added/deleted )
    * Easy to use interface for interfering with the gateway
* Parallelization of all time critical or potentially blocking tasks
* Quick configuration of the gateway via easy config files
* Can be used either dockerized or standalone

# Table of Contens
1. [Files and Folder structure](#files-and-folder-structure)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Usage](#usage)
    1. [Configuration files](#configuration-files)
    2. [Starting the application in a Docker container](#starting-the-application-in-a-docker-container)
    3. [Basic usage](#basic-usage)
5. [Notes](#notes)
6. [License](#license)

# Files and Folder structure

# Dependencies

# Installation

# Usage
## Configuration files

## Starting the application in a Docker container

## Basic usage

# Notes

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

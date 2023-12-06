# EE

### Installation

Initialize the DB

```
CREATE USER 'ee'@'localhost' IDENTIFIED BY 'ee';
GRANT ALL PRIVILEGES ON *.* TO 'ee'@'localhost' WITH GRANT OPTION;
CREATE DATABASE `ee` DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
```

Run the following script:

> python generate_api_key.py

Save the API Key generated. Use it for api calls.
There is no api timeout right now.

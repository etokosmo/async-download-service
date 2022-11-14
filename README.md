# Microservice for downloading files

## About

Microservice helps the work of the main site made on CMS and serves
requests to download archives with files. Microservice can do nothing but pack files
to the archive. Files are uploaded to the server via FTP or CMS admin panel.

The creation of the archive quickly upon request of the user. The archive is not stored on disk; instead, as it is packaged, it is immediately sent to the user for download.

The archive is protected from unauthorized access by a hash in the download link address, for example: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. The hash is given by the name of the directory with the files, the directory structure looks like this:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```

## Configurations

* Python version: 3.10
* Libraries: [requirements.txt](https://github.com/etokosmo/async-download-service/blob/master/requirements.txt)

## Launch

### Local server

- Download code
- Through the console in the directory with the code, install the virtual
  environment with the command:

```bash
python3 -m venv env
```

- Activate the virtual environment with the command:

```bash
source env/bin/activate
```

- Install the libraries with the command:

```bash
pip install -r requirements.txt
```

- Write the environment variables in the `.env` file in the format KEY=VALUE

`BASE_ARCHIVE_PATH` - string value. Specify the path to the directory with photos. Default = `test_photos`.

`ACTIVATE_LOGS` - bool value (`True` or `False`). Enable or disable logging. Default = True.

`PROCESS_DELAY` - positive integer value (`1`, `2`, `3` etc.). Enable response delay. Default = 0 (no delay).

> P.S. Default values are already set

- Run local server with the command (it will be available
  at http://127.0.0.1:8080/):

```bash
python server.py
```

## How to deploy to the server

```bash
python server.py
```

After that, redirect requests starting with `/archive/` to the microservice. For example:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```
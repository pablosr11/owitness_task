# Requirements:
- [Poetry](https://python-poetry.org/) for dependency management.

# Local setup:
- Env setup: ```poetry install```
- DB utils : Run 'utils.py' to create and populate a local sqlite DB with the given json file.
- How to run: ```uvicorn app.main:app```

# Build docker image
- For demo purposes and given its small size we are loading the sqlite file into
the image. Make sure you have run ```python utils.py``` before proceeding so it gets
populated.
- To avoid dealing with poetry when building, export the current dependencies as
a requirements file: ```poetry export -f requirements.txt --output requirements.txt```
- Image building: ```docker build -t IMAGE_NAME:IMAGE_TAG .  ```

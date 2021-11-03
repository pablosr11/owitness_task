# Requirements:
- [Poetry](https://python-poetry.org/) for dependency management.
- Docker

# Just run it:
- Make sure port 8080 is free or change it below.
- ```docker run --name ow --rm  -p 8080:8080 pablosr11/owitness:0.0.1```
- ```curl 'http://0.0.0.0:8080/api/titles'```
- ```curl 'http://0.0.0.0:8080/api/titles/1'```
- ```curl 'http://0.0.0.0:8080/api/titles?_order=desc&_sort=title_number,id'```
- Dont forget to remove the image after testing to keep system lightweight
    ```docker rmi $(docker images | grep 'pablosr11')```

# Local setup:
- Env setup: ```poetry install```
- DB utils : Run ```python utils.py``` to create and populate a local sqlite DB with the given json file.
- How to run: ```uvicorn app.main:app```

# Build docker image
- For demo purposes and given its small size we are loading the sqlite file into
the image. Make sure you have run ```python utils.py``` before proceeding so it gets
populated.
- To avoid dealing with poetry when building the image, export the current dependencies as
a requirements file: ```poetry export -f requirements.txt --output requirements.txt```
- Image building: ```docker build -t REPOSITORY/IMAGE_NAME:IMAGE_TAG .  ```

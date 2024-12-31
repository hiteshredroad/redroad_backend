# MongoDB with FastAPI

This is a small sample project demonstrating how to build an API with [MongoDB](https://developer.mongodb.com/) and [FastAPI](https://fastapi.tiangolo.com/).


## TL;DR
before running activate your Python virtualenv, and then run the following from your terminal (edit env file and update the `MONGODB_URL` first!):

[FastAPI URL](https://fastapi.tiangolo.com/virtual-environments/)

python -m venv .venv

.venv\Scripts\Activate.ps1

Get-Command python

echo "*" > .venv/.gitignore

pip install "fastapi[standard]"

pip install -r requirements.txt

```bash
# Install the requirements:
pip install -r requirements.txt

# Configure the location of your MongoDB database example(local):
MONGODB_URL="mongodb://localhost:27017/"

# Start the service:
uvicorn app:app --reload
```

(Check out [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) if you need a MongoDB database.)

Now you can load http://localhost:8000/docs or in which port you host in your browser ... but there won't be much to see until you've inserted some data.

If you have any questions or suggestions, check out the [MongoDB Community Forums](https://developer.mongodb.com/community/forums/)!

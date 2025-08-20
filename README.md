
# Interview-Style Conversational Agents

We recommend installing a new conda environment when setting up this project.

## Local Setup

Python 3.12 is supported. If you are using conda you can create an environment with:
```
conda create --name isca python=3.12
```

Install the requirements with:
```
pip install -r requirements.txt
```

You may need to install the libmysqlclient-dev package to install the python mysql library:
```
default-libmysqlclient-dev
```

You will need to install mysql and setup a user with the name biobot. Create a database named interview and import the init.sql database with the following command:
```
mysql -u root -p interview < init.sql
```

Give the new user privileges on this database and then put the password in runserver.sh

Update the MYSQL password in the runserver.sh.

Choose a new SECRET_KEY in ewc19/ewc19/settings.py

Now install the spacy model used for topic modeling:
```
python -m spacy download en_core_web_sm
```

## Running the server

You can run the webserver as a python application with ```runserver.sh```. To deploy the system for data collection, you probably want to run it as a uWSGI application. There is a config file at ewc19/ewc19/uwsgi_ewc19.ini that you can modify. See the [Django documentation](https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/uwsgi/) for more information.

You should see a message saying it is running on http://127.0.0.1:8000 and you can connect to this port in any web browser.
Go to http:127.0.0.1:8000/interview/admin/management/login for the administrative console or to http:127.0.0.1:8000/interview/write for the participant facing side.

The default login information for the admin panel is:

```
Username: adminuser
Password: testpassword
```

You should change this at http://127.0.0.1:8000/interview/admin as soon as possible.

## Demo Video

See the demo video here: https://www.youtube.com/watch?v=_5XvMsZf8dA

<!-- ## Citation

If you use this code please cite our paper:
```
@inproceedings{welch-2025-framework,
  title = {A Framework for Interview-Style Conversational Agents},
  author = {Welch, Charles and Lahnala, Allison and Varadarajan, Vasudha and Flek, Lucie and Mihalcea, Rada and Boyd, Lomax and Sedoc, João},
  booktitle = {arxiv preprint},
  year = {2025},
}
``` -->
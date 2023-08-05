Difio registration agent for Heroku / Python applications.

It compiles a list of locally installed Python packages and sends it to
<http://www.dif.io>.


Installing on your Heroku application
--------------------------------------

Create an account at <http://www.dif.io>

Create a Python application on Heroku

Add a dependency in your `requirements.txt` file

::

    echo 'difio-heroku-python' >> requirements.txt

Set the following environment variables on Heroku

::

    heroku config:set DIFIO_USER_ID=YourUserID
    heroku config:set DIFIO_APP_NAME=MyApplication
    heroku config:set DIFIO_APP_URL=http://myapp.herokuapp.com

Then commit and push your application to Heroku

::

    git commit -a -m "added dependency on Difio"
    git push heroku master


Execute the registration script to submit the information to Difio

::

    heroku run /app/.heroku/venv/bin/difio-heroku-python
    Running `/app/.heroku/venv/bin/difio-heroku-python` attached to terminal... up, run.1
    Success, registered/updated application 8370e3be-6e54-462d-9ca9-224301c29a1d

That's it, you can now check your application statistics at
<http://www.dif.io>


Updating your requirements.txt
------------------------------

Whenever you change your `requirements.txt` file to include new
dependencies or upgrade/downgrade package versions you should
re-submit the information to Difio. 

::

    heroku run /app/.heroku/venv/bin/difio-heroku-python

Difio registration agent for cloudControl / Python applications.

It compiles a list of locally installed Python packages and sends it to
<http://www.dif.io>.


Installing on your cloudControl application
--------------------------------------

Create an account at <http://www.dif.io>

Create a Python application on cloudControl

Add a dependency in your `requirements.txt` file

::

    echo 'difio-cloudcontrol-python' >> requirements.txt

Then commit, push and deploy your application to cloudControl

::

    git commit -a -m "added dependency on Difio"
    cctrlapp APP_NAME push
    cctrlapp APP_NAME deploy

Configure your user credentials

::

    cctrlapp APP_NAME/DEP_NAME addon.add config.free --DIFIO_USER_ID=YourUserID


Execute the registration script to submit the information to Difio

::

    cctrlapp APP_NAME/DEP_NAME run /app/.heroku/venv/bin/difio-cctrl-python
    Running `/app/.heroku/venv/bin/difio-cctrl-python` attached to terminal... up, run.1
    Success, registered/updated application 8370e3be-6e54-462d-9ca9-224301c29a1d

That's it, you can now check your application statistics at
<http://www.dif.io>


Updating your requirements.txt
------------------------------

Whenever you change your `requirements.txt` file to include new
dependencies or upgrade/downgrade package versions you should
re-submit the information to Difio. 

::

    cctrlapp APP_NAME/DEP_NAME run /app/.heroku/venv/bin/difio-cctrl-python

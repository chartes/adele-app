# The [Adele](https://adele.chartes.psl.eu/) API
Adele application API (collaborative diplomatic edition) ([Adele](https://adele.chartes.psl.eu/)).

![Static Badge](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python&label=PYTHON&color=blue)

![Static Badge](https://img.shields.io/badge/Flask-2.0.1-blue?logo=flask)

## Install

- Clone the GitHub repository in your projects' folder:
<pre>
<code>
  cd <b><i>path/to/projects_folder/</i></b>
  git clone https://github.com/chartes/adele-app.git
</code>
</pre>
- Ensure you are running Python 3.12, for example with pyenv:
  ```bash
  pyenv shell 3.12
  ```

- Set up the virtual environment:
  <pre><code>
  cd <b><i>path/to/projects_folder</i></b>/adele-app
  python -m venv <b><i>your_venv_name</i></b>
  source <b><i>your_venv_name</i></b>/bin/activate
  pip install -r requirements.txt
  </code></pre>

- For servers requiring uWSGI to run Python apps (remote Nginx servers):
  - check if uWSGI is installed `pip list --local`
  - install it in your virtual *__your_venv_name__* if it's not: `pip install uwsgi`.
  The WSGI application is located at `flask_app:flask_app`
  *NB : this command may require wheel:*
    - to check whether wheel is installed: `pip show wheel`
    - to install it if required: `pip install wheel`

## Launch the app:

> :warning: Below commands are mainly for local launch.
> For servers, apps may be started via processes management tools, refer to the servers documentation
  - Reactivate the virtual environment if needed (<code>source <b><i>your_venv_name</i></b>/bin/activate</code>)
  - Launch:
  from the subfolder containing flask_app.py (<code>cd <b><i>path/to/adele_app</i></b></code>)
    <code>python flask_app.py (--config=<b><i>local/staging/prod/test</i></b>)</code>
  - Then visit http://localhost:5000/api/1.0/documents?192 to test it is running



## Launch the front-end:
- [Front-end's Readme](https://github.com/chartes/adele-vue)

---
Additional details for offline commands:


```bash
python3 manage.py --help

Usage: manage.py [OPTIONS] COMMAND [ARGS]...

Options:
  --config [local|staging|prod|test]  select appropriate .env file to use
                                 [default: staging]
  --help                         Show this message and exit.

Commands:
  db-create     Create the database
  db-recreate   Recreate the database
  load-fixtures Load test fixtures
  add-manifest  Add a IIIF manifest
  add-user      Add a new database user

```

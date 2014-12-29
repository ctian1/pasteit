## Pastes

A simple Pastes application written in Python3 and CherryPy

### Dependencies

 * Python >= 3.3 (during development was used Python 3.4)
 * CherryPy (available on PIP)
 * Jinja2 (available on PIP)
 * Pygments (available on PIP)
 
 * PyYAML and psycopg2 if modifications
 
### Normal installation
 * Edit options in pasteit.conf (namely master password)
 * in pasteit.conf, add the absolute path to your directory
 * pip install -r requirements.txt
 
### Modifications that this repo adds:
 * use postgres as database instead of saving pastes to file
 * add temporary/permanent paste type
 * add delete paste option for logged in user
 * other small fixes/changes
 
### Installion of modifications
 * setup ssl by adding privkey and cert
 * add postgres db info in db.yaml
 * you may need to edit line 249 of src/pasteit.py for your port
# cse412_project

For the backend coders you should build a virtual environment called "venv" in ./backend. You should also create a .env file in ./backend with variables set that will be used for database connection. For example here's Hrishi's ./backend/.env contents:

DBNAME=project
DBUSER=hrishi
DBPASSWORD=""
DBHOST=localhost
DBPORT=8888

You should also switch your terminal and python interpreter to that of the virtual environment. On Linux Ubuntu this is done with:
source ./backend/venv/vin/activate

After that, please get the required dependencies for this project with:
pip install -r ./backend/requirements.txt

You might need to run the following commands (or thier equivilant) to get all the dependencies needed if the last step fails:
sudo apt-get install python3.12-dev
sudo apt-get install libpq-dev

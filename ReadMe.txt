
Download Python 3.9.13 - Programming language  https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
Checkbox should be checked for Add Python to PATH

Django 4.1.3 - Framework  pip install Django

Download and Install XAMPP https://sourceforge.net/projects/xampp/files/XAMPP%20Linux/8.1.12/xampp-linux-x64-8.1.12-0-installer.run

Download and Install Vscode https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user

in xampp start apache and mysql 
Click on mysql > admin
create a database named : airconditioner_database

Setup Source code
python --version //To check if the python was properly installed
python -m venv venv //Creates a virtual environment folder,
cd venv/Scripts //navigate to the activate.bat directory
activate //this will activate the virtual environment(venv)
pip install -r requirements.txt //this will install all dependencies
python manage.py makemigrations //creates a mapping of python classes into database
python manage.py migrate // this will perform the actual conversion of python classes into mysql database

python manage.py createsuperuser //this will create admin account


python manage.py runserver //This will run the web app





Download Python 3.9.13 - Programming language  https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
Checkbox should be checked for Add Python to PATH
click windows icon/start menu then search "alias" on the bottom most part of the screen turn off the two python entries
python --version //To check if the python was properly installed

Django 4.1.3 - Framework  pip install Django

Download and Install XAMPP https://sourceforge.net/projects/xampp/files/XAMPP%20Linux/8.1.12/xampp-linux-x64-8.1.12-0-installer.run

Download and Install Vscode https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user

in xampp start apache and mysql 
Click on mysql > admin
create a database named : airconditioner_database

open vscode and install the ff extensions:
ms-python.python


Setup Source code
[One time only, if venv is not yet created]
python -m venv venv //Creates a virtual environment folder,

[run this if the venv is not yet activated in cmd]
cd venv/Scripts //navigate to the activate.bat directory
activate //this will activate the virtual environment(venv)

[run this everytime the source code was updated]
pip install -r requirements.txt //this will install all dependencies
python manage.py makemigrations //creates a mapping of python classes into database
python manage.py migrate // this will perform the actual conversion of python classes into mysql database

[run this if there's no admin user yet]
python manage.py createsuperuser //this will create admin account

[run this to start your web app]
python manage.py runserver //This will run the web app




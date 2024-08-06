To build new executable:

delete build / disc / .spec
delete / migrate .db file -- only if changing league

pyinstaller --onefile main.py --name SSF_Trade --icon=static/logo.ico --add-data "static:static" --add-data "templates:templates"
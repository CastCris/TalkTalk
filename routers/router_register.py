from begin import *

import importlib
import inspect

##
def router_register(app:object, folder:str)->None:
    folder_path = os.path.abspath(folder)

    for file in os.listdir(folder_path):
        if file in ROUTER_REGISTER_IGNORE:
            continue
        print(file)

        file_extension = file.split('.')[-1]
        file_path = f"{folder}/{file}"

        if file_extension != 'py' and os.path.isfile(file_path):
            continue
        elif file_extension != 'py':
            router_register(app, file_path)

        ##
        module_name = file[:-3]
        module = importlib.import_module(module_name)
        
        for i,j in inspect.getmembers(module):
            if isinstance(j, flask.Blueprint):
                app.register_blueprint(j)

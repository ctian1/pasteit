#!/usr/bin/python3.4
import cherrypy
import jinja2

# The jinja2 enviroment
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

def template(name):
    """ Decorator which render the template passed to it with all arguments returned from the function """
    def decorator(f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs) # Execute the function
            # If the function return nothing, suppose it want to return an empty dict
            if not result:
                result = {}
            tmpl = jinja_env.get_template(name) # Prepare the template
            return tmpl.render(**result) # Return the rendered version of it
        return wrapper
    return decorator

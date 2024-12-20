from flask import Flask,request,abort
from functools import wraps

app = Flask(__name__)


    #TODO unpack the request headers
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)
    
    auth_headers = request.headers["Authorization"]
    header_parts = auth_headers.split(' ')
    if len(header_parts) != 2:
        abort(401)
    elif header_parts[0].lower() != 'bearer':
        abort(401) 
    return header_parts[1]

def requires_auth(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        jwt = get_token_auth_header()
        return f(jwt, *args,**kwargs)
    return wrapper

@app.route('/headers')
@requires_auth
def headers(jwt):
    print(jwt)
    return "Not Implemented"

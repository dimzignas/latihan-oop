import uuid
from flask import render_template
# from views.alerts import alert_blueprint
# from views.stores import store_blueprint
from views.users import user_blueprint
from config import connex_app, app

__author__ = 'dimz'

# Get the application instance
app.secret_key = uuid.uuid4().hex

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('openapi.yml')

# app.register_blueprint(alert_blueprint, url_prefix='/alerts')
# app.register_blueprint(store_blueprint, url_prefix='/stores')
app.register_blueprint(user_blueprint, url_prefix='/users')
# connex_app.register_blueprint(products_blueprint, url_prefix='/products')


# Create a URL route in our application for "/"
@app.route("/")
def home():
    return render_template("home.html")


if __name__ == '__main__':
    connex_app.run(host='0.0.0.0', port=61296, debug=True)

import os
import connexion
from flask_marshmallow import Marshmallow
from swagger_ui_bundle import swagger_ui_3_path


basedir = os.path.abspath(os.path.dirname(__file__))

# Create the connexion application instance
options = {'swagger_path': swagger_ui_3_path}
connex_app = connexion.App(__name__, specification_dir=os.path.join(basedir, 'openapi/'), options=options)

# Get the underlying Flask app instance
app = connex_app.app

# Initialize Marshmallow
ma = Marshmallow(app)
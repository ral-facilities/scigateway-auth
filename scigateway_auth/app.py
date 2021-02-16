from flask import Flask
from flask_restful import Api

if __name__ == "__main__":  # NOQA: E402
    from scigateway_auth.common import constants
    constants.SECURE = False

from scigateway_auth.common.config import config
from scigateway_auth.common.logger_setup import setup_logger
from scigateway_auth.src.endpoints import LoginEndpoint, VerifyEndpoint, RefreshEndpoint, AuthenticatorsEndpoint, \
    MaintenanceEndpoint, ScheduledMaintenanceEndpoint  # NOQA: E402

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)

setup_logger()

api.add_resource(LoginEndpoint, "/login")
api.add_resource(VerifyEndpoint, "/verify")
api.add_resource(RefreshEndpoint, "/refresh")
api.add_resource(AuthenticatorsEndpoint, "/authenticators")
api.add_resource(MaintenanceEndpoint, "/maintenance")
api.add_resource(ScheduledMaintenanceEndpoint, "/scheduled_maintenance")

if __name__ == "__main__":
    app.run(host=config.get_host(), port=config.get_port(),
            debug=config.is_debug_mode())

from flask import (
    Blueprint,
    request,
    escape,
)
from flask_login import login_required, current_user
from flask import current_app as app
from ..util.price_providers import update_price

# Setup endpoint blueprint
price_endpoint = Blueprint("price_endpoint", __name__)

################ Price settings ####################
@price_endpoint.route("/update/", methods=["GET", "POST"])
@login_required
def update():
    try:
        price_type = escape(request.form.get("price_type", "manual"))
        if price_type == "manual":
            alt_rate = escape(request.form.get("alt_rate", 0))
            alt_symbol = escape(request.form.get("alt_symbol", ""))
            app.specter.update_price_provider("", current_user)
            app.specter.price_checker.stop()
            if alt_rate and alt_symbol:
                app.specter.update_alt_rate(alt_rate, current_user)
                app.specter.update_alt_symbol(alt_symbol, current_user)
                return {"success": True}
        else:
            price_provider = escape(request.form.get("price_provider", ""))
            app.specter.update_price_provider(price_provider, current_user)
            if not app.specter.price_checker.running:
                app.specter.price_checker.start()
            return {"success": update_price(app.specter, current_user)}
    except Exception as e:
        app.logger.warning("Failed to update price settings. Exception: {}".format(e))
    return {"success": False}


@price_endpoint.route("/toggle/", methods=["GET", "POST"])
@login_required
def toggle():
    try:
        app.specter.update_price_check_setting(
            not app.specter.price_check, current_user
        )
        return {"success": True}
    except Exception as e:
        app.logger.warning("Failed to update price settings. Exception: {}".format(e))
    return {"success": False}

from flask import Blueprint, render_template
from models.product import Product
from models.user import requires_login

products_blueprint = Blueprint("products", __name__)


@products_blueprint.route("/")
@requires_login
def index():
    query = {'kota': {'$regex': ".*barat.*", '$options': 'i'}}
    projecting = {'sumber': 1, 'tgl_crawl': 1, 'nama_produk': 1, 'harga': 1, 'thumb': 1}
    sort = [("harga", -1)]
    limit = 10
    # data = Product.test(query, projecting, sort, limit)
    data = Product.test()
    # alerts = Alert.find_many_by("user_email", session["email"])
    return render_template("products/index.html", data=data)

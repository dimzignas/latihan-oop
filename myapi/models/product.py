# System modules
import uuid
from dataclasses import dataclass, field
from typing import List

# 3rd party modules
from flask import make_response, abort

# local modules
from config import ma
from models.model import Model
from models.recipe import Recipe, RecipeSchema
from models.user.decorators import requires_login
from common.database import Database

__author__ = 'dimz'


class ProductSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("_id", "sumber", "tgl_crawl", "nama_produk", "link_produk", "deskripsi",
                  "thumb", "harga_unit", "harga_awal", "harga", "discount", "qty", "qty_unit",
                  "username", "link_toko")


@dataclass(eq=False)
class Product(Model):
    # collection = "items"
    collection: str = field(init=False, default="products")
    sumber: str
    tgl_crawl: str
    nama_produk: str
    link_produk: str
    deskripsi: str
    thumb: str
    harga_unit: str
    harga_awal: str
    harga: str
    discount: str
    qty: str
    qty_unit: str
    nama_toko: str
    link_toko: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self):
        product_schema = ProductSchema()
        return product_schema.dump(self)

    @staticmethod
    def find_produk(query=None, projecting=None, sort: List = None, offset: int = 0, limit: int = 10):
        """Mencari produk dari database dengan query dan projecting, ditambah opsi sorting, skip, dan limit

        @param query: Dict query pencarian
        @param projecting: Dict kolom projecting (field yg ingin diambil sbg output query)
        @param sort: List of tuple kolom yg digunakan sebagai sorting
        @param offset: int posisi awal record yg akan diambil
        @param limit: int jumlah record yg akan diambil
        @return: hasil pencarian dari database
        """
        if query is None:
            query = {}
        result = Database.DATABASE['products'].find(query, projecting)
        if sort is not None:
            result = result.sort(sort)
        result = result.skip(offset).limit(limit)
        return result

    @staticmethod
    @requires_login
    def read_all(f: List, v: List, sort: List = None, offset: int = 0, limit: int = 10):
        """Fungsi ini merespon API pada endpoint /api/v1.0/produk, yaitu mencari produk yang sesuai dengan parameter yang
        diberikan.
        @param f: List dari field/atribut yang digunakan dalam pencarian
        @param v: List dari nilai field/atribut yang digunakan dalam pencarian
        @param sort: List nama field/atribut yang digunakan untuk melakukan sorting
        @param offset: posisi awal record pada hasil pencarian
        @param limit: batas jumlah record yang akan diambil
        @return: JSON record produk yang dicari
        """
        # build query
        if len(f) != len(v):
            abort(400, 'Parameter f tidak sama banyak dengan parameter v, mohon cek kembali.')
        if limit > 50:
            abort(400, 'Parameter limit lebih dari nilai maksimum (50).')
        query = {field_a: {'$regex': ".*{}.*".format(value), '$options': 'i'} for field_a in f for value in v}

        # build sort
        if sort is None:
            sort = ['nama_produk']
        sort_ = [(s, Database.ASCENDING) for s in sort]

        # Cari produk dari database
        produk = Product.find_produk(query=query, sort=sort_, offset=offset, limit=limit)

        if produk is None:
            # Bila tidak ditemukan sama sekali
            return make_response(
                "Tidak ditemukan produk dengan parameter yang telah diberikan.", 204
            )
        else:
            # Serialize the data for the response
            product_schema = ProductSchema(many=True)
            data = product_schema.dump(produk)
            return data

    @staticmethod
    @requires_login
    def read_resep():
        """

        @return:
        """
        # ambil resep dari API pihak ketiga
        recipes = Recipe.read_all()

        # Serialize the data for the response
        recipes_schema = RecipeSchema(many=True)
        data = recipes_schema.dump(recipes)
        return data

    @staticmethod
    @requires_login
    def read_komplemen(q: List, sort: List = None, offset: int = 0, limit: int = 10):
        """Fungsi ini merespon API pada endpoint /api/v1.0/produk/komplemen, yaitu mencari produk pelengkap sebagai
        rekomendasi bila mencari produk tertentu. Rekomendasi diberikan berdasarkan data bahan dari menu yang didapat
        melalui API eksternal.
        @param q: List dari nilai field/atribut yang digunakan dalam pencarian
        @param sort: List nama field/atribut yang digunakan untuk melakukan sorting
        @param offset: posisi awal record pada hasil pencarian
        @param limit: batas jumlah record yang akan diambil
        @return: JSON record produk yang dicari
        """
        # pengecekan awal
        if limit > 50:
            abort(400, 'Parameter limit lebih dari nilai maksimum (50).')

        # ambil resep dari API eksternal
        recipes = Recipe.read_all()

        bahans = [b for r in recipes for b in r.pop('bahan')]
        nama_bahans = [b.pop('nama_bahan') for b in bahans]
        str_nama_bahan = ' '.join(nama_bahans)

        # build sort
        if sort is None:
            sort = ['nama_produk']
        sort_ = [(s, Database.ASCENDING) for s in sort]

        # Cari produk dari database
        query = {'$text': {'$search': "{}".format(str_nama_bahan)}}
        produk = Product.find_produk(query=query, sort=sort_, offset=offset, limit=limit)

        if produk is None:
            # Bila tidak ditemukan sama sekali
            return make_response(
                "Tidak ditemukan produk dengan parameter yang telah diberikan.", 204
            )
        else:
            # Serialize the data for the response
            product_schema = ProductSchema(many=True)
            data = product_schema.dump(produk)
            return data

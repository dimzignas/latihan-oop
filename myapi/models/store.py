# System modules
import uuid
from dataclasses import dataclass, field
from typing import Dict

# 3rd party modules
from flask import make_response, abort

# local modules
from config import ma
from models.model import Model
from models.user.user import requires_login, requires_admin


class StoreSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("_id", "nama_toko", "deskripsi", "link_toko")


@dataclass(eq=False)
class Store(Model):
    # collection = "stores"
    collection: str = field(init=False, default="stores")
    nama_toko: str
    deskripsi: str
    link_toko: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        store_schema = StoreSchema()
        return store_schema.dump(self)

    @classmethod
    def get_by_name(cls, nama_toko: str) -> "Store" or None:
        try:
            return cls.find_one_by("nama_toko", nama_toko)
        except TypeError:
            return None

    @staticmethod
    @requires_login
    def read_all():
        """Fungsi ini merespon API pada endpoint /api/v1.0/stores, yaitu dengan mencari semua data toko dalam database.
        @return: semua hasil pencarian toko
        """
        # Create the list of stores from our data
        store = Store.all()

        if store is None:
            # Bila tidak ditemukan sama sekali
            return make_response(
                "Tidak ditemukan toko dengan parameter yang telah diberikan.", 204
            )
        else:
            # Serialize the data for the response
            store_schema = StoreSchema(many=True)
            data = store_schema.dump(store)
            return data

    @staticmethod
    @requires_login
    def read_one(store_id: str):
        """Fungsi ini merespon API pada endpoint /api/v1.0/stores/{store_id}, yaitu dengan mencari satu toko dengan
        parameter toko_id.
        @param store_id: String id sebagai acuan pencarian toko pada database
        @return: Toko hasil pencarian
        """
        # Build the initial query
        try:
            store = Store.get_by_id(store_id)
        except TypeError:
            store = None

        # Did we find a store?
        if store is not None:
            # Serialize the data for the response
            store_schema = StoreSchema()
            data = store_schema.dump(store)
            return data

        # Otherwise, nope, didn't find that store
        else:
            abort(404, 'Toko dengan id: {} tidak ditemukan.'.format(store_id))

    @staticmethod
    @requires_login
    @requires_admin
    def create(store: Dict):
        """Fungsi ini merespon API pada endpoint /api/v1.0/stores, yaitu dengan membuat toko berdasarkan parameter
        tertentu.
        @param store: Data mengenai toko yang hendak dibuat sesuai schema
        @return: 201 on success, 409 on store exists
        """
        nama_toko = store.get('nama_toko')
        existing_store = Store.get_by_name(nama_toko)

        # Can we insert this person?
        if existing_store is None:
            # Create a person instance using the schema and the passed-in person
            schema = StoreSchema()
            new_store = schema.load(store)

            # Add the person to the database
            new_store_ = Store(**new_store)
            new_store_.save_to_mongo()

            # Serialize and return the newly created person in the response
            data = new_store_.json()
            return data, 201

        # Otherwise, nope, person exists already
        else:
            abort(409, f'Toko dengan nama {nama_toko} sudah ada dalam database.')

    @staticmethod
    @requires_login
    @requires_admin
    def update(store_id: str, store: Dict):
        """Fungsi ini merespon API pada endpoint /api/v1.0/stores/{store_id}
        @param store_id: String id sebagai acuan pencarian toko pada database
        @param store: Data mengenai toko yang hendak diperbarui sesuai schema
        @return: 200 on success, 404 on not found, 409 on store exists
        """
        # Get the store requested from the db into session
        try:
            update_store = Store.get_by_id(store_id)
        except TypeError:
            update_store = None

        # Try to find an existing store with the same name as the update
        nama_toko = store.get("nama_toko")
        existing_store = Store.get_by_name(nama_toko)

        # Are we trying to find a store that does not exist?
        if update_store is None:
            abort(404, "Toko dengan id: {} tidak ditemukan.".format(store_id))

        # Would our update create a duplicate of another store already existing?
        elif existing_store is not None and existing_store._id != store_id:
            abort(409, "Toko dengan nama {} telah ada dalam database.".format(nama_toko))

        # Otherwise go ahead and update!
        else:
            # turn the passed in store into a db object
            schema = StoreSchema()
            update = schema.load(store)

            # Set the id to the store we want to update
            update['_id'] = update_store._id

            # merge the new object into the old and commit it to the db
            updated = Store(**update)
            updated.save_to_mongo()

            # return updated store in the response
            data = updated.json()
            return data, 200

    @staticmethod
    @requires_login
    @requires_admin
    def delete(store_id: str):
        """Fungsi ini merespon API pada endpoint /api/v1.0/stores/{store_id}, yaitu menghapus toko dengan store_id dari
        database.
        @param store_id: String id sebagai acuan pencarian toko pada database
        @return: 200 on success, 404 on not found
        """
        # Get the store requested
        try:
            store = Store.get_by_id(store_id)
        except TypeError:
            store = None

        # Did we find a store?
        if store is not None:
            store.remove_from_mongo()
            return make_response("Toko dengan id {} berhasil dihapus.".format(store_id), 200)

        # Otherwise, nope, didn't find that store
        else:
            abort(404, "Toko dengan id: {} tidak ditemukan.".format(store_id))

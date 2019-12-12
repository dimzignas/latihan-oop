# System modules
import uuid
import requests
from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Dict

# 3rd party modules
from flask import make_response, abort
from marshmallow import fields

# local modules
from config import ma
from models.user.user import requires_login


# from models.model import Model


class RecipeSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("resep_id", "nama_resep", "penulis", "timestamp", "tags", "bahan")

    bahan = fields.Nested("RecipeBahanSchema", default=[], many=True)


class RecipeBahanSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("bahan_id", "kuantitas", "nama_bahan", "resep_id", "satuan", "timestamp")


@dataclass(eq=False)
class Recipe(metaclass=ABCMeta):
    # collection = "stores"
    collection: str = field(init=False, default="stores")
    nama_resep: str
    penulis: str
    tags: str
    timestamp: str
    resep_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    data_resep_rizky = [
        {
            "bahan": [
                {
                    "bahan_id": 2,
                    "kuantitas": 2,
                    "nama_bahan": "Kelapa Muda",
                    "resep_id": 1,
                    "satuan": "butir",
                    "timestamp": "2019-12-12 05:20:22.428801"
                },
                {
                    "bahan_id": 23,
                    "kuantitas": 2,
                    "nama_bahan": "Kelapa Tua",
                    "resep_id": 1,
                    "satuan": "Butir",
                    "timestamp": "2019-12-12 01:03:31.220140"
                },
                {
                    "bahan_id": 22,
                    "kuantitas": 1,
                    "nama_bahan": "Gula",
                    "resep_id": 1,
                    "satuan": "gram",
                    "timestamp": "2019-12-11 16:07:33.135247"
                },
                {
                    "bahan_id": 1,
                    "kuantitas": 500,
                    "nama_bahan": "Daging sapi khas dalam",
                    "resep_id": 1,
                    "satuan": "gram",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 3,
                    "kuantitas": 2,
                    "nama_bahan": "Kecap Bango",
                    "resep_id": 1,
                    "satuan": "sdm",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 4,
                    "kuantitas": 1,
                    "nama_bahan": "Gula merah",
                    "resep_id": 1,
                    "satuan": "sdt",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 5,
                    "kuantitas": 3,
                    "nama_bahan": "Minyak sayur",
                    "resep_id": 1,
                    "satuan": "sdm",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 6,
                    "kuantitas": 750,
                    "nama_bahan": "Santan",
                    "resep_id": 1,
                    "satuan": "ml",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 7,
                    "kuantitas": 2,
                    "nama_bahan": "Garam",
                    "resep_id": 1,
                    "satuan": "sdt",
                    "timestamp": "2019-01-06 22:17:54"
                }
            ],
            "nama_resep": "Gulai sapi lemak",
            "penulis": "Wina",
            "resep_id": 1,
            "tags": "Masakan Hari Raya",
            "timestamp": "2019-12-12T05:20:54.667206"
        },
        {
            "bahan": [],
            "nama_resep": "Lontong Medan",
            "penulis": "Rizky",
            "resep_id": 4,
            "tags": "Sarapan",
            "timestamp": "2019-12-11T16:36:11.745253"
        },
        {
            "bahan": [
                {
                    "bahan_id": 8,
                    "kuantitas": 3,
                    "nama_bahan": "Kulit Lumpia",
                    "resep_id": 2,
                    "satuan": "lembar",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 9,
                    "kuantitas": 1,
                    "nama_bahan": "Minyak",
                    "resep_id": 2,
                    "satuan": "ml",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 10,
                    "kuantitas": 200,
                    "nama_bahan": "Daging sapi cincang",
                    "resep_id": 2,
                    "satuan": "gram",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 11,
                    "kuantitas": 3,
                    "nama_bahan": "Daun jeruk",
                    "resep_id": 2,
                    "satuan": "lembar",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 12,
                    "kuantitas": 1,
                    "nama_bahan": "Serai",
                    "resep_id": 2,
                    "satuan": "batang",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 13,
                    "kuantitas": 1,
                    "nama_bahan": "Royco kaldu sapi",
                    "resep_id": 2,
                    "satuan": "sdt",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 14,
                    "kuantitas": 2,
                    "nama_bahan": "Bawang daun",
                    "resep_id": 2,
                    "satuan": "batang",
                    "timestamp": "2019-01-06 22:17:54"
                }
            ],
            "nama_resep": "Martabak telur",
            "penulis": "Wina",
            "resep_id": 2,
            "tags": "Sarapan",
            "timestamp": "2019-12-11T08:17:06.947498"
        },
        {
            "bahan": [
                {
                    "bahan_id": 15,
                    "kuantitas": 1,
                    "nama_bahan": "Jagung manis",
                    "resep_id": 3,
                    "satuan": "kaleng",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 16,
                    "kuantitas": 1,
                    "nama_bahan": "Wortel",
                    "resep_id": 3,
                    "satuan": "buah",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 17,
                    "kuantitas": 2,
                    "nama_bahan": "Air",
                    "resep_id": 3,
                    "satuan": "liter",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 18,
                    "kuantitas": 2,
                    "nama_bahan": "Telur ukuran sedang",
                    "resep_id": 3,
                    "satuan": "butir",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 19,
                    "kuantitas": 1,
                    "nama_bahan": "Royco sup krim jagung",
                    "resep_id": 3,
                    "satuan": "bungkus",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 20,
                    "kuantitas": 2,
                    "nama_bahan": "Daun bawang",
                    "resep_id": 3,
                    "satuan": "batang",
                    "timestamp": "2019-01-06 22:17:54"
                },
                {
                    "bahan_id": 21,
                    "kuantitas": 1,
                    "nama_bahan": "Jagung manis cream",
                    "resep_id": 3,
                    "satuan": "kaleng",
                    "timestamp": "2019-01-06 22:17:54"
                }
            ],
            "nama_resep": "Sup krim jagung",
            "penulis": "Maddie",
            "resep_id": 3,
            "tags": "Sarapan",
            "timestamp": "2019-12-11T08:17:06.947498"
        }
    ]
    data_bahan_rizky = [
        {
            "bahan_id": 2,
            "kuantitas": 2,
            "nama_bahan": "Kelapa Muda",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "butir",
            "timestamp": "2019-12-12T05:20:22.428801"
        },
        {
            "bahan_id": 23,
            "kuantitas": 2,
            "nama_bahan": "Kelapa Tua",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "Butir",
            "timestamp": "2019-12-12T01:03:31.220140"
        },
        {
            "bahan_id": 22,
            "kuantitas": 1,
            "nama_bahan": "Gula",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "gram",
            "timestamp": "2019-12-11T16:07:33.135247"
        },
        {
            "bahan_id": 1,
            "kuantitas": 500,
            "nama_bahan": "Daging sapi khas dalam",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "gram",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 3,
            "kuantitas": 2,
            "nama_bahan": "Kecap Bango",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "sdm",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 4,
            "kuantitas": 1,
            "nama_bahan": "Gula merah",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "sdt",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 5,
            "kuantitas": 3,
            "nama_bahan": "Minyak sayur",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "sdm",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 6,
            "kuantitas": 750,
            "nama_bahan": "Santan",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "ml",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 7,
            "kuantitas": 2,
            "nama_bahan": "Garam",
            "resep": {
                "nama_resep": "Gulai sapi lemak",
                "penulis": "Wina",
                "resep_id": 1,
                "tags": "Masakan Hari Raya",
                "timestamp": "2019-12-12 05:20:54.667206"
            },
            "satuan": "sdt",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 8,
            "kuantitas": 3,
            "nama_bahan": "Kulit Lumpia",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "lembar",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 9,
            "kuantitas": 1,
            "nama_bahan": "Minyak",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "ml",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 10,
            "kuantitas": 200,
            "nama_bahan": "Daging sapi cincang",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "gram",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 11,
            "kuantitas": 3,
            "nama_bahan": "Daun jeruk",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "lembar",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 12,
            "kuantitas": 1,
            "nama_bahan": "Serai",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "batang",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 13,
            "kuantitas": 1,
            "nama_bahan": "Royco kaldu sapi",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "sdt",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 14,
            "kuantitas": 2,
            "nama_bahan": "Bawang daun",
            "resep": {
                "nama_resep": "Martabak telur",
                "penulis": "Wina",
                "resep_id": 2,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "batang",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 15,
            "kuantitas": 1,
            "nama_bahan": "Jagung manis",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "kaleng",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 16,
            "kuantitas": 1,
            "nama_bahan": "Wortel",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "buah",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 17,
            "kuantitas": 2,
            "nama_bahan": "Air",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "liter",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 18,
            "kuantitas": 2,
            "nama_bahan": "Telur ukuran sedang",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "butir",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 19,
            "kuantitas": 1,
            "nama_bahan": "Royco sup krim jagung",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "bungkus",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 20,
            "kuantitas": 2,
            "nama_bahan": "Daun bawang",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "batang",
            "timestamp": "2019-01-06T22:17:54"
        },
        {
            "bahan_id": 21,
            "kuantitas": 1,
            "nama_bahan": "Jagung manis cream",
            "resep": {
                "nama_resep": "Sup krim jagung",
                "penulis": "Maddie",
                "resep_id": 3,
                "tags": "Sarapan",
                "timestamp": "2019-12-11 08:17:06.947498"
            },
            "satuan": "kaleng",
            "timestamp": "2019-01-06T22:17:54"
        }
    ]

    def json(self) -> Dict:
        recipe_schema = RecipeSchema()
        return recipe_schema.dump(self)

    @staticmethod
    def call_api(url, param=None):
        r = requests.get(url, data=param)
        r.encoding = 'utf-8'
        data = r.json()
        return data

    @staticmethod
    def get_resep():
        # resep = Recipe.call_api('http://localhost:5000/api/resep')
        # return resep
        return Recipe.data_resep_rizky

    @staticmethod
    def get_bahan():
        # bahan = Recipe.call_api('http://localhost:5000/api/bahan')
        # return bahan
        return Recipe.data_bahan_rizky

    @staticmethod
    @requires_login
    def read_all():
        """
        This function responds to a request for /api/stores
        with the complete lists of stores
        :return:        json string of list of stores
        """
        # Create the list of stores from our data
        recipes = Recipe.call_api()

        # Deserialize the data for the response
        recipe_schema = RecipeSchema(many=True)
        data = recipe_schema.load(recipes)
        return data

    @staticmethod
    @requires_login
    def read_one():
        """
        This function responds to a request for /api/stores
        with the complete lists of stores
        :return:        json string of list of stores
        """
        # Create the list of stores from our data
        recipes = Recipe.call_api()

        # Serialize the data for the response
        recipe_schema = RecipeSchema(many=True)
        data = recipe_schema.dump(recipes)
        return data

    @staticmethod
    @requires_login
    def read_produk():
        # ambil resep dari API pihak ketiga
        recipes = Recipe.read_all()

        # Serialize the data for the response
        recipes_schema = RecipeSchema(many=True)
        data = recipes_schema.dump(recipes)
        return data

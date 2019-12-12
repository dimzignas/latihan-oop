from typing import Dict
import pymongo

__author__ = 'dimz'


class Database:
    URI = "mongodb://127.0.0.1:27017/webapi_db"
    # URI = "mongodb+srv://dimz:dimz010296@cluster0-ecovn.gcp.mongodb.net/test?retryWrites=true&w=majority"
    CLIENT = pymongo.MongoClient(URI)
    DATABASE = CLIENT.get_database()
    ASCENDING = pymongo.ASCENDING
    DESCENDING = pymongo.DESCENDING

    @staticmethod
    def insert(collection, data: Dict):
        """Memasukkan data ke database

        :param collection: nama collection
        :param data: data yang mau dimasukkan ke database
        """
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection: str, query: Dict, projecting: Dict = None) -> pymongo.cursor:
        """Mengembalikan semua data yang ditemukan dalam objek cursor

        @param collection: nama collection
        @param query: query pencarian
        @param projecting: kolom projecting
        """
        if projecting is None:
            return Database.DATABASE[collection].find(query)
        else:
            return Database.DATABASE[collection].find(query, projecting)

    @staticmethod
    def find_one(collection: str, query: Dict, projecting: Dict = None) -> Dict:
        """Mengembalikan data yang pertama kali ditemukan

        @param collection: nama collection
        @param query: query pencarian
        @param projecting: kolom projecting
        """
        if projecting is None:
            return Database.DATABASE[collection].find_one(query)
        else:
            return Database.DATABASE[collection].find_one(query, projecting)

    @staticmethod
    def update(collection: str, query: Dict, data: Dict) -> None:
        """Melakukan update berdasarkan query {'_id': <id>}
        Bila query tidak ditemukan, dilakukan insert data karena flag upsert=True

        @param collection: nama collection
        @param query: query pencarian
        @param data: data yang hendak di-update atau di-insert
        """
        Database.DATABASE[collection].update(query, data, upsert=True)

    @staticmethod
    def remove(collection: str, query: Dict) -> Dict:
        """Melakukan hapus records berdasarkan query pencarian yang diberikan

        @param collection: nama collection
        @param query: query pencarian
        """
        Database.DATABASE[collection].remove(query)

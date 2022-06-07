from pymongo import MongoClient

def query_cases(clinet: MongoClient, county_names: bool = True, state_names: bool = True):
    
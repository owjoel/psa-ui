import os
import sys

from pymongo import MongoClient, errors
from pymongo.database import Database
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import quote_plus

client: MongoClient
db: Database

def db_init():
    global client
    global collection
    host: str = os.getenv('MONGO_HOST')
    port: str = os.getenv('MONGO_PORT')
    username: str = os.getenv('MONGO_USERNAME')
    password: str = os.getenv('MONGO_PASSWORD')
    uri = "mongodb://%s:%s@%s:%s" % (
        quote_plus(username), quote_plus(password), quote_plus(host), quote_plus(port))
    try:
        client = MongoClient(uri)
        db = client['dev']
        collection = db['allocations']
        print(f"MongoDB client connected")
    except errors.ConnectionFailure:
        sys.exit(1)

class ShipType(Enum):
    CONTAINER = 0
    GENERAL_HEAVY_LIFT = 1
    TANKER = 2
    LNG_TANKER = 3
    LPG_TANKER = 4

class Shift(Enum):
    SHIFT_1 = 0  # 00:00 - 08:00
    SHIFT_2 = 1  # 08:00 - 16:00
    SHIFT_3 = 2  # 16:00 - 24:00

@dataclass
class ShipData:
    LAT: float
    LON: float
    SOG: float
    COG: float
    Heading: float
    Length: int
    Width: int
    Draft: float
    distanceToPort: float
    Ship_Type: ShipType
    Vessel_Max_Draft: float
    MaxDraft: float
    MaxLOA: float
    BerthLength: float
    ATA_inport: int
    ATA_berth_delay: float
    ATA_shift: Shift
    EDT_shift: Shift
    ATA_day_Friday: bool = False
    ATA_day_Monday: bool = False
    ATA_day_Saturday: bool = False
    ATA_day_Sunday: bool = False
    ATA_day_Thursday: bool = False
    ATA_day_Tuesday: bool = False
    ATA_day_Wednesday: bool = False
    EDT_day_Friday: bool = False
    EDT_day_Monday: bool = False
    EDT_day_Saturday: bool = False
    EDT_day_Sunday: bool = False
    EDT_day_Thursday: bool = False
    EDT_day_Tuesday: bool = False
    EDT_day_Wednesday: bool = False
    ATA_season_autumn: bool = False
    ATA_season_spring: bool = False
    ATA_season_summer: bool = False
    ATA_season_winter: bool = False
    EDT_season_autumn: bool = False
    EDT_season_spring: bool = False
    EDT_season_summer: bool = False
    EDT_season_winter: bool = False
    

    @classmethod
    def from_dict(cls, data: dict):
        """Converts json payload into ShipData object"""
        converted = {
            'Ship_Type': ShipType(data['Ship_Type']),
            'ATA_shift': Shift(data['ATA_shift']),
            'EDT_shift': Shift(data['EDT_shift']), 
        }
        other_fields = {k: v for k, v in data.items() if k not in converted}
        return cls(**converted, **other_fields)
    

    def to_dict(self):
        """Converts ShipData object back into a dictionary with basic types."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result

@dataclass
class IncomingShips:
    IMO: str
    Lat: float
    Long: float
    SOG: float
    COG: float
    Heading: float
    Draft: float
    distanceToPort: float
    ETA: datetime
    Berth_id: str

    def create(self):
        db.IncomingShips.insert_one(asdict(self))
    
    @staticmethod
    def get_by_imo(IMO):
        return db.IncomingShips.find_one({"IMO": IMO})

@dataclass
class Berth:
    id: int
    BerthLength: float
    MaxDraft: float
    MaxLOA: float
    Terminal_id: int
    EstimatedWaitTime: datetime
    UploadTime: datetime

    def create(self):
        db.Berth.insert_one(asdict(self))
    
    @staticmethod
    def get_by_id(id):
        return db.Berth.find_one({"id": id})

@dataclass
class DockedShips:
    IMO: str
    ATA: datetime
    ShipType: str
    ETD: datetime
    Berth_id: str
    MaxVesselDraft: float


    def create(self):
        db.DockedShips.insert_one(asdict(self))
    
    @staticmethod
    def get_by_imo(IMO):
        return db.DockedShips.find_one({"IMO": IMO})

@dataclass
class Terminal:
    id: int
    ship_count: int

    def create(self):
        db.Terminal.insert_one(asdict(self))
    
    @staticmethod
    def get_by_id(id):
        return db.Terminal.find_one({"id": id})
from typing import List, Optional
from .BusRoute import BusRoute
from .SeoulArrival import SeoulBusArrival
from .GyeonggiArrival import GyeonggiBusArrival
from .IncheonArrival import IncheonBusArrival


class BusRouteInfo:
    def __init__(self, **payload):
        self.name: str = payload['name']
        self.id: str = payload['id']
        self.type: str = payload['type']
        self.arrival_info: List[BusArrivalInfo] = [
            BusArrivalInfo(**x) for x in payload['arrival_info']
        ]

    @classmethod
    def from_seoul(cls, data: SeoulBusArrival):
        return cls(
            name=data.name,
            id=data.id,
            type="10" + format(data.bus_type, '02d'),
            arrival_info=[
                {
                    "type": getattr(data, "vehicle_type{0}".format(key)),
                    "time": getattr(data, "time{0}".format(key)),
                    "prev_count": getattr(data, "prev_count{0}".format(key)),
                    "prev_station": getattr(data, "now_station{0}".format(key)),
                    "is_full": getattr(data, "is_full{0}".format(key)),
                    "is_arrival": getattr(data, "is_arrive{0}".format(key))
                } for key in range(1, 3)
            ]
        )

    @classmethod
    def from_gyeonggi(cls, route: BusRoute, arrival: GyeonggiBusArrival):
        return cls(
            name=route.name,
            id=route.id,
            type="20" + format(route.type, '02d'),
            arrival_info=[
                {
                    "car_number": getattr(arrival, "car_number{0}".format(key), None),
                    "type": getattr(arrival, "vehicle_type{0}".format(key), None),
                    "time": (
                        getattr(arrival, "time{0}".format(key), None) * 60
                        if getattr(arrival, "time{0}".format(key), None) is not None
                        else None
                    ),
                    "seat": cls.convert_seat(
                        getattr(arrival, "seat{0}".format(key), None)
                    ),
                    "prev_count": getattr(arrival, "prev_count{0}".format(key), None),
                    "is_full": True if getattr(arrival, "is_full{0}".format(key), None) == 0 else False,
                    "is_arrival": getattr(arrival, "prev_count{0}".format(key)) <= 1
                    if isinstance(getattr(arrival, "prev_count{0}".format(key), None), int)
                    else False
                } for key in range(1, 3)
            ]
        )

    @classmethod
    def from_incheon(cls, route: BusRoute, arrival: List[IncheonBusArrival]):
        new_cls = cls(
            name=route.name,
            id=route.id,
            type="30" + format(route.type, '02d'),
            arrival_info=[]
        )
        new_cls.arrival_info = [
            BusArrivalInfo(**{
                "car_number": x.car_number,
                "congestion": x.congestion,
                "type": int(x.low_bus),
                "time": x.time,
                "seat": x.seat,
                "prev_count": x.prev_count,
                "prev_station": x.now_station,
                "is_full": True if x.seat == 0 else False,
                "is_arrival": x.prev_count <= 1
                if isinstance(x.prev_count, int)
                else False
            }) for x in arrival
        ]
        return new_cls

    @staticmethod
    def convert_seat(people: int) -> Optional[int]:
        if people == -1:
            return None
        return people

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "type": self.type,
            "arrivalInfo": [x.to_dict() for x in self.arrival_info]
        }


class BusArrivalInfo:
    def __init__(self, **payload):
        self.type: int = payload['type']
        self.prev_count: int = payload['prev_count']
        self.time: int = payload['time']
        self.seat: Optional[int] = payload.get('seat')
        self.prev_station: Optional[str] = payload.get('prev_station')
        self.congestion: Optional[int] = payload.get('congestion')
        self.car_number: Optional[str] = payload.get('car_number')
        self.is_full: Optional[bool] = payload.get('is_full')
        self.is_arrival: Optional[bool] = payload.get('is_arrival')

    def to_dict(self) -> dict:
        return {
            "congestion": self.congestion,
            "carNumber": self.car_number,
            "lowBus": bool(self.type),
            "time": self.time,
            "seat": self.seat,
            "isFull": self.is_full,
            "isArrival": self.is_arrival,
            "prevCount": self.prev_count
        }

from app.modules.baseClient import BaseClient
from .models.BusStation import BusStation
from .models.BusRoute import BusRoute
from .models.BusStationAround import BusStationAround
from app.modules.errors import *
from app.utils import get_list_from_ordered_dict


class KoreaBIS(BaseClient):
    def __init__(self, token: str):
        super().__init__("http://apis.data.go.kr")
        self.token = token

    def request(self, **kwargs):
        params = {
            'serviceKey': self.token
        }
        return super(KoreaBIS, self).request(_default_params=params, _default_xml=False, **kwargs)

    def get_station(self, name: str, city_code: int):
        data = self.get(
            path="/1613000/BusSttnInfoInqireService/getSttnNoList",
            params={
                "pageNo": 1,
                "numOfRows": 100,
                "nodeNm": name,
                "cityCode": city_code,
                "_type": "json"
            }
        )
        result = data['response']

        # HEAD AND BODY
        head = result['header']
        body = result['body']['items']
        if body == '' or body is None:
            raise EmptyData()

        item_list = body['item']
        return [BusStation.from_korea(x, city_code) for x in get_list_from_ordered_dict(item_list)]

import json
from asyncio import sleep
from .models import SalesByCardType
import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChartsConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_sales_by_card_type(self):
        max_batch_no = SalesByCardType.objects.values('batch_no').order_by('-batch_no').first()
        print("Printing max_batch_no: ")
        print(max_batch_no)
        print(max_batch_no['batch_no'])
        queryset = SalesByCardType.objects.all().filter(batch_no=max_batch_no['batch_no'])

        labels = []
        sales_data = []

        for salesByCardType in queryset:
            labels.append(salesByCardType.card_type)
            sales_data.append(salesByCardType.total_sales)

        current_refresh_time = 'Current Refresh Time: {date:%Y-%m-%d %H:%M:%S}'.format(date=datetime.datetime.now())
        charts_data = {
            "labels": labels,
            "sales_data": sales_data,
            "current_refresh_time": current_refresh_time
        }

        return charts_data

    async def connect(self):
        await self.accept()

        while True:
            charts_data = await self.get_sales_by_card_type()
            #print("charts_data")
            #print(charts_data)
            await self.send(json.dumps(charts_data))
            await sleep(5)

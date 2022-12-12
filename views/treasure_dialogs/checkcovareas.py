import json
import os.path

import flet as ft
import pdf2docx

from utils import snack_bar, DESKTOP
from views.treasure_dialogs.base import BaseDialog
from methods.getcovareas import get_risk_area_data


class Dialog(BaseDialog):
    def __init__(self):
        self.province_dd = ft.Dropdown(
            options=[],
            width=200,
            height=40,
            content_padding=5,
            on_change=lambda e: self.change_province_event(e.data),
        )
        self.city_dd = ft.Dropdown(
            options=[],
            width=200,
            height=40,
            content_padding=5,
            on_change=lambda e: self.change_city_event(e.data),
        )
        self.county_dd = ft.Dropdown(
            options=[],
            width=200,
            height=40,
            content_padding=5,
            on_change=lambda e: self.change_county_event(e.data),
        )
        self.select_component = ft.Row([self.province_dd, self.city_dd, self.county_dd])
        self.title_text = ft.Text()

        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("名称")), ft.DataColumn(ft.Text("风险等级"))], width=600
        )
        self.close_btn = ft.IconButton(
            icon=ft.icons.CLOSE_OUTLINED, on_click=self.close_dlg
        )
        self.area_data = {}
        self.end_update_time = ""
        super(Dialog, self).__init__(
            title=ft.Text("高风险地区实时查询"),
            content=ft.Stack(
                [ft.Column([self.select_component, self.title_text, ft.ListView([self.data_table], height=400)])],
                width=700,
                expand=True,
            ),
            content_padding=20,
            actions=[self.close_btn],
            actions_alignment="center",
        )

    def open_dlg(self, e):
        super().open_dlg(e)
        data = get_risk_area_data()
        if data[1] != 200:
            self.title_text.value = "抱歉，查询接口出错！"
        else:
            self.format_data(data[0])
            self.title_text.value = self.end_update_time
            provinces = list(self.area_data.keys())
            self.province_dd.options.extend([ft.dropdown.Option(i) for i in provinces])
            self.province_dd.value = provinces[0]
            self.change_province_event(provinces[0])
        self.update()

    def format_data(self, data):
        # province-> city-> county-> communitys ->level

        self.end_update_time = data["data"]["end_update_time"]
        details = data["data"]
        mark = {"highlist": "高风险区域", "middlelist": "中风险区域", "lowlist": "低风险区域"}
        for list_name, level in mark.items():
            for h in details[list_name]:
                if h["province"] not in self.area_data:
                    self.area_data[h["province"]] = {}
                province = self.area_data[h["province"]]
                if h["city"] not in province:
                    province[h["city"]] = {}
                city = province[h["city"]]
                if h["county"] not in city:
                    city[h["county"]] = {}
                county = city[h["county"]]
                for community in h["communitys"]:
                    county[community] = level

    def change_province_event(self, province):
        self.province_dd.value = province
        cities = list(self.area_data[province].keys())
        self.city_dd.options.clear()
        self.city_dd.options.extend([ft.dropdown.Option(i) for i in cities])
        self.change_city_event(cities[0])

    def change_city_event(self, city):
        self.city_dd.value = city
        province = self.province_dd.value
        counties = list(self.area_data[province][city].keys())
        self.county_dd.options.clear()
        self.county_dd.options.extend([ft.dropdown.Option(i) for i in counties])
        self.change_county_event(counties[0])

    def change_county_event(self, county):
        self.county_dd.value = county
        province = self.province_dd.value
        city = self.city_dd.value
        self.data_table.rows.clear()
        for position, level in self.area_data[province][city][county].items():
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(position, width=400, overflow="clip")),
                    ft.DataCell(ft.Text(level))
                ]
            )
            if level == "高风险区域":
                row.color = ft.colors.RED_50
            elif level == "中风险区域":
                row.color = ft.colors.PINK_50
            elif level == "低风险区域":
                row.color = ft.colors.YELLOW_50
            self.data_table.rows.append(row)

        self.update()

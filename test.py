import flet as ft


def main(page: ft.Page):
    page.add(ft.ListView(
        [ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("First name")),
                ft.DataColumn(ft.Text("Last name")),
                ft.DataColumn(ft.Text("Age"), numeric=True),
            ],
            rows=[
                     ft.DataRow(
                         cells=[
                             ft.DataCell(ft.Text("John")),
                             ft.DataCell(ft.Text("Smith")),
                             ft.DataCell(ft.Text("43")),
                         ],
                     ),
                     ft.DataRow(
                         cells=[
                             ft.DataCell(ft.Text("Jack")),
                             ft.DataCell(ft.Text("Brown")),
                             ft.DataCell(ft.Text("19")),
                         ],
                     ),
                     ft.DataRow(
                         cells=[
                             ft.DataCell(ft.Text("Alice")),
                             ft.DataCell(ft.Text("Wong")),
                             ft.DataCell(ft.Text("25")),
                         ],
                     ),
                 ] * 20,

        )],height=200)
    )


ft.app(target=main)

import flet as ft

def main(page: ft.Page):
    page.bgcolor = "white"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.add(
        ft.Text("مرحباً! محرك التطبيق يعمل بنجاح!", size=25, color="black", weight="bold")
    )

ft.app(target=main)

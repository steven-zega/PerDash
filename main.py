APP_VERSION = "1.0.0"

import flet as ft
from database import load_data
from modules.todo import build_todo
from modules.links import build_links
from modules.vault import build_vault

def main(page: ft.Page):
    # 1. Konfigurasi Jendela Utama
    page.title = "Personal Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1000
    page.window.height = 650

    app_data = load_data()

    # Container Utama (Area Konten Kanan)
    content_area = ft.Container(
        content=build_todo(page, app_data),
        expand=True,
        padding=25
    )

    # Switcher Menu
    def on_nav_change(e):
        selected_idx = e.control.selected_index
        if selected_idx == 0:
            content_area.content = build_todo(page, app_data)
        elif selected_idx == 1:
            content_area.content = build_links(page, app_data)
        elif selected_idx == 2:
            content_area.content = build_vault(page, app_data)
        
        page.update()

    # Sidebar
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=90,
        min_extended_width=180,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CHECK_BOX_OUTLINED,
                selected_icon=ft.Icons.CHECK_BOX,
                label="To-Do List",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LINK_OUTLINED,
                selected_icon=ft.Icons.LINK,
                label="Link",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOCK_OUTLINE,
                selected_icon=ft.Icons.LOCK,
                label="Password",
            ),
        ],
        on_change=on_nav_change,
    )

    # Layout Utama
    layout = ft.Row(
        [
            sidebar,
            ft.VerticalDivider(width=1),
            content_area,
        ],
        expand=True,
    )

    page.add(layout)

# Jalankan Aplikasi
ft.run(main)
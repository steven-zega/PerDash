APP_VERSION = "1.0.3"

import flet as ft
import threading
import time
import os
import platform
from database import load_data, save_data

from modules.todo import build_todo
from modules.links import build_links
from modules.vault import build_vault
from modules.notes import build_notes

from modules.mobile.todo_mobile import build_todo_mobile
from modules.mobile.links_mobile import build_links_mobile
from modules.mobile.vault_mobile import build_vault_mobile
from modules.mobile.notes_mobile import build_notes_mobile

def main(page: ft.Page):
    page.assets_dir = "assets"
    
    page.title = "PerDash"
    page.padding = 0
    page.window.width = 1000
    page.window.height = 650

    try:
        if platform.system() == "Windows":
            icon_path = os.path.join(os.path.dirname(__file__), "PerDash.ico")
            if os.path.exists(icon_path):
                page.window.icon = icon_path
    except Exception:
        pass

    app_data = load_data()

    saved_theme = app_data.get("theme_mode", "dark")
    page.theme_mode = ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.DARK_MODE
            theme_btn.tooltip = "Switch to Dark Mode"
            app_data["theme_mode"] = "light"
        else:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.LIGHT_MODE
            theme_btn.tooltip = "Switch to Light Mode"
            app_data["theme_mode"] = "dark"
        
        save_data(app_data)
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE,
        tooltip="Switch Mode",
        on_click=toggle_theme
    )

    current_idx = [0]
    current_is_mobile = [None]

    def get_content(idx, is_mob):
        if idx == 0:
            return build_todo_mobile(page, app_data) if is_mob else build_todo(page, app_data)
        elif idx == 1:
            return build_links_mobile(page, app_data) if is_mob else build_links(page, app_data)
        elif idx == 2:
            return build_vault_mobile(page, app_data) if is_mob else build_vault(page, app_data)
        elif idx == 3:
            return build_notes_mobile(page, app_data) if is_mob else build_notes(page, app_data)
        return build_todo_mobile(page, app_data) if is_mob else build_todo(page, app_data)

    content_area = ft.Container(
        expand=True,
        padding=10
    )

    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=140,
        group_alignment=-1.0,
        expand=True,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.CHECK_BOX_OUTLINED, selected_icon=ft.Icons.CHECK_BOX, label="To-Do"),
            ft.NavigationRailDestination(icon=ft.Icons.LINK_OUTLINED, selected_icon=ft.Icons.LINK, label="Link"),
            ft.NavigationRailDestination(icon=ft.Icons.LOCK_OUTLINE, selected_icon=ft.Icons.LOCK, label="Password"),
            ft.NavigationRailDestination(icon=ft.Icons.STICKY_NOTE_2_OUTLINED, selected_icon=ft.Icons.STICKY_NOTE_2, label="Notes"),
        ],
        on_change=lambda e: on_nav_change(e.control.selected_index),
    )

    left_sidebar = ft.Container(
        content=ft.Column(
            [
                sidebar,
                ft.Container(
                    content=theme_btn,
                    padding=ft.Padding(0, 0, 0, 10),
                    alignment=ft.Alignment(0, 1)
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=85,
        padding=ft.Padding(0, 15, 0, 0)
    )

    bottom_nav = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CHECK_BOX_OUTLINED, selected_icon=ft.Icons.CHECK_BOX, label="To-Do"),
            ft.NavigationBarDestination(icon=ft.Icons.LINK_OUTLINED, selected_icon=ft.Icons.LINK, label="Link"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCK_OUTLINE, selected_icon=ft.Icons.LOCK, label="Password"),
            ft.NavigationBarDestination(icon=ft.Icons.STICKY_NOTE_2_OUTLINED, selected_icon=ft.Icons.STICKY_NOTE_2, label="Notes"),
        ],
        on_change=lambda e: on_nav_change(e.control.selected_index)
    )

    mobile_header = ft.Container(
        content=ft.Row(
            [
                ft.Text("PerDash", size=16, weight=ft.FontWeight.BOLD),
                theme_btn
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding(12, 6, 12, 0),
        visible=False
    )

    divider = ft.VerticalDivider(width=1)
    main_layout = ft.Column([], expand=True)

    def on_nav_change(selected_idx):
        current_idx[0] = selected_idx
        sidebar.selected_index = selected_idx
        bottom_nav.selected_index = selected_idx
        is_mob = current_is_mobile[0] if current_is_mobile[0] is not None else False
        content_area.content = get_content(selected_idx, is_mob)
        page.update()

    def update_layout(is_mob):
        if is_mob:
            left_sidebar.visible = False
            divider.visible = False
            mobile_header.visible = True
            bottom_nav.visible = True
            content_area.padding = 6
            main_layout.controls = [
                mobile_header,
                content_area,
                bottom_nav
            ]
        else:
            left_sidebar.visible = True
            divider.visible = True
            mobile_header.visible = False
            bottom_nav.visible = False
            content_area.padding = 15
            main_layout.controls = [
                ft.Row(
                    [
                        left_sidebar,
                        divider,
                        content_area,
                    ],
                    expand=True,
                )
            ]

        content_area.content = get_content(current_idx[0], is_mob)
        page.update()

    def auto_check_size():
        while True:
            try:
                w = page.width or (page.window.width if page.window else 0)
                
                is_mob = w < 650 if w > 0 else False

                if current_is_mobile[0] != is_mob:
                    current_is_mobile[0] = is_mob
                    update_layout(is_mob)

            except Exception:
                pass
            
            time.sleep(0.2)

    page.add(main_layout)

    threading.Thread(target=auto_check_size, daemon=True).start()

ft.app(target=main)
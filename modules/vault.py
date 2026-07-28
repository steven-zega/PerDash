import subprocess
import platform
import threading
import flet as ft
from database import save_data

def copy_to_clipboard(text: str):
    try:
        if platform.system() == "Windows":
            subprocess.run("clip", input=text.encode("utf-16"), check=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run("pbcopy", input=text.encode("utf-8"), check=True)
        else:  # Linux
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=True)
    except Exception:
        pass

def build_vault(page: ft.Page, app_data: dict):
    passwords = app_data.get("passwords", [])

    service_input = ft.TextField(hint_text="Name / Title...", expand=True, border_color="white")
    user_input = ft.TextField(hint_text="Username / Email", expand=True, border_color="white")
    pass_input = ft.TextField(
        hint_text="Password",
        password=True,
        can_reveal_password=True,
        expand=True,
        border_color="white"
    )

    vault_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def render_passwords():
        vault_column.controls.clear()
        if not passwords:
            vault_column.controls.append(
                ft.Container(
                    content=ft.Text("No passwords saved", color="white54", italic=True),
                    padding=20
                )
            )
        else:
            for item in passwords:
                action_row = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

                # Fungsi pembuat tombol salin
                def make_copy_btn(vault_item, row_ref):
                    def on_copy(e):
                        copy_to_clipboard(vault_item["password"])

                        copied_label = ft.Container(
                            content=ft.Row([
                                ft.Text("Copied!", color="green400", size=12, weight=ft.FontWeight.BOLD)
                            ], spacing=3),
                            padding=8
                        )

                        row_ref.controls[0] = copied_label
                        page.update()

                        def reset():
                            try:
                                row_ref.controls[0] = make_copy_btn(vault_item, row_ref)
                                page.update()
                            except Exception:
                                pass  

                        threading.Timer(2.0, reset).start()

                    return ft.IconButton(
                        icon=ft.Icons.COPY,
                        icon_color="green400",
                        tooltip="Copy Password",
                        on_click=on_copy
                    )

                def make_delete_handler(vault_item):
                    return lambda e: delete_password(vault_item)

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    tooltip="Delete",
                    on_click=make_delete_handler(item)
                )

                copy_btn = make_copy_btn(item, action_row)
                action_row.controls = [copy_btn, del_btn]

                card_content = ft.Row([
                    ft.Column([
                        ft.Text(item["service"], weight=ft.FontWeight.BOLD, size=15),
                        ft.Text(f"👤 {item['username']}", color="white70", size=13),
                        ft.Text("🔑 ••••••••", color="white54", size=12)
                    ], expand=True, spacing=2),
                    action_row
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

                card = ft.Container(
                    content=card_content,
                    padding=12,
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                vault_column.controls.append(card)

        page.update()

    def add_password(e):
        if not service_input.value.strip() or not pass_input.value.strip():
            return

        new_item = {
            "service": service_input.value.strip(),
            "username": user_input.value.strip(),
            "password": pass_input.value.strip()
        }
        passwords.append(new_item)
        app_data["passwords"] = passwords
        save_data(app_data)

        service_input.value = ""
        user_input.value = ""
        pass_input.value = ""
        render_passwords()

    def delete_password(vault_item):
        passwords.remove(vault_item)
        app_data["passwords"] = passwords
        save_data(app_data)
        render_passwords()

    add_btn = ft.ElevatedButton(
        "Add",
        icon=ft.Icons.ADD,
        on_click=add_password
    )

    form_layout = ft.Column([
        ft.Row([service_input, user_input]),
        ft.Row([pass_input, add_btn])
    ], spacing=10)

    render_passwords()

    return ft.Column([
        ft.Text("Password", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        form_layout,
        ft.Divider(height=10),
        vault_column
    ], expand=True)
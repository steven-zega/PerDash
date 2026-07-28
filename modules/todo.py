import flet as ft
from database import save_data

def build_todo(page: ft.Page, app_data: dict):
    todos = app_data.get("todos", [])

    task_input = ft.TextField(
        hint_text="Activity...",
        expand=True,
        autofocus=True,
        border_color="white"
    )
    date_input = ft.TextField(
        hint_text="Date",
        width=240,
        border_color="white"
    )

    todo_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def render_todos():
        todo_list_column.controls.clear()
        if not todos:
            todo_list_column.controls.append(
                ft.Container(
                    content=ft.Text("No activities", color="white54", italic=True),
                    padding=20
                )
            )
        else:
            for item in todos:
                def make_checkbox_handler(todo_item):
                    return lambda e: toggle_todo(todo_item, e.control.value)

                def make_delete_handler(todo_item):
                    return lambda e: delete_todo(todo_item)

                display_text = f"{item['task']}   —   {item['date']}" if item.get('date') else item['task']

                chk = ft.Checkbox(
                    label=display_text,
                    value=item.get("completed", False),
                    on_change=make_checkbox_handler(item),
                    expand=True
                )
                
                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    tooltip="Delete",
                    on_click=make_delete_handler(item)
                )

                card = ft.Container(
                    content=ft.Row([chk, del_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                todo_list_column.controls.append(card)
        
        page.update()

    def add_todo(e):
        if not task_input.value.strip():
            return
        
        new_item = {
            "task": task_input.value.strip(),
            "date": date_input.value.strip(),
            "completed": False
        }
        todos.append(new_item)
        app_data["todos"] = todos
        save_data(app_data)

        task_input.value = ""
        date_input.value = ""
        render_todos()

    def toggle_todo(todo_item, value):
        todo_item["completed"] = value
        app_data["todos"] = todos
        save_data(app_data)
        render_todos()

    def delete_todo(todo_item):
        todos.remove(todo_item)
        app_data["todos"] = todos
        save_data(app_data)
        render_todos()

    add_btn = ft.ElevatedButton(
        "Add",
        icon=ft.Icons.ADD,
        on_click=add_todo
    )

    form_row = ft.Row([task_input, date_input, add_btn], spacing=10)

    render_todos()

    return ft.Column([
        ft.Text("To-Do List", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        form_row,
        ft.Divider(height=10),
        todo_list_column
    ], expand=True)
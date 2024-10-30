from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const
from .admin_states import AddRefLinkSG
ref_links_add_dialog = Dialog(
    Window(
        Const("Введите имя новой ссылки:"),
        TextInput(id="link_name",),
        Cancel(Const("В меню")),
        state=AddRefLinkSG.get_link
    ),
)

"""Страница профиля пользователя — Aigocy Style."""

import reflex as rx

from app.components.navbar import navbar
from app.pages.index import _footer
from app.state import AppState
from app.states.user import UserState
from app.states.vehicle import VehicleState


# -- vehicle card -------------------------------------------------------------

def _vehicle_card(v: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.i(
                    class_name="bi bi-car-front-fill",
                    style={"font-size": "1.6rem", "color": "var(--ag-red)", "flex-shrink": "0"},
                ),
                rx.el.div(
                    rx.el.div(
                        v["brand"], " ", v["model"],
                        style={"font-weight": "700", "font-size": "1rem"},
                    ),
                    rx.el.div(
                        rx.cond(v["year"], v["year"].to_string() + " г. · ", ""),
                        v["engine_type"], " · ", v["transmission"],
                        style={"font-size": ".82rem", "color": "var(--ag-gray)", "margin-top": ".2rem"},
                    ),
                    rx.cond(
                        v["license_plate"] != "",
                        rx.el.div(
                            rx.el.i(class_name="bi bi-tag me-1"),
                            v["license_plate"],
                            style={"font-size": ".8rem", "color": "var(--ag-gray)", "margin-top": ".2rem"},
                        ),
                    ),
                ),
                style={"display": "flex", "align-items": "flex-start", "gap": "1rem", "flex": "1"},
            ),
            rx.el.button(
                rx.el.i(class_name="bi bi-trash"),
                on_click=VehicleState.delete_vehicle(v["id"].to_string()),
                class_name="btn btn-sm btn-outline-danger",
                title="Удалить",
                style={"flex-shrink": "0"},
            ),
            style={"display": "flex", "justify-content": "space-between", "align-items": "flex-start", "gap": "1rem"},
        ),
        class_name="ag-card mb-3",
    )


# -- add vehicle form ---------------------------------------------------------

def _add_vehicle_form() -> rx.Component:
    return rx.cond(
        VehicleState.add_form_open,
        rx.el.div(
            rx.el.h6("Новый автомобиль", style={"font-weight": "800", "margin-bottom": "1.25rem"}),
            # VIN lookup block
            rx.el.div(
                rx.el.label("Найти по VIN", class_name="ag-form-label"),
                rx.el.div(
                    rx.el.input(
                        placeholder="17 символов, например JTMBR3FV8FD034123",
                        value=VehicleState.vin_raw,
                        on_change=VehicleState.set_vin_raw,
                        on_key_up=rx.cond(
                            VehicleState.vin_raw.length() == 17,
                            VehicleState.lookup_vin(),
                            rx.noop(),
                        ),
                        class_name="ag-form-control",
                        style={"font-family": "monospace", "text-transform": "uppercase", "flex": "1"},
                        max_length=17,
                    ),
                    rx.el.button(
                        rx.cond(VehicleState.vin_loading, "...", "Декодировать"),
                        on_click=VehicleState.lookup_vin,
                        class_name="ag-btn-dark",
                        type="button",
                        style={"white-space": "nowrap"},
                    ),
                    style={"display": "flex", "gap": ".75rem", "align-items": "flex-end"},
                ),
                rx.cond(
                    VehicleState.vin_hint != "",
                    rx.el.div(
                        rx.el.i(class_name="bi bi-check-circle-fill me-1", style={"color": "green"}),
                        VehicleState.vin_hint,
                        style={"font-size": ".85rem", "color": "green", "margin-top": ".4rem"},
                    ),
                ),
                rx.cond(
                    VehicleState.vin_image_url != "",
                    rx.el.img(
                        src=VehicleState.vin_image_url,
                        alt="Фото автомобиля",
                        style={
                            "max-width": "100%",
                            "max-height": "180px",
                            "object-fit": "cover",
                            "border-radius": "8px",
                            "margin-top": ".75rem",
                            "display": "block",
                        },
                    ),
                ),
                rx.cond(
                    VehicleState.vin_error != "",
                    rx.el.div(
                        rx.el.i(class_name="bi bi-exclamation-circle me-1"),
                        VehicleState.vin_error,
                        class_name="ag-form-error",
                        style={"margin-top": ".4rem"},
                    ),
                ),
                class_name="ag-form-group",
                style={"background": "#f8f8f8", "border-radius": "8px", "padding": "1rem", "margin-bottom": "1.25rem"},
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label("Марка", class_name="ag-form-label"),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Выберите марку",
                            style={"width": "100%"},
                        ),
                        rx.select.content(
                            rx.foreach(
                                VehicleState.brands,
                                lambda b: rx.select.item(b["name"], value=b["name"]),
                            ),
                        ),
                        value=VehicleState.new_brand,
                        on_change=VehicleState.on_brand_change,
                        size="2",
                    ),
                    class_name="ag-form-group col-12 col-sm-6",
                ),
                rx.el.div(
                    rx.el.label("Модель", class_name="ag-form-label"),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder=rx.cond(
                                VehicleState.new_brand != "",
                                "Выберите модель",
                                "Сначала выберите марку",
                            ),
                            style={"width": "100%"},
                        ),
                        rx.select.content(
                            rx.foreach(
                                VehicleState.models_list,
                                lambda m: rx.select.item(m["name"], value=m["name"]),
                            ),
                        ),
                        value=VehicleState.new_model,
                        on_change=VehicleState.set_new_model,
                        disabled=VehicleState.new_brand == "",
                        size="2",
                    ),
                    class_name="ag-form-group col-12 col-sm-6",
                ),
                rx.el.div(
                    rx.el.label("Год выпуска", class_name="ag-form-label"),
                    rx.el.input(
                        placeholder="2020",
                        value=VehicleState.new_year,
                        on_change=VehicleState.set_new_year,
                        type="number",
                        class_name="ag-form-control",
                    ),
                    class_name="ag-form-group col-12 col-sm-6",
                ),
                rx.el.div(
                    rx.el.label("Гос. номер", class_name="ag-form-label"),
                    rx.el.input(
                        placeholder="А001АА177",
                        value=VehicleState.new_license_plate,
                        on_change=VehicleState.set_new_license_plate,
                        class_name="ag-form-control",
                    ),
                    class_name="ag-form-group col-12 col-sm-6",
                ),
                rx.el.div(
                    rx.el.label("Тип двигателя", class_name="ag-form-label"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Двигатель"),
                        rx.select.content(
                            rx.select.item("Бензин", value="gasoline"),
                            rx.select.item("Дизель", value="diesel"),
                            rx.select.item("Электро", value="electric"),
                            rx.select.item("Гибрид", value="hybrid"),
                            rx.select.item("Газ (LPG)", value="gas"),
                        ),
                        value=VehicleState.new_engine_type,
                        on_change=VehicleState.set_new_engine_type,
                        size="2",
                    ),
                    class_name="ag-form-group col-12 col-sm-6",
                ),
                rx.el.div(
                    rx.el.label("Коробка передач", class_name="ag-form-label"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Коробка"),
                        rx.select.content(
                            rx.select.item("Автомат", value="automatic"),
                            rx.select.item("Механика", value="manual"),
                            rx.select.item("Робот", value="robot"),
                            rx.select.item("Вариатор", value="cvt"),
                        ),
                        value=VehicleState.new_transmission,
                        on_change=VehicleState.set_new_transmission,
                        size="2",
                    ),
                    class_name="ag-form-group col-12 col-sm-6",
                ),
                class_name="row g-3",
            ),
            rx.cond(
                VehicleState.new_error != "",
                rx.el.div(
                    rx.el.i(class_name="bi bi-exclamation-circle me-1"),
                    VehicleState.new_error,
                    class_name="ag-form-error mt-2",
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.cond(VehicleState.new_loading, "Добавляем...", "Добавить"),
                    on_click=VehicleState.add_vehicle,
                    class_name="ag-btn-dark",
                    type="button",
                ),
                rx.el.button(
                    "Отмена",
                    on_click=VehicleState.set_add_form_open(False),
                    class_name="ag-btn-outline",
                    type="button",
                ),
                class_name="d-flex gap-2 mt-3",
            ),
            class_name="ag-card mt-3",
        ),
    )


# -- tab: профиль -------------------------------------------------------------

def _tab_profile() -> rx.Component:
    return rx.el.div(
        rx.el.h5("Редактировать профиль", style={"font-weight": "800", "margin-bottom": "1.5rem"}),
        rx.el.div(
            rx.el.label("Имя", class_name="ag-form-label"),
            rx.el.input(
                placeholder="Ваше имя",
                value=UserState.edit_name,
                on_change=UserState.set_edit_name,
                class_name="ag-form-control",
            ),
            class_name="ag-form-group",
        ),
        rx.el.div(
            rx.el.label("Email", class_name="ag-form-label"),
            rx.el.input(
                placeholder="example@mail.com",
                value=UserState.edit_email,
                on_change=UserState.set_edit_email,
                type="email",
                class_name="ag-form-control",
            ),
            class_name="ag-form-group",
        ),
        rx.cond(
            UserState.profile_error != "",
            rx.el.div(
                rx.el.i(class_name="bi bi-exclamation-circle me-1"),
                UserState.profile_error,
                class_name="ag-form-error mb-3",
            ),
        ),
        rx.cond(
            UserState.profile_saved,
            rx.el.div(
                rx.el.i(class_name="bi bi-check-circle me-1"),
                "Профиль сохранён!",
                style={"color": "green", "font-size": ".9rem", "margin-bottom": "1rem"},
            ),
        ),
        rx.el.button(
            rx.cond(UserState.profile_loading, "Сохраняем...", "Сохранить изменения"),
            on_click=UserState.save_profile,
            class_name="ag-btn-dark",
            type="button",
        ),
    )


# -- tab: гараж ---------------------------------------------------------------

def _tab_garage() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h5(
                rx.el.i(class_name="bi bi-car-front me-2"),
                "Мой гараж",
                style={"font-weight": "800", "margin": "0"},
            ),
            rx.cond(
                ~VehicleState.add_form_open,
                rx.el.button(
                    rx.el.i(class_name="bi bi-plus-lg me-1"),
                    "Добавить авто",
                    on_click=VehicleState.open_add_form,
                    class_name="ag-btn-dark",
                    type="button",
                ),
            ),
            style={"display": "flex", "justify-content": "space-between", "align-items": "center", "margin-bottom": "1.5rem"},
        ),
        _add_vehicle_form(),
        rx.cond(
            VehicleState.vehicles_loading,
            rx.el.div(
                rx.el.div(class_name="spinner-border text-secondary"),
                style={"text-align": "center", "padding": "3rem 0"},
            ),
            rx.cond(
                VehicleState.vehicles,
                rx.foreach(VehicleState.vehicles, _vehicle_card),
                rx.cond(
                    ~VehicleState.add_form_open,
                    rx.el.div(
                        rx.el.i(
                            class_name="bi bi-car-front",
                            style={"font-size": "3rem", "color": "var(--ag-light)"},
                        ),
                        rx.el.p(
                            "В вашем гараже пока нет автомобилей",
                            style={"color": "var(--ag-gray)", "margin-top": "1rem"},
                        ),
                        rx.el.p(
                            "Добавьте первый автомобиль, чтобы быстро находить подходящие услуги",
                            style={"color": "var(--ag-light)", "font-size": ".88rem"},
                        ),
                        style={"text-align": "center", "padding": "3rem 0"},
                    ),
                ),
            ),
        ),
    )


# -- tab: уведомления ---------------------------------------------------------

def _notification_item(n: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.i(
                class_name=rx.cond(n["is_read"], "bi bi-bell", "bi bi-bell-fill"),
                style={
                    "color": rx.cond(n["is_read"], "var(--ag-gray)", "var(--ag-red)"),
                    "font-size": "1.1rem",
                    "flex-shrink": "0",
                },
            ),
            rx.el.div(
                rx.el.div(
                    n["title"],
                    style={"font-weight": rx.cond(n["is_read"], "500", "700"), "font-size": ".95rem"},
                ),
                rx.el.div(
                    n["body"],
                    style={"font-size": ".85rem", "color": "var(--ag-gray)", "margin-top": ".2rem"},
                ),
            ),
            style={"display": "flex", "gap": "1rem", "align-items": "flex-start"},
        ),
        style={
            "padding": "1rem 1.25rem",
            "border-bottom": "1px solid var(--ag-border)",
            "background": rx.cond(n["is_read"], "white", "#fff8f8"),
        },
    )


def _tab_notifications() -> rx.Component:
    return rx.el.div(
        rx.el.h5("Уведомления", style={"font-weight": "800", "margin-bottom": "1.25rem"}),
        rx.cond(
            UserState.notifications,
            rx.el.div(
                rx.foreach(UserState.notifications, _notification_item),
                style={"border": "1px solid var(--ag-border)", "border-radius": "var(--ag-radius)"},
            ),
            rx.el.div(
                rx.el.i(class_name="bi bi-bell-slash", style={"font-size": "3rem", "color": "var(--ag-light)"}),
                rx.el.p("Уведомлений нет", style={"color": "var(--ag-gray)", "margin-top": "1rem"}),
                style={"text-align": "center", "padding": "3rem 0"},
            ),
        ),
    )


# -- sidebar ------------------------------------------------------------------

def _sidebar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                AppState.user_avatar != "",
                rx.el.img(
                    src=AppState.user_avatar,
                    style={
                        "width": "80px",
                        "height": "80px",
                        "border-radius": "50%",
                        "object-fit": "cover",
                        "margin": "0 auto 1rem",
                        "display": "block",
                    },
                ),
                rx.el.div(
                    rx.el.i(class_name="bi bi-person-circle", style={"font-size": "3rem", "color": "var(--ag-red)"}),
                    style={
                        "width": "80px",
                        "height": "80px",
                        "border-radius": "50%",
                        "background": "#fff0f0",
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "margin": "0 auto 1rem",
                    },
                ),
            ),
            rx.el.div(
                AppState.display_name,
                style={"font-weight": "800", "font-size": "1.1rem", "text-align": "center", "margin-bottom": ".25rem"},
            ),
            rx.cond(
                AppState.user_phone != "",
                rx.el.div(AppState.user_phone, style={"font-size": ".87rem", "color": "var(--ag-gray)", "text-align": "center"}),
            ),
            rx.cond(
                AppState.user_email != "",
                rx.el.div(AppState.user_email, style={"font-size": ".82rem", "color": "var(--ag-gray)", "text-align": "center", "word-break": "break-all"}),
            ),
            style={"padding": "1.5rem 1.25rem 1.25rem", "border-bottom": "1px solid var(--ag-border)"},
        ),
        rx.el.nav(
            rx.el.button(
                rx.el.i(class_name="bi bi-person me-2"),
                "Профиль",
                on_click=UserState.set_profile_tab("profile"),
                style={
                    "display": "flex",
                    "align-items": "center",
                    "width": "100%",
                    "padding": ".75rem 1.25rem",
                    "border": "none",
                    "background": rx.cond(UserState.profile_tab == "profile", "#fff0f0", "none"),
                    "color": rx.cond(UserState.profile_tab == "profile", "var(--ag-red)", "var(--ag-dark)"),
                    "font-weight": rx.cond(UserState.profile_tab == "profile", "700", "500"),
                    "font-size": ".92rem",
                    "cursor": "pointer",
                    "text-align": "left",
                    "border-left": rx.cond(UserState.profile_tab == "profile", "3px solid var(--ag-red)", "3px solid transparent"),
                    "transition": "all .15s",
                },
            ),
            rx.el.button(
                rx.el.i(class_name="bi bi-car-front me-2"),
                "Мой гараж",
                on_click=UserState.set_profile_tab("garage"),
                style={
                    "display": "flex",
                    "align-items": "center",
                    "width": "100%",
                    "padding": ".75rem 1.25rem",
                    "border": "none",
                    "background": rx.cond(UserState.profile_tab == "garage", "#fff0f0", "none"),
                    "color": rx.cond(UserState.profile_tab == "garage", "var(--ag-red)", "var(--ag-dark)"),
                    "font-weight": rx.cond(UserState.profile_tab == "garage", "700", "500"),
                    "font-size": ".92rem",
                    "cursor": "pointer",
                    "text-align": "left",
                    "border-left": rx.cond(UserState.profile_tab == "garage", "3px solid var(--ag-red)", "3px solid transparent"),
                    "transition": "all .15s",
                },
            ),
            rx.el.button(
                rx.el.i(class_name="bi bi-bell me-2"),
                "Уведомления",
                rx.cond(
                    UserState.unread_count > 0,
                    rx.el.span(
                        " (",
                        UserState.unread_count.to_string(),
                        ")",
                        style={"color": "var(--ag-red)", "font-weight": "700"},
                    ),
                ),
                on_click=UserState.set_profile_tab("notifications"),
                style={
                    "display": "flex",
                    "align-items": "center",
                    "width": "100%",
                    "padding": ".75rem 1.25rem",
                    "border": "none",
                    "background": rx.cond(UserState.profile_tab == "notifications", "#fff0f0", "none"),
                    "color": rx.cond(UserState.profile_tab == "notifications", "var(--ag-red)", "var(--ag-dark)"),
                    "font-weight": rx.cond(UserState.profile_tab == "notifications", "700", "500"),
                    "font-size": ".92rem",
                    "cursor": "pointer",
                    "text-align": "left",
                    "border-left": rx.cond(UserState.profile_tab == "notifications", "3px solid var(--ag-red)", "3px solid transparent"),
                    "transition": "all .15s",
                },
            ),
            style={"padding": ".5rem 0"},
        ),
        rx.el.div(
            rx.el.button(
                rx.el.i(class_name="bi bi-box-arrow-right me-2"),
                "Выйти",
                on_click=AppState.sign_out,
                class_name="ag-btn-outline",
                style={"width": "100%", "font-size": ".9rem"},
            ),
            style={"padding": "1rem 1.25rem"},
        ),
        style={
            "background": "white",
            "border-radius": "var(--ag-radius)",
            "box-shadow": "var(--ag-shadow)",
            "overflow": "hidden",
        },
    )


# -- main content panel -------------------------------------------------------

def _content_panel() -> rx.Component:
    return rx.el.div(
        rx.cond(
            UserState.profile_tab == "profile",
            _tab_profile(),
            rx.cond(
                UserState.profile_tab == "garage",
                _tab_garage(),
                _tab_notifications(),
            ),
        ),
        class_name="ag-card",
    )


# -- page ---------------------------------------------------------------------

def profile_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    rx.el.a("Главная", href="/"),
                    " / Личный кабинет",
                    class_name="ag-breadcrumb",
                ),
                class_name="mb-2",
            ),
            rx.el.h1("Личный кабинет"),
            class_name="ag-page-header",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(_sidebar(), class_name="col-12 col-lg-3 mb-4 mb-lg-0"),
                    rx.el.div(_content_panel(), class_name="col-12 col-lg-9"),
                    class_name="row g-4",
                ),
                class_name="container",
            ),
            class_name="ag-section-white ag-section-py",
        ),
        _footer(),
        on_mount=[
            AppState.load_profile,
            UserState.init_edit_profile,
            UserState.load_notifications,
            VehicleState.load_vehicles,
        ],
    )


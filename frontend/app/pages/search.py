"""Страница поиска автосервисов — современный дизайн."""
from __future__ import annotations

import reflex as rx

from app.api import YANDEX_MAPS_KEY
from app.components.navbar import navbar
from app.pages.index import _footer
from app.states.search import SearchState

# ──────────────────────────────────────────────────────────────────────────────
# Яндекс.Карты JS
# ──────────────────────────────────────────────────────────────────────────────
_YMAP_SCRIPT = f"""
(function() {{
  var YKEY = '{YANDEX_MAPS_KEY}';
  var _map = null, _clusterer = null, _ready = false, _pendingPts = null;

  window._ahSetPoints = function(pts) {{
    _pendingPts = pts;
    if (_ready) _renderPoints();
  }};

  function _renderPoints() {{
    if (!_map || !_pendingPts) return;
    _map.geoObjects.removeAll();
    var placemarks = _pendingPts.map(function(p) {{
      return new ymaps.Placemark(
        [p.lat, p.lon],
        {{
          hintContent: p.n,
          balloonContent: '<div style="font-family:Inter,sans-serif;padding:4px 0">'
            + '<b style="font-size:14px">' + p.n + '</b>'
            + (p.a ? '<br><span style="color:#777;font-size:12px">' + p.a + '</span>' : '')
            + (p.ph ? '<br><a href="tel:' + p.ph + '" style="color:#e84040;font-size:12px">' + p.ph + '</a>' : '')
            + (p.r > 0 ? '<br><span style="color:#f59e0b;font-size:12px">&#9733; ' + p.r.toFixed(1) + '</span>' : '')
            + '</div>',
        }},
        {{ preset: 'islands#carIcon', iconColor: '#e84040' }}
      );
    }});
    _clusterer.add(placemarks);
    _map.geoObjects.add(_clusterer);
    if (_pendingPts.length > 0) {{
      try {{
        _map.setBounds(_map.geoObjects.getBounds(), {{ checkZoomRange: true, zoomMargin: 50 }});
      }} catch(e) {{}}
    }}
    _pendingPts = null;
  }}

  function _initMap() {{
    var el = document.getElementById('autohub-ymap');
    if (!el || _map) return;
    _map = new ymaps.Map('autohub-ymap', {{
      center: [55.75, 37.62],
      zoom: 9,
      controls: ['zoomControl', 'geolocationControl', 'fullscreenControl'],
    }});
    _clusterer = new ymaps.Clusterer({{
      preset: 'islands#invertedRedClusterIcons',
      groupByCoordinates: false,
    }});
    _ready = true;
    if (_pendingPts) _renderPoints();
  }}

  window._ahInitMap = function() {{
    if (_map) return;
    if (window.ymaps) {{ ymaps.ready(_initMap); return; }}
    var url = YKEY
      ? 'https://api-maps.yandex.ru/2.1/?apikey=' + YKEY + '&lang=ru_RU'
      : 'https://api-maps.yandex.ru/2.1/?lang=ru_RU';
    var s = document.createElement('script');
    s.src = url;
    s.onload = function() {{ ymaps.ready(_initMap); }};
    document.head.appendChild(s);
  }};
}})();
"""

# Quick-filter chips
_CHIPS = [
    ("Шиномонтаж", "шиномонтаж"),
    ("ТО и обслуживание", "то"),
    ("Кузовной ремонт", "кузов"),
    ("Детейлинг", "детейлинг"),
    ("Автоэлектрика", "электрика"),
    ("Тюнинг", "тюнинг"),
    ("Автомойка", "мойка"),
]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _stars(rating) -> rx.Component:
    """Рейтинг в виде звёзд + число."""
    return rx.el.span(
        rx.el.span("★★★★★", class_name="sh-stars"),
        rx.el.span("(" + rating.to_string() + ")", class_name="sh-stars-count"),
        style={"display": "inline-flex", "align-items": "center", "gap": "3px"},
    )


def _chip_row() -> rx.Component:
    return rx.el.div(
        *[
            rx.el.span(
                label,
                class_name="sh-chip",
                on_click=SearchState.on_query_change(val) | SearchState.on_enter_search,
            )
            for label, val in _CHIPS
        ],
        class_name="sh-chips",
    )


def _view_toggle() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            "Список",
            on_click=SearchState.switch_to_list,
            class_name=rx.cond(
                SearchState.view_mode == "list",
                "sh-view-btn active",
                "sh-view-btn",
            ),
            type="button",
        ),
        rx.el.button(
            "Карта",
            on_click=SearchState.switch_to_map,
            class_name=rx.cond(
                SearchState.view_mode == "map",
                "sh-view-btn active",
                "sh-view-btn",
            ),
            type="button",
        ),
        class_name="sh-view-toggle",
    )


def _filter_bar() -> rx.Component:
    return rx.el.div(
        rx.el.input(
            placeholder="Город (напр. Москва)",
            value=SearchState.city_filter,
            on_change=SearchState.set_city_filter,
            class_name="sh-filter-input",
            style={"max-width": "160px"},
        ),
        rx.el.select(
            rx.el.option("Все регионы", value="all"),
            rx.el.option("Москва и МО", value="Москва и Московская область"),
            rx.el.option("Санкт-Петербург", value="Санкт-Петербург и Ленинградская область"),
            rx.el.option("Краснодарский край", value="Краснодарский край"),
            rx.el.option("Свердловская обл.", value="Свердловская область"),
            class_name="sh-filter-select",
            on_change=SearchState.set_region_filter,
            default_value="all",
        ),
        rx.el.select(
            rx.el.option("По рейтингу", value="rating"),
            rx.el.option("Релевантность", value="relevance"),
            class_name="sh-filter-select",
            on_change=SearchState.set_sort,
            default_value="rating",
        ),
        _view_toggle(),
        class_name="sh-filter-bar",
    )


def _partner_card(p: dict) -> rx.Component:
    return rx.el.div(
        # Avatar
        rx.el.div(
            rx.el.span(
                p["name"].to(str)[0:2],
                class_name="sh-avatar-initials",
            ),
            class_name="sh-avatar",
        ),
        # Body
        rx.el.div(
            rx.el.a(
                p["name"],
                href="/partners/" + p["id"].to(str),
                class_name="sh-card-name",
            ),
            rx.el.div(
                rx.el.i(class_name="bi bi-geo-alt", style={"color": "#ccc", "margin-right": "4px"}),
                p["address"],
                class_name="sh-card-address",
            ),
            rx.el.div(
                # Rating tag
                rx.el.span(
                    "★ ", p["rating"].to_string(),
                    class_name="sh-tag sh-tag-rating",
                ),
                # Hours tag
                rx.el.span(
                    p["working_hours"],
                    class_name="sh-tag",
                ),
                class_name="sh-card-tags",
            ),
            class_name="sh-card-body",
        ),
        # Actions
        rx.el.div(
            rx.el.a(
                "Подробнее →",
                href="/partners/" + p["id"].to(str),
                class_name="sh-btn-detail",
            ),
            rx.el.a(
                "Позвонить",
                href="tel:" + p["phone"].to(str),
                class_name="sh-btn-call",
            ),
            class_name="sh-card-actions",
        ),
        class_name="sh-card",
    )


def _results_list() -> rx.Component:
    return rx.cond(
        SearchState.loading,
        rx.el.div(
            rx.el.div(class_name="spinner-border text-secondary"),
            rx.el.p("Загружаем автосервисы..."),
            class_name="sh-spinner",
        ),
        rx.cond(
            SearchState.results,
            rx.el.div(
                # Meta row
                rx.el.div(
                    rx.el.span(
                        "Найдено: ",
                        rx.el.strong(SearchState.total.to_string()),
                        " автосервисов",
                        class_name="sh-meta-count",
                    ),
                    class_name="sh-meta",
                ),
                rx.foreach(SearchState.results, _partner_card),
            ),
            rx.el.div(
                rx.el.i(class_name="bi bi-search sh-empty-icon"),
                rx.el.h3("Ничего не найдено"),
                rx.el.p("Попробуйте другой запрос или уберите фильтры"),
                class_name="sh-empty",
            ),
        ),
    )


def _map_view() -> rx.Component:
    return rx.cond(
        SearchState.map_loading,
        rx.el.div(
            rx.el.div(class_name="spinner-border text-danger"),
            rx.el.p("Загружаем точки на карте..."),
            class_name="sh-spinner",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span("Автосервисов на карте: "),
                SearchState.map_total.to_string(),
                class_name="sh-map-overlay",
            ),
            rx.el.div(
                id="autohub-ymap",
                style={"width": "100%", "height": "640px"},
            ),
            class_name="sh-map-container",
            style={"position": "relative"},
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main page
# ──────────────────────────────────────────────────────────────────────────────

def search_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.script(_YMAP_SCRIPT),

        # === HERO ===
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(class_name="sh-eyebrow-dot"),
                    "5000+ автосервисов · Москва и вся Россия",
                    class_name="sh-eyebrow",
                ),
                rx.el.h1(
                    "Найди идеальный ",
                    rx.el.em("автосервис"),
                ),
                rx.el.p(
                    "Проверенные мастера рядом с вами — рейтинг, цены, запись онлайн",
                    class_name="sh-hero-sub",
                ),
                # Search box
                rx.el.div(
                    rx.el.input(
                        placeholder="Шиномонтаж, замена масла, кузовной ремонт...",
                        value=SearchState.query,
                        on_change=SearchState.on_query_change,
                        on_key_up=SearchState.on_enter_search,
                        id="sh-main-input",
                        auto_focus=True,
                    ),
                    rx.el.button(
                        "Найти",
                        on_click=SearchState.on_enter_search,
                        class_name="sh-search-btn",
                        type="button",
                    ),
                    class_name="sh-search-wrap",
                ),
                # Quick chips
                rx.el.div(
                    rx.el.span(
                        "Шиномонтаж",
                        class_name="sh-chip",
                        on_click=SearchState.on_query_change("шиномонтаж"),
                    ),
                    rx.el.span(
                        "ТО и обслуживание",
                        class_name="sh-chip",
                        on_click=SearchState.on_query_change("то"),
                    ),
                    rx.el.span(
                        "Кузовной ремонт",
                        class_name="sh-chip",
                        on_click=SearchState.on_query_change("кузов"),
                    ),
                    rx.el.span(
                        "Детейлинг",
                        class_name="sh-chip",
                        on_click=SearchState.on_query_change("детейлинг"),
                    ),
                    rx.el.span(
                        "Автоэлектрика",
                        class_name="sh-chip",
                        on_click=SearchState.on_query_change("электрика"),
                    ),
                    rx.el.span(
                        "Автомойка",
                        class_name="sh-chip",
                        on_click=SearchState.on_query_change("мойка"),
                    ),
                    class_name="sh-chips",
                ),
                class_name="container",
            ),
            class_name="sh-hero",
        ),

        # === RESULTS SECTION ===
        rx.el.div(
            rx.el.div(
                # Filter bar
                _filter_bar(),

                # Error
                rx.cond(
                    SearchState.error != "",
                    rx.el.div(
                        SearchState.error,
                        class_name="alert alert-warning mb-3",
                    ),
                ),

                # Content: list or map
                rx.cond(
                    SearchState.view_mode == "map",
                    _map_view(),
                    _results_list(),
                ),

                # CTA banner
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            "Вы владелец автосервиса?",
                            class_name="sh-cta-title",
                        ),
                        rx.el.div(
                            "Разместите свой сервис бесплатно — тарифные планы появятся позже",
                            class_name="sh-cta-sub",
                        ),
                    ),
                    rx.el.a(
                        "Разместить бесплатно →",
                        href="/partner/register",
                        class_name="sh-cta-btn",
                    ),
                    class_name="sh-cta",
                ),

                class_name="container",
            ),
            style={"padding": "2.5rem 0 5rem"},
        ),

        _footer(),
        on_mount=[SearchState.load_categories, SearchState.do_search],
    )
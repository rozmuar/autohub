import reflex as rx

config = rx.Config(
    app_name="app",
    backend_port=8001,
    backend_host="0.0.0.0",
    frontend_port=3000,
    frontend_host="0.0.0.0",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)

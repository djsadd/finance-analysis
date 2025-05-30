"""Project URL Configuration"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from django.contrib.sitemaps import GenericSitemap
from expenses.models import Expense
from django.conf.urls.i18n import i18n_patterns

info_dict = {
    "queryset": Expense.objects.all(),
    "date_field": "date",
}

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Подключаем стандартные URL Django для локализации
    path("admin/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
    # Local apps URL Configuration
    path("", include("income.urls")),
    path("accounts/", include("accounts.urls")),
    path("expenses/", include("expenses.urls")),
    # Sitemap and robots.txt URL Configuration
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "expense": GenericSitemap(
                    info_dict,
                    priority=0.6,
                    changefreq="weekly",
                )
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="config/robots.txt", content_type="text/plain"
        ),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('translationsss/', include('translationsss.urls')),
)
# Customizing-error-views
handler404 = "accounts.views.page_not_found_error"
handler500 = "accounts.views.page_error"
# handler403 = "accounts.views.error_403"
# handler400 = "accounts.views.error_400"

from django.urls import path
from . import views

urlpatterns = [
    path('', views.historico, name='historico'),
    path('upload/', views.upload_documento, name='upload'),
    path('revisar/<int:doc_id>/', views.revisar_documento, name='revisar_documento'),
    path('gerar-pdf/<int:doc_id>/', views.gerar_pdf, name='gerar_pdf'),
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),
]

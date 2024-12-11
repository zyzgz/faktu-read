import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from fakturead import settings

# Pobieranie danych konfiguracyjnych
endpoint = settings.AZURE_AI_ENDPOINT
key = settings.AZURE_AI_KEY


def get_azure_api_response(file_path):
    """
    Funkcja wysyła plik do Azure Document Intelligence API i zwraca wyniki analizy.

    :param file_path: Ścieżka do lokalnego pliku do analizy.
    :return: Wyniki analizy dokumentu.
    """
    # Inicjalizacja klienta Azure Document Intelligence
    document_analysis_client = DocumentIntelligenceClient(
        endpoint=settings.AZURE_AI_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_AI_KEY)
    )

    # Otwieranie pliku w trybie binarnym i przesyłanie do API
    try:
        with open(file_path, "rb") as file:
            poller = document_analysis_client.begin_analyze_document(
                model_id="prebuilt-invoice", analyze_request=file, content_type="application/octet-stream")
            invoices = poller.result()
            return invoices
    except Exception as e:
        raise RuntimeError(f"Error processing file {file_path}: {str(e)}")

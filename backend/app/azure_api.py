import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from backend.fakturead import settings

# Pobieranie danych konfiguracyjnych
endpoint = settings.AZURE_AI_ENDPOINT
key = settings.AZURE_AI_KEY


def get_azure_api_response(file_name):
    """
    Funkcja wysyła plik do Azure Document Intelligence API i zwraca wyniki analizy.

    :param file_name: Nazwa pliku do analizy (np. 'faktura.png').
    :return: Zawartość dokumentu, liczba stron i wersja API.
    """
    # Określenie pełnej ścieżki pliku


    # Inicjalizacja klienta Azure Document Intelligence
    document_analysis_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Otwieranie pliku w trybie binarnym
    with open("faktura-vat-marza.jpg", "rb") as file:
        # Rozpoczynanie analizy dokumentu
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-invoice", analyze_request=file, content_type="application/octet-stream"
        )
        result = poller.result()

    content = []
    pages = 0

    # Przetwarzanie wyników analizy
    for page in result.pages:
        line_content = []
        for line in page.lines:
            line_content.append(line.content)
        content.append(" ".join(line_content))
        pages += 1

    return "\n".join(content), pages, "Latest"


# Wywołanie funkcji z plikiem faktura.png
if __name__ == "__main__":
    response_content, num_pages, version = get_azure_api_response("faktura.png")
    print(f"Content:\n{response_content}")
    print(f"Number of pages: {num_pages}")
    print(f"API Version: {version}")

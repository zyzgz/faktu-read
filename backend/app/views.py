import re
import traceback
from datetime import datetime
from decimal import Decimal

from django.http import JsonResponse, HttpResponse
from openpyxl.workbook import Workbook
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token

from .azure_api import get_azure_api_response
from .docai_parser import parse_invoice_content
from .models import CustomUser, UploadedFile, Invoice
from .serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from fakturead import settings
from azure.storage.blob import BlobServiceClient


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_login(request):
    if request.method == 'POST':
        return Response({'message': 'User is logged in.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def convert_date(date_string):
    date_formats = [
        "%d-%m-%Y",  # format np. 24-08-2017
        "%Y-%m-%d",  # format np. 2017-08-24
        "%m/%d/%Y",  # format np. 08/24/2017
        "%Y/%m/%d",  # format np. 2017/08/24
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue  # Próbuj następny format, jeśli ten nie działa

    raise ValueError(f"Date '{date_string}' is in an invalid format.")


def extract_amount(amount_string):
    # Usuwamy wszystko, co nie jest liczbą lub kropką
    amount_string = re.sub(r'[^\d.,-]', '', amount_string)

    # Zamiana na Decimal, aby zachować precyzyjność
    return Decimal(amount_string.replace(',', '.'))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_invoices(request):
    parser_classes = [MultiPartParser]

    if 'files' not in request.FILES:
        return JsonResponse({'error': 'No files provided'}, status=400)

    files = request.FILES.getlist('files')  # Pobierz listę plików
    responses = []  # Lista na odpowiedzi dla każdego pliku

    for file in files:
        try:
            # Utwórz rekord dla przesłanego pliku
            uploaded_file = UploadedFile.objects.create(file=file)

            # Przetwarzanie pliku za pomocą Azure Document Intelligence
            invoices = get_azure_api_response(uploaded_file.file.path)

            for invoice in invoices.documents:
                invoice_data = parse_invoice_content(invoice)

                issue_date = convert_date(invoice_data['invoice_date'])
                due_date = convert_date(invoice_data['due_date'])
                total_amount = extract_amount(invoice_data['total_amount'])

                invoice_obj = Invoice.objects.create(
                    invoice_number=invoice_data['invoice_id'],
                    client_nip=invoice_data['customer_tax_id'],
                    issue_date=issue_date,
                    due_date=due_date,
                    total_amount=total_amount,
                    created_by=request.user,
                    file=uploaded_file,
                )

                # Przesyłanie pliku do Azure Blob Storage
                blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING)
                blob_client = blob_service_client.get_blob_client(
                    container=settings.CONTAINER_NAME, blob=uploaded_file.file.name)
                with open(uploaded_file.file.path, "rb") as data:
                    blob_client.upload_blob(data)

            # Oznacz plik jako przetworzony
            uploaded_file.processed = True
            uploaded_file.save()

            responses.append({
                'file_name': file.name,
                'message': 'File uploaded and processed successfully',
                'invoice_ids': [invoice_data['invoice_id'] for invoice in invoices.documents]
            })
        except Exception as e:
            print(traceback.format_exc())
            responses.append({
                'file_name': file.name,
                'error': str(e)
            })

    return JsonResponse({'results': responses}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_excel_report(request):
    nip = request.GET.get('nip')
    if not nip:
        return JsonResponse({'error': 'NIP parameter is required'}, status=400)

    invoices = Invoice.objects.filter(client_nip=nip)
    if not invoices.exists():
        return JsonResponse({'error': 'No invoices found for this NIP'}, status=404)

    # Tworzenie pliku Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"Report for NIP {nip}"

    # Nagłówki
    headers = ["Invoice Number", "Issue Date", "Due Date", "Total Amount"]
    sheet.append(headers)

    # Dane
    for invoice in invoices:
        sheet.append([
            invoice.invoice_number,
            invoice.issue_date,
            invoice.due_date,
            float(invoice.total_amount),
        ])

    # Podsumowanie
    sheet.append([])
    sheet.append(["Total Invoices", invoices.count()])
    sheet.append(["Total Amount", sum(invoice.total_amount for invoice in invoices)])

    # Przygotowanie odpowiedzi HTTP z plikiem Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="report_{nip}.xlsx"'
    workbook.save(response)

    return response





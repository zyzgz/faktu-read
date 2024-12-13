import os
import re
import traceback
from datetime import datetime
from decimal import Decimal

from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse
from openpyxl.workbook import Workbook
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token

from .azure_api import get_azure_api_response
from .docai_parser import parse_invoice_content
from .models import CustomUser, UploadedFile, Invoice, Report
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
            return Response({'token': token.key,
                             'username': username,
                             }, status=status.HTTP_200_OK)

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
    amount_string = re.sub(r'[^\d.,-]', '', amount_string)

    # Zamiana na Decimal, aby zachować precyzyjność
    return Decimal(amount_string.replace(',', '.'))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_invoices(request):
    parser_classes = [MultiPartParser]

    if 'files' not in request.FILES:
        return JsonResponse({'error': 'No files provided'}, status=400)

    files = request.FILES.getlist('files')
    responses = []

    for file in files:
        try:
            uploaded_file = UploadedFile.objects.create(file=file)

            invoices = get_azure_api_response(uploaded_file.file.path)

            invoice_objects = []
            for invoice in invoices.documents:
                invoice_data = parse_invoice_content(invoice)

                invoice_date = convert_date(invoice_data['invoice_date'])
                due_date = convert_date(invoice_data['due_date'])
                total_amount = extract_amount(invoice_data['total_amount'])

                invoice_obj = Invoice.objects.create(
                    invoice_number=invoice_data['invoice_id'],
                    invoice_date=invoice_date,
                    due_date=due_date,
                    total_amount=total_amount,
                    vendor_name=invoice_data['vendor_name'],
                    vendor_address=invoice_data['vendor_address'],
                    vendor_tax_id=invoice_data['vendor_tax_id'],
                    vendor_address_recipient=invoice_data['vendor_address_recipient'],
                    customer_name=invoice_data['customer_name'],
                    customer_id=invoice_data['customer_id'],
                    customer_tax_id=invoice_data['customer_tax_id'],
                    customer_address=invoice_data['customer_address'],
                    billing_address=invoice_data.get('billing_address'),
                    shipping_address=invoice_data.get('shipping_address'),
                    payment_term=invoice_data.get('payment_term'),
                    items=invoice_data.get('items'),
                    created_by=request.user,
                    file=uploaded_file,
                )

                invoice_objects.append(invoice_obj)

                blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING)
                blob_client = blob_service_client.get_blob_client(
                    container=settings.CONTAINER_NAME, blob=uploaded_file.file.name)
                with open(uploaded_file.file.path, "rb") as data:
                    blob_client.upload_blob(data)

            uploaded_file.processed = True
            uploaded_file.save()

            responses.append({
                'file_name': file.name,
                'message': 'File uploaded and processed successfully',
                'invoices': [
                    {
                        "invoice_number": invoice.invoice_number,
                        "invoice_date": invoice.invoice_date,
                        "due_date": invoice.due_date,
                        "total_amount": invoice.total_amount,
                        "amount_due": invoice.amount_due,
                        "vendor_name": invoice.vendor_name,
                        "vendor_address": invoice.vendor_address,
                        "vendor_tax_id": invoice.vendor_tax_id,
                        "vendor_address_recipient": invoice.vendor_address_recipient,
                        "customer_name": invoice.customer_name,
                        "customer_id": invoice.customer_id,
                        "customer_tax_id": invoice.customer_tax_id,
                        "customer_address": invoice.customer_address,
                        "billing_address": invoice.billing_address,
                        "shipping_address": invoice.shipping_address,
                        "payment_term": invoice.payment_term,
                        "items": invoice.items,
                        "created_by": invoice.created_by.username,
                        "created_at": invoice.created_at,
                        "file_id": invoice.file.id if invoice.file else None,
                        "file_name": invoice.file.file.name if invoice.file else None,
                    } for invoice in invoice_objects
                ]
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
    type = request.GET.get('type')

    if not nip:
        return JsonResponse({'error': 'NIP parameter is required'}, status=400)

    invoices = Invoice.objects.filter(customer_tax_id=nip)
    if not invoices.exists():
        return JsonResponse({'error': 'No invoices found for this NIP'}, status=404)

    workbook = Workbook()
    sheet = workbook.active

    if type == "customer_total":
        sheet.title = f"Report for NIP {nip}"

        headers = [
            "Invoice Number", "Invoice Date", "Due Date", "Total Amount",
            "Vendor Name", "Customer Name"
        ]
        sheet.append(headers)

        for invoice in invoices:
            sheet.append([
                invoice.invoice_number,
                invoice.invoice_date,
                invoice.due_date,
                float(invoice.total_amount),
                invoice.vendor_name,
                invoice.customer_name,
            ])

        sheet.append([])
        sheet.append(["Total Invoices", invoices.count()])
        sheet.append(["Total Amount", sum(invoice.total_amount for invoice in invoices)])

        file_name = f"report_{nip}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        file_path = f"temp/{file_name}"
    else:
        return JsonResponse({'error': 'Unknown customer type'}, status=400)

    workbook.save(file_path)

    with open(file_path, 'rb') as file_content:
        report = Report.objects.create(
            name=f"Raport dla NIP {nip}",
            report_type="Excel",
            generated_by=request.user,
        )
        report.file.save(file_name, ContentFile(file_content.read()))

    os.remove(file_path)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="report_{nip}.xlsx"'
    workbook.save(response)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoices(request):
    """
    Endpoint zwracający dane faktur w formacie JSON.
    Obsługuje filtry GET: invoice_number, vendor_tax_id, customer_tax_id, invoice_date_from, invoice_date_to.
    """

    invoice_number = request.GET.get('invoice_number')
    vendor_tax_id = request.GET.get('vendor_nip')
    customer_tax_id = request.GET.get('customer_nip')
    invoice_date_from = request.GET.get('invoice_date_from')
    invoice_date_to = request.GET.get('invoice_date_to')

    filters = Q()

    if invoice_number:
        filters &= Q(invoice_number__icontains=invoice_number)
    if vendor_tax_id:
        filters &= Q(vendor_tax_id__icontains=vendor_tax_id)
    if customer_tax_id:
        filters &= Q(customer_tax_id__icontains=customer_tax_id)
    if invoice_date_from:
        try:
            date_from = datetime.strptime(invoice_date_from, '%Y-%m-%d').date()
            filters &= Q(invoice_date__gte=date_from)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format for invoice_date_from. Use YYYY-MM-DD.'}, status=400)
    if invoice_date_to:
        try:
            date_to = datetime.strptime(invoice_date_to, '%Y-%m-%d').date()
            filters &= Q(invoice_date__lte=date_to)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format for invoice_date_to. Use YYYY-MM-DD.'}, status=400)

    invoices = Invoice.objects.filter(filters)

    data = [
        {
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date,
            "due_date": invoice.due_date,
            "total_amount": invoice.total_amount,
            "amount_due": invoice.amount_due,
            "vendor_name": invoice.vendor_name,
            "vendor_address": invoice.vendor_address,
            "vendor_tax_id": invoice.vendor_tax_id,
            "vendor_address_recipient": invoice.vendor_address_recipient,
            "customer_name": invoice.customer_name,
            "customer_id": invoice.customer_id,
            "customer_tax_id": invoice.customer_tax_id,
            "customer_address": invoice.customer_address,
            "billing_address": invoice.billing_address,
            "shipping_address": invoice.shipping_address,
            "payment_term": invoice.payment_term,
            "items": invoice.items,
            "created_by": invoice.created_by.username,
            "created_at": invoice.created_at,
            "file_id": invoice.file.id if invoice.file else None,
            "file_name": invoice.file.file.name if invoice.file else None,
        }
        for invoice in invoices
    ]

    return JsonResponse({"invoices": data}, status=200, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reports(request):
    name_filter = request.GET.get('name', '')

    reports = Report.objects.filter(
        Q(name__icontains=name_filter)
    ).order_by('-generated_at')

    report_list = [
        {
            'id': report.id,
            'name': report.name,
            'type': report.report_type,
            'generated_at': report.generated_at,
            'generated_by': report.generated_by.username,
        }
        for report in reports
    ]

    return JsonResponse({'reports': report_list})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        return FileResponse(report.file.open('rb'), as_attachment=True, filename=report.file.name)
    except Report.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    try:
        report = UploadedFile.objects.get(id=file_id)
        return FileResponse(report.file.open('rb'), as_attachment=True, filename=report.file.name)
    except Report.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)


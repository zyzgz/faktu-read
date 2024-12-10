
def parse_invoice_content(invoice):
    """
    Funkcja analizuje dane faktury zwrócone przez Azure Document Intelligence
    i przygotowuje je do zapisania w bazie danych.

    :param invoice: Pojedynczy obiekt faktury zwrócony przez Azure Document Intelligence.
    :return: Słownik z przetworzonymi danymi faktury.
    """
    def get_field_value(field):
        """Bezpiecznie pobiera wartość pola, jeśli istnieje."""
        return field["content"] if field else None

    # Wyciąganie kluczowych danych z obiektu faktury
    invoice_data = {
        "invoice_id": get_field_value(invoice.fields.get("InvoiceId")),
        "vendor_name": get_field_value(invoice.fields.get("VendorName")),
        "vendor_address": get_field_value(invoice.fields.get("VendorAddress")),
        "vendor_tax_id": get_field_value(invoice.fields.get("VendorTaxId")),
        "customer_name": get_field_value(invoice.fields.get("CustomerName")),
        "customer_id": get_field_value(invoice.fields.get("CustomerId")),
        "customer_tax_id": get_field_value(invoice.fields.get("CustomerTaxId")),
        "customer_address": get_field_value(invoice.fields.get("CustomerAddress")),
        "invoice_date": get_field_value(invoice.fields.get("InvoiceDate")),
        "due_date": get_field_value(invoice.fields.get("DueDate")),
        "total_amount": get_field_value(invoice.fields.get("InvoiceTotal")),
        "billing_address": get_field_value(invoice.fields.get("BillingAddress")),
        "shipping_address": get_field_value(invoice.fields.get("ShippingAddress")),
    }


    return invoice_data

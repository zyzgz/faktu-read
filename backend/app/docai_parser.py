
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

    def get_field_value_with_key(field, key):
        """Pobiera wartość konkretnego klucza z pola, jeśli istnieje."""
        return field.get(key) if field else None

    print(invoice.fields)
    invoice_data = {
        "invoice_id": get_field_value(invoice.fields.get("InvoiceId")),
        "vendor_name": get_field_value(invoice.fields.get("VendorName")),
        "vendor_address": get_field_value(invoice.fields.get("VendorAddress")),
        "vendor_tax_id": get_field_value(invoice.fields.get("VendorTaxId")),
        "vendor_address_recipient": get_field_value(invoice.fields.get("VendorAddressRecipient")),
        "customer_name": get_field_value(invoice.fields.get("CustomerName")),
        "customer_id": get_field_value(invoice.fields.get("CustomerId")),
        "customer_tax_id": get_field_value(invoice.fields.get("CustomerTaxId")),
        "customer_address": get_field_value(invoice.fields.get("CustomerAddress")),
        "invoice_date": get_field_value(invoice.fields.get("InvoiceDate")),
        "due_date": get_field_value(invoice.fields.get("DueDate")),
        "total_amount": get_field_value(invoice.fields.get("InvoiceTotal")),
        "amount_due": get_field_value(invoice.fields.get("AmountDue")),
        "billing_address": get_field_value(invoice.fields.get("BillingAddress")),
        "shipping_address": get_field_value(invoice.fields.get("ShippingAddress")),
        "payment_term": get_field_value(invoice.fields.get("PaymentTerm")),
        "items": [],
    }

    # items = invoice.fields.get("Items")
    # if items and items.get("valueArray"):
    #     invoice_data["items"] = []
    #     for item in items["valueArray"]:
    #         if item.get("valueObject"):
    #             invoice_data["items"].append({
    #                 "description": get_field_value(item["valueObject"].get("Description")),
    #                 "quantity": get_field_value_with_key(item["valueObject"].get("Quantity"), "valueNumber"),
    #                 "unit": get_field_value(item["valueObject"].get("Unit")),
    #                 "unit_price": get_field_value_with_key(item["valueObject"].get("UnitPrice"), "valueCurrency"),
    #                 "amount": get_field_value_with_key(item["valueObject"].get("Amount"), "valueCurrency"),
    #             })

    return invoice_data

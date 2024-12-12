export interface Invoice {
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  total_amount: number;
  amount_due: number;
  vendor_name: string;
  vendor_address: string;
  vendor_tax_id: string;
  vendor_address_recipient: string;
  customer_name: string;
  customer_id: string;
  customer_tax_id: string;
  customer_address: string;
  billing_address: string;
  shipping_address: string;
  payment_term: string;
  items: any[];
  created_by: string;
  created_at: string;
  file: string | null;
}

import { Invoice } from './invoice.interface';

export interface UploadResponse {
  file_name: string;
  invoices: Invoice[];
  message: string;
}

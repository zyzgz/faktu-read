export interface UploadResponse {
  file_name: string;
  message?: string;
  error?: string;
  invoice_ids?: string[];
}

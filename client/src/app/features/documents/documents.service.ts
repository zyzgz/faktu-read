import { inject, Injectable } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { HttpParams } from '@angular/common/http';
import { catchError, map, Observable } from 'rxjs';
import { Invoice } from './interfaces/invoice.interface';
import { InvoiceFilters } from './interfaces/invoice-filters.interface';
import { UploadResponse } from './interfaces/upload-response.interface';

@Injectable({
  providedIn: 'root',
})
export class DocumentsService {
  private readonly api = inject(ApiService);

  getInvoices(filters: InvoiceFilters = {}): Observable<Invoice[]> {
    let params = new HttpParams();
    for (const key in filters) {
      if (filters[key as keyof InvoiceFilters]) {
        params = params.set(key, filters[key as keyof InvoiceFilters] as string);
      }
    }

    return this.api.get<{ invoices: Invoice[] }>('get-invoices/').pipe(
      map((response) => response.invoices),
      catchError((error) => {
        console.error('Get invoices error:', error);
        throw error;
      }),
    );
  }

  uploadInvoices(files: File[]): Observable<{ results: UploadResponse[] }> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file, file.name));

    return this.api.post<{ results: UploadResponse[] }>('upload-invoices/', formData).pipe(
      catchError((error) => {
        console.error('Upload invoices error:', error);
        throw error;
      }),
    );
  }
}

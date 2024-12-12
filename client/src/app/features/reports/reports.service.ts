import { inject, Injectable } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { catchError, Observable } from 'rxjs';
import { HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ReportsService {
  private readonly api = inject(ApiService);

  generateExcelReport(nip: string): Observable<Blob> {
    const params = new HttpParams().set('nip', nip);

    return this.api.get<Blob>('/generate-excel-report', { params, responseType: 'blob' }).pipe(
      catchError((error) => {
        console.error('Generate Excel report error:', error);
        throw error;
      }),
    );
  }
}

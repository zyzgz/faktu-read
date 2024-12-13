import { inject, Injectable } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { catchError, map, Observable } from 'rxjs';
import { HttpHeaders, HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ReportsService {
  private readonly api = inject(ApiService);

  generateExcelReport(nip: string): Observable<Blob> {
    const params = new HttpParams().set('nip', nip).set('type', 'customer_total');

    return this.api
      .get<Blob>('generate-excel-report', params, {
        responseType: 'blob' as 'json',
      })
      .pipe(
        catchError((error) => {
          console.error('Generate excel report error:', error);
          throw error;
        }),
      );
  }

  getExcelReports(): Observable<Report[]> {
    return this.api.get<{ reports: Report[] }>('list-reports').pipe(
      map((response) => response.reports),
      catchError((error) => {
        console.error('Get excel reports error:', error);
        throw error;
      }),
    );
  }

  getReportById(id: string): Observable<Blob> {
    return this.api
      .get<Blob>(`download-report/${id}`, new HttpParams(), { responseType: 'blob' as 'json' })
      .pipe(
        catchError((error) => {
          console.error('Get report by id error:', error);
          throw error;
        }),
      );
  }
}

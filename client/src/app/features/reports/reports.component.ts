import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ReportsService } from './reports.service';
import { Select } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DocumentsService } from '../documents/documents.service';
import { BehaviorSubject, catchError, map, of, switchMap, tap } from 'rxjs';
import { MessageService } from 'primeng/api';
import { AsyncPipe, DatePipe } from '@angular/common';
import { Toast } from 'primeng/toast';
import { TableModule } from 'primeng/table';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [Select, FormsModule, ButtonModule, AsyncPipe, Toast, TableModule, DatePipe],
  providers: [MessageService],
  templateUrl: './reports.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportsComponent {
  private readonly reports = inject(ReportsService);
  private readonly documents = inject(DocumentsService);
  private readonly message = inject(MessageService);

  private readonly refreshNips$ = new BehaviorSubject<void>(undefined);
  nips$ = this.refreshNips$.pipe(
    switchMap(() =>
      this.documents.getInvoices().pipe(
        map((invoices) => {
          const nipSet = new Set<string>();
          invoices.forEach((invoice) => {
            if (invoice.customer_tax_id) nipSet.add(invoice.customer_tax_id);
          });
          this.nipError$.next(null);
          return Array.from(nipSet).map((nip) => ({ label: nip, value: nip }));
        }),
        catchError(() => {
          this.nipError$.next('Nie udało się pobrać NIP-ów.');
          return of([]);
        }),
      ),
    ),
  );
  selectedNip: string | null = null;
  nipError$ = new BehaviorSubject<string | null>(null);
  reportHistoryError$ = new BehaviorSubject<string | null>(null);
  reportHistory$ = this.reports.getExcelReports().pipe(
    tap(() => this.reportHistoryError$.next(null)),
    catchError(() => {
      this.reportHistoryError$.next('Nie udało się pobrać historii raportów.');
      return of([]);
    }),
  );

  refreshNips(): void {
    this.refreshNips$.next();
  }

  generateReport(): void {
    if (!this.selectedNip) {
      this.message.add({
        severity: 'info',
        summary: 'Proszę wybrać NIP z listy, aby wygenerować raport.',
      });
      return;
    }

    this.reports.generateExcelReport(this.selectedNip).subscribe({
      next: (blob) => this.downloadExcelFile(blob, `report_${this.selectedNip}.xlsx`),
      error: () =>
        this.message.add({
          severity: 'error',
          summary: 'Wystąpił błąd',
          detail: 'Nie udało się wygenerować raportu, spróbuj ponownie.',
        }),
    });
  }

  getReportById(id: string): void {
    this.reports.getReportById(id).subscribe({
      next: (blob) => this.downloadExcelFile(blob, `report_${id}.xlsx`),
      error: () =>
        this.message.add({
          severity: 'error',
          summary: 'Wystąpił błąd',
          detail: 'Nie udało się pobrać raportu, spróbuj ponownie.',
        }),
    });
  }

  private downloadExcelFile(blob: Blob, fileName: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
    window.URL.revokeObjectURL(url);
  }
}

import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ReportsService } from './reports.service';
import { Select } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DocumentsService } from '../documents/documents.service';
import { BehaviorSubject, catchError, map, of, switchMap } from 'rxjs';
import { MessageService } from 'primeng/api';
import { AsyncPipe } from '@angular/common';
import { Toast } from 'primeng/toast';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [Select, FormsModule, ButtonModule, AsyncPipe, Toast],
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
  reportHistory = [];

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
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${this.selectedNip}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: () => {
        this.message.add({
          severity: 'error',
          summary: 'Wystąpił błąd',
          detail: 'Nie udało się wygenerować raportu, spróbuj ponownie.',
        });
      },
    });
  }
}

import { AsyncPipe, CurrencyPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { DocumentsService } from '../documents/documents.service';
import { BehaviorSubject, catchError, of, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ButtonModule, RouterLink, TableModule, CurrencyPipe, AsyncPipe, DatePipe],
  templateUrl: './home.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly documents = inject(DocumentsService);

  private readonly refresh$ = new BehaviorSubject<void>(undefined);
  invoicesError$ = new BehaviorSubject<string | null>(null);
  invoicesCount$ = new BehaviorSubject<number>(0);
  invoices$ = this.refresh$.pipe(
    switchMap(() =>
      this.documents.getInvoices().pipe(
        tap((invoices) => {
          this.invoicesError$.next(null);
          this.invoicesCount$.next(invoices.length);
        }),
        catchError(() => {
          this.invoicesError$.next('Nie udało się pobrać faktur.');
          this.invoicesCount$.next(0);
          return of([]);
        }),
      ),
    ),
  );

  refresh(): void {
    this.refresh$.next();
  }
}

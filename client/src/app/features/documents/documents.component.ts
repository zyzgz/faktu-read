import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FileUpload, FileUploadHandlerEvent, FileUploadModule } from 'primeng/fileupload';
import { DocumentsService } from './documents.service';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { Toast } from 'primeng/toast';
import { Invoice } from './interfaces/invoice.interface';
import { CurrencyPipe } from '@angular/common';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [FileUpload, FileUploadModule, TableModule, ButtonModule, Toast, CurrencyPipe],
  providers: [MessageService],
  templateUrl: './documents.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentsComponent {
  private readonly documents = inject(DocumentsService);
  private readonly message = inject(MessageService);

  uploadedInvoices: Invoice[] = [];

  uploadInvoices(event: FileUploadHandlerEvent): void {
    const files: File[] = Array.from(event.files);
    this.documents.uploadInvoices(files).subscribe({
      next: (response) => {
        console.log(response);

        this.uploadedInvoices = response.results.map((result) => result.invoices).flat();
        const successCount = response.results.filter((result) => result.message).length;

        if (successCount > 0) {
          this.message.add({
            severity: 'success',
            summary: 'Sukces',
            detail: `${successCount} faktur przesłano pomyślnie.`,
          });
        }
      },
      error: () => {
        this.message.add({
          severity: 'error',
          summary: 'Wystąpił błąd',
          detail: 'Przesyłanie nie powiodło się, spróbuj ponownie.',
        });
      },
    });
  }
}

import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FileUpload, FileUploadHandlerEvent, FileUploadModule } from 'primeng/fileupload';
import { DocumentsService } from './documents.service';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { UploadResponse } from './interfaces/upload-response.interface';
import { Toast } from 'primeng/toast';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [FileUpload, FileUploadModule, TableModule, ButtonModule, Toast],
  providers: [MessageService],
  templateUrl: './documents.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentsComponent {
  private readonly documentsService = inject(DocumentsService);
  private readonly messageService = inject(MessageService);

  uploadedInvoices: UploadResponse[] = [];

  uploadInvoices(event: FileUploadHandlerEvent): void {
    const files: File[] = Array.from(event.files);
    this.documentsService.uploadInvoices(files).subscribe({
      next: (responses: UploadResponse[]) => {
        this.uploadedInvoices = responses;
        const successCount = responses.filter((response) => response.message).length;
        const errorCount = responses.filter((response) => response.error).length;

        if (successCount > 0) {
          this.messageService.add({
            severity: 'success',
            summary: 'Sukces',
            detail: `${successCount} faktur przesłano pomyślnie.`,
          });
        }

        if (errorCount > 0) {
          this.messageService.add({
            severity: 'error',
            summary: 'Błąd',
            detail: `${errorCount} faktur nie udało się przesłać.`,
          });
        }
      },
      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Wystąpił błąd',
          detail: 'Przesyłanie nie powiodło się, spróbuj ponownie.',
        });
      },
    });
  }
}

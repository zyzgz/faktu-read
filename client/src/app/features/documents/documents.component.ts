import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [],
  templateUrl: './documents.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentsComponent {}

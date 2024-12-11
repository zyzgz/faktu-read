import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Avatar } from 'primeng/avatar';
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [Avatar],
  templateUrl: './dashboard.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent {}

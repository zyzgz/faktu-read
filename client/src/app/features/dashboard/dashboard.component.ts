import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router, RouterLink, RouterModule, RouterOutlet } from '@angular/router';
import { Menu } from 'primeng/menu';
import { ButtonModule } from 'primeng/button';
import { MenuItem, MessageService } from 'primeng/api';
import { AuthService } from '../../core/services/auth.service';
import { Toast } from 'primeng/toast';
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, RouterOutlet, RouterModule, ButtonModule, Menu, Toast],
  providers: [MessageService],
  templateUrl: './dashboard.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly message = inject(MessageService);

  items: MenuItem[] = [
    {
      label: 'Wyloguj',
      icon: 'pi pi-sign-out',
      command: () => {
        this.auth.logout().subscribe({
          next: () => this.router.navigate(['/login']),
          error: () =>
            this.message.add({
              severity: 'error',
              summary: 'Wystąpił błąd',
              detail: 'Nie udało się wylogować, spróbuj ponownie.',
            }),
        });
      },
    },
  ];
}

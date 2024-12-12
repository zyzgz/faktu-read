import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import {
  FormsModule,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { passwordMatchValidator } from './password-match.validator';
import { AuthService } from '../../../core/services/auth.service';
import { Message } from 'primeng/message';
@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    InputTextModule,
    ButtonModule,
    RouterLink,
    Message,
  ],
  templateUrl: './register.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RegisterComponent {
  private readonly auth = inject(AuthService);
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly router = inject(Router);

  registerForm = this.fb.group(
    {
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(6)]],
    },
    { validators: passwordMatchValidator() },
  );
  isLoading = signal(false);
  errorMessage: string | null = null;

  register(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      this.errorMessage = null;
      return;
    }

    this.isLoading.set(true);
    this.errorMessage = null;
    const { username, password } = this.registerForm.getRawValue();
    this.auth.register(username, password).subscribe({
      next: () => this.router.navigate(['/login']),
      error: () => {
        this.isLoading.set(false);
        this.errorMessage = 'Nie udało się zarejestrować.';
        this.registerForm.reset();
      },
    });
  }
}

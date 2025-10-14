import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ReactiveFormsModule } from '@angular/forms';
import { inject } from '@angular/core';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [ReactiveFormsModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
    })
    export class LoginComponent {
    fb = inject(FormBuilder);
    auth = inject(AuthService);
    router = inject(Router);
    form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required]
    });
    onSubmit() {
    if (this.form.invalid) return;
    const { email, password } = this.form.value;
    this.auth.login(email!, password!).subscribe({
    next: () => {
    if (this.auth.isAdmin()) this.router.navigate(['/admin']);
    else this.router.navigate(['/user']);
    },
    error: (err) => alert(err.error.detail || 'Error al iniciar sesión')
    });
    }
}
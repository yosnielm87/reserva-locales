import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [ReactiveFormsModule],
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.css']
})
export class RegisterComponent {
    private fb = inject(FormBuilder);
    private auth = inject(AuthService);
    private router = inject(Router);

    form = this.fb.group({
        fullName: ['', Validators.required],
        email: ['', [Validators.required, Validators.email]],
        password: ['', [Validators.required, Validators.minLength(6)]]
    });

    onSubmit() {
        if (this.form.invalid) return;

        const { fullName, email, password } = this.form.value;

        // 1 objeto en lugar de 3 parámetros sueltos
        this.auth.register({ email: email!, password: password!, full_name: fullName! })
            .subscribe({
                next: res => {
                    // guardamos el token que YA nos devuelve el backend
                    localStorage.setItem('token', res.access_token);
                    alert('Cuenta creada y autenticada');
                    this.router.navigate(['/']);   // dashboard, home, etc.
                },
                error: err => alert(err.error.detail || 'Error al registrarse')
            });
    }
}
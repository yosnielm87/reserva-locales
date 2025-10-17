import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { tap, switchMap } from 'rxjs/operators';

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

        this.auth.register({ email: email!, password: password!, full_name: fullName! })
            .pipe(
                tap(res => localStorage.setItem('token', res.access_token)),
                switchMap(() => this.auth.getMe())   // <-- petición que ya sale 200
            )
            .subscribe({
                next: user => {                      // <-- objeto user del backend
                    console.log('Usuario logueado →', user);
                    // ⬇️⬇️⬇️  AQUÍ guardas el usuario  ⬇️⬇️⬇️
                    this.auth.setUser(user);
                    // ⬆️⬇️  y luego navegas  ⬇️⬆️
                    this.router.navigate(['/user']);
                },
                error: err => alert(err.error.detail || 'Error al registrarse')
            }
        );
    }

}
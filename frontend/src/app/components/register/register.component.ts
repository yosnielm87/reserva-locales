import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ReactiveFormsModule } from '@angular/forms';
import { inject } from '@angular/core';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [ReactiveFormsModule],
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.css']
})
export class RegisterComponent {
fb = inject(FormBuilder);
auth = inject(AuthService);
router = inject(Router);
form = this.fb.group({
fullName: ['', Validators.required],
email: ['', [Validators.required, Validators.email]],
password: ['', [Validators.required, Validators.minLength(6)]]
});
onSubmit() {
if (this.form.invalid) return;
const { fullName, email, password } = this.form.value;
this.auth.register(email!, password!, fullName!).subscribe({
next: () => {
alert('Cuenta creada');
this.router.navigate(['/login']);
},
error: (err) => alert(err.error.detail || 'Error al registrarse')
});
}
}
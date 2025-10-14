import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
export const authGuard = () => {
const auth = inject(AuthService);
const router = inject(Router);
if (!auth.token) {
router.navigate(['/login']);
return false;
}
return true;
};
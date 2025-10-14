import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
export const adminGuard = () => {
const auth = inject(AuthService);
const router = inject(Router);
if (!auth.isAdmin()) {
router.navigate(['/user']);
return false;
}
return true;
};
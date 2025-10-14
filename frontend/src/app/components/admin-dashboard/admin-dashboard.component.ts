import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../services/admin.service';
@Component({
    selector: 'app-admin-dashboard',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './admin-dashboard.component.html',
    styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
    adminSvc = inject(AdminService);
    conflicts: any[] = [];
    ngOnInit() {
        this.loadConflicts();
    }
    loadConflicts() {
        this.adminSvc.getConflicts().subscribe(data => this.conflicts = data);
    }
    resolve(reservationId: string, priority: number, status: 'approved' | 'rejected') {
        this.adminSvc.resolve(reservationId, priority, status).subscribe(() => {
        alert('Resolución guardada');
        this.loadConflicts();
    });
    }
    logout() {
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
}
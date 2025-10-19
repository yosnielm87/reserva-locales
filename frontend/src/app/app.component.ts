import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { LoginComponent } from './components/login/login.component';
import { AuthService } from './services/auth.service';
import { LocaleService } from './services/locale.service'; // <-- tu servicio

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LoginComponent, CommonModule],
  styleUrls: ['./app.component.css'],
  template: `
    <header class="banner">
      <div class="top-right">
        <app-login *ngIf="(auth.user$ | async) === null" [styleInline]="true"></app-login>
        <ng-container *ngIf="auth.user$ | async as user">
          <span>Hola, {{ user.full_name }}</span>
          <button (click)="logout()">Cerrar sesión</button>
        </ng-container>
      </div>
      <div class="banner-content">
        <h1>Reserva de Locales</h1>
        <p>Gestioná tus espacios de forma rápida y sencilla</p>
      </div>
    </header>

    <!-- Panel de locales (solo logueado) -->
    <div class="layout">
      <aside class="sidebar" *ngIf="auth.user$ | async">
        <h3>Locales</h3>
        <div class="local-card" *ngFor="let l of locales$ | async">
          <strong>{{ l.name }}</strong>

          <img [src]="l.imagen_url"
              [alt]="l.name"
              onerror="this.src='/assets/img/no-image.jpg'">

          <div class="info">
            <p>{{ l.description }}</p>
            <small>Capacidad: {{ l.capacity }} personas</small>
          </div>
        </div>
      </aside>

      <!-- Contenido de la página -->
      <main class="content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `
})
export class AppComponent implements OnInit {
  locales$!: Observable<any[]>; // <-- locales

  constructor(
    public auth: AuthService,
    private localeSvc: LocaleService // <-- tu servicio
  ) { }

  ngOnInit() {
    this.auth.initSession().subscribe(); // recupera usuario
    this.locales$ = this.localeSvc.list(); // carga todos los locales
  }

  logout() {
    this.auth.logout();
    window.location.reload();
  }
}
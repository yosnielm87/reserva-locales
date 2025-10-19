import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { LoginComponent } from './components/login/login.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LoginComponent, CommonModule],
  styles: [`
    .banner{
      position:relative;
      height:300px;
      background:url('/assets/img/banner.jpg') center/cover no-repeat;
      display:flex;
      align-items:center;
      justify-content:center;
      color:#fff;
    }
    .banner::before{content:'';position:absolute;inset:0;background:rgba(0,0,0,.45);}
    .banner-content{position:relative;z-index:1;text-align:center;}
    .top-right{position:absolute;top:15px;right:30px;z-index:2;display:flex;gap:8px;align-items:center;}
    .top-right span{font-weight:500;}
    .top-right button{padding:4px 10px;border:none;border-radius:3px;background:#ff9800;color:#fff;cursor:pointer;}
  `],
  template: `
    <header class="banner">
      <div class="top-right">
        <!-- Sin loguear → login inline -->
        <app-login *ngIf="(auth.user$ | async) === null" [styleInline]="true"></app-login>

        <!-- Logueado → bienvenida + cerrar sesión -->
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

    <router-outlet></router-outlet>
  `
})
export class AppComponent implements OnInit {
  constructor(public auth: AuthService) {}

  ngOnInit() {
    this.auth.initSession().subscribe(); // recupera usuario si hay token
  }

  logout() {
    this.auth.logout();
    window.location.reload(); // recarga y vuelve a mostrar login
  }
}
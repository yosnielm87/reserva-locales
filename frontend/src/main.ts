// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';   // <-- importa el config

bootstrapApplication(AppComponent, appConfig)   // <-- pásalo completo
 .catch(err => console.error(err));
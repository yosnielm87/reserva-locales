import { Component, inject, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
// Importamos FormsModule para usar [(ngModel)] en los inputs del filtro
import { FormBuilder, FormsModule, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { AdminService } from '../../services/admin.service';
import { ReservationWithLocale, LocaleListItem, ReservationFull } from '../../models/reservation.model';
// Importamos combineLatest para fusionar los disparadores de recarga y filtro
import { Observable, BehaviorSubject, switchMap, startWith, map, of, combineLatest } from 'rxjs';
import { LocaleCreate, LocaleOut } from '../../models/locale.model';
import { LocaleAdminService } from '../../services/locale-admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  // FormsModule es necesario para la vinculación de datos de los filtros [(ngModel)]
  imports: [CommonModule, DatePipe, FormsModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  private auth = inject(AuthService);
  private adminSvc = inject(AdminService);

  private localeAdminSvc = inject(LocaleAdminService);
  private fb = inject(FormBuilder);

  activeTab: 'pending' | 'history' | 'locales' = 'pending';

  // 1. DISPARADORES Y ESTADO DE FILTRO
  private reloadTrigger$ = new BehaviorSubject<void>(undefined); // Para aprobar/rechazar
  private filterTrigger$ = new BehaviorSubject<void>(undefined); // Para el botón de búsqueda

  startDate: string = ''; // Input de fecha de inicio (ISO format string)
  endDate: string = '';   // Input de fecha de fin (ISO format string)

  /* Snapshot y User */
  private get userSnap() { return (this.auth as any)['user$'].value; }
  user$ = this.auth.getUser();

  // --- DATA FLOWS ---

  // Combina los dos disparadores para el historial (cambio de status O clic en Buscar)
  private historyTrigger$ = combineLatest([this.reloadTrigger$, this.filterTrigger$]);

  // 1. PENDIENTES: Se recarga solo con reloadTrigger$
  pending$: Observable<ReservationFull[]> = this.reloadTrigger$.pipe(
    switchMap(() => this.adminSvc.getPendingReservations()),
    map(list =>
      list.map(r => ({
        id: r.id,
        start_dt: r.start_dt,
        end_dt: r.end_dt,
        status: r.status,
        motive: r.motive,
        userName: r.userName ?? 'Usuario Desconocido',   // ← viene del backend
        userEmail: r.userEmail ?? 'Sin email',          // ← viene del backend
        locale: {
          id: r.locale.id,
          name: r.locale.name,
          imagen_url: r.locale.imagen_url ?? '/assets/img/no-image.jpg'
        }
      }) as ReservationFull)
    ),
    startWith([])
  );

  // 2. HISTORIAL: Se recarga con cualquier cambio en historyTrigger$
  history$: Observable<ReservationFull[]> = this.historyTrigger$.pipe(
    // switchMap recibe los triggers, pero usa el estado actual del componente para filtrar
    switchMap((): Observable<ReservationFull[]> => {
      const start = this.startDate;
      const end = this.endDate;

      // Llama al servicio con las fechas de inicio y fin
      const historyObservable = (this.adminSvc as any).getHistoryWithLocale ?
        (this.adminSvc as any).getHistoryWithLocale(start, end) : of([]);

      return historyObservable as Observable<ReservationFull[]>;
    }),
    startWith([])
  );

  // 3. LOCALES: Se cargan una sola vez al inicio.
  locales$: Observable<LocaleOut[]> = this.localeAdminSvc.list().pipe(
    map(list => {
      list.forEach(l => this.localesMap.set(l.id, l));
      return list;
    }),
    startWith([])
  );

  private localesMap = new Map<string, LocaleListItem>();

  ngOnInit(): void {
    if (!this.userSnap) { this.auth.initSession().subscribe(); }

    // Cargar locales reales desde el servicio
    this.locales$.subscribe(list => list.forEach(l => this.localesMap.set(l.id, l)));
  }

  // --- TEMPLATE HELPERS ---
  getLocaleDetail(id: string): LocaleListItem | undefined {
    return this.localesMap.get(id);
  }

  getLocaleImage(id: string): string {
    return this.localesMap.get(id)?.imagen_url || 'https://placehold.co/80x80/9e9e9e/ffffff?text=Local';
  }

  // --- FILTER ACTIONS ---
  /** Dispara la búsqueda de historial con los rangos de fecha actuales */
  searchHistory(): void {
    // ESTA es la función que activa history$ mediante el filterTrigger$
    this.filterTrigger$.next();
  }

  // --- RESERVATION ACTIONS ---

  /** Aprueba la reserva */
  approve(res: ReservationFull): void {
    this.adminSvc.setReservationStatus(res.id, 'approved').subscribe({
      next: () => {
        // ⚠️ REEMPLAZAR alert() con una notificación o modal custom
        console.log(`Reserva ${res.id} aprobada.`);
        this.reloadTrigger$.next(); // Recarga Pending y History
      },
      error: (err: any) => console.error(`Error al aprobar: ${err.message || 'Desconocido'}`)
    });
  }

  /** Rechaza/Anula la reserva (USA 'cancelled') */
  reject(res: ReservationFull): void {
    (this.adminSvc as any).setReservationStatus(res.id, 'cancelled').subscribe({
      next: () => {
        // ⚠️ REEMPLAZAR alert() con una notificación o modal custom
        console.log(`Reserva ${res.id} cancelada.`);
        this.reloadTrigger$.next(); // Recarga Pending y History
      },
      error: (err: any) => console.error(`Error al cancelar: ${err.message || 'Desconocido'}`)
    });
  }

  // --- LOCALE ACTIONS (PLACEHOLDERS) ---

  showLocaleForm = false;
  isEditing = false;
  localeForm: FormGroup = this.fb.group({
    name: ['', Validators.required],
    description: [''],
    capacity: [0, [Validators.min(1)]],
    location: [''],
    open_time: [''],
    close_time: [''],
    imagen: [null]
  });
  selectedFile: File | null = null;
  editingId: string | null = null;

  addLocale(): void {
    this.isEditing = false;
    this.localeForm.reset();
    this.showLocaleForm = true;
  }

  editLocale(id: string): void {
    this.isEditing = true;
    this.editingId = id;
    this.localeAdminSvc.list().pipe(
      map(list => list.find(l => l.id === id)!)
    ).subscribe(l => {
      this.localeForm.patchValue(l);
      this.showLocaleForm = true;
    });
  }

  deleteLocale(id: string): void {
    if (!confirm('¿Eliminar este local?')) return;
    this.localeAdminSvc.delete(id).subscribe(() => this.locales$ = this.localeAdminSvc.list());
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) this.selectedFile = input.files[0];
  }

  saveLocale(): void {
    if (this.localeForm.invalid) return;
    const dto = new FormData();
    Object.keys(this.localeForm.value).forEach(key => {
      if (key === 'imagen' && this.selectedFile) dto.append('imagen', this.selectedFile);
      else dto.append(key, this.localeForm.value[key]);
    });

    const op = this.isEditing && this.editingId
      ? this.localeAdminSvc.update(this.editingId, dto)
      : this.localeAdminSvc.create(dto);

    op.subscribe(() => {
      this.showLocaleForm = false;
      this.selectedFile = null;
      this.locales$ = this.localeAdminSvc.list();
    });
  }

  logout(): void {
    this.auth.logout();
    window.location.href = '/login';
  }
}

import { Injectable } from '@angular/core';
import { Register } from 'src/app/models/register.model';
import { BehaviorSubject, Observable } from 'rxjs';
import { Client } from 'src/app/models/client.model';

@Injectable({
  providedIn: 'root'
})
export class OrderService {


  public reservationId: number;
  public client: Register;

  constructor() { }

  public setClient(client: Client): void {
    localStorage.setItem('client', JSON.stringify(client));
  }

  public getClient(): string {
    return localStorage.getItem('client');
  }

  public setReservation(reservationId): void {
    localStorage.setItem('reservationId', JSON.stringify(reservationId));
  }

  public getReservation(): string {
    return localStorage.getItem('reservationId');
  }
}

import { Injectable } from '@angular/core';
import { Register } from 'src/app/models/register.model';

@Injectable({
  providedIn: 'root'
})
export class OrderService {

  public reservationId: number;
  public client: Register;

  constructor() { }
}

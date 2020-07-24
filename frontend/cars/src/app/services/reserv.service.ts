import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { Reservation } from '../models/reservation.model';
import { Observable } from 'rxjs';
import { Token } from '@angular/compiler/src/ml_parser/lexer';

@Injectable({
  providedIn: 'root'
})
export class ReservService {

  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
  ) { }

  public postReservation(reservationData: Reservation): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'reservation';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<Token>(url, reservationData, httpOptions);
  }
}

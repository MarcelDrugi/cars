import { Segment } from './../models/segment.model';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { Reservation } from '../models/reservation.model';
import { Observable } from 'rxjs';
import { Token } from '@angular/compiler/src/ml_parser/lexer';
import { AccDataService } from '../shared/services/acc-data.service';
import { SavedReservation } from '../models/saved-reservation';


@Injectable({
  providedIn: 'root'
})
export class ReservService {

  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
    private accDataService: AccDataService
  ) { }

  public postReservation(reservationData: Reservation): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'checkres';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<any>(url, reservationData, httpOptions);
  }

  public getSegment(id: string): Observable<Segment> {
    const url = this.backendInfoService.absolutePath + 'segment/' + id;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.get<Segment>(url, httpOptions);
  }

  public getReservation(id: number): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'reservation/' + id;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.get<any>(url, httpOptions);
  }

}

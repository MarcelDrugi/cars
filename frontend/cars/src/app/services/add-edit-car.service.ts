import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { Token } from '../models/token.model';
import { Observable } from 'rxjs';
import { Car } from '../models/car.model';
import { Segment } from '../models/segment.model';

@Injectable({
  providedIn: 'root'
})
export class AddEditCarService {

  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
    private accDataService: AccDataService
  ) { }

  public postCar(carData: FormData): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'cars';
    const headers = new HttpHeaders({
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<Token>(url, carData, httpOptions);
  }

  public updateCar(carData: FormData): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'cars';
    const headers = new HttpHeaders({
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.put<Token>(url, carData, httpOptions);
  }

  public deleteCar(deletedCar: number): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'cars/' + deletedCar;
    const headers = new HttpHeaders({
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.delete<Token>(url, httpOptions);
  }

  public postSegment(segmentData: Segment): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'segments';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<Token>(url, segmentData, httpOptions);
  }

  public updateSegment(segmentData: Segment): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'segments/' + segmentData.id;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.put<Token>(url, segmentData, httpOptions);
  }

  public deleteSegment(deletedSegment: number): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'segments/' + deletedSegment;
    const headers = new HttpHeaders({
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.delete<Token>(url, httpOptions);
  }
}

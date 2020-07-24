import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Car } from '../models/car.model';

@Injectable({
  providedIn: 'root'
})
export class GetPublicDataService {

  constructor(
    private backendInfoService: BackendInfoService,
    private accDataService: AccDataService,
    private http: HttpClient,
    ) { }

  public getSegment(): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'segments';
    const token = this.accDataService.getToken();
    let headers: HttpHeaders;
    if (token !== 'null') {
      headers = new HttpHeaders({
        Authorization: 'JWT ' + token
      });
    }
    else {
      headers = new HttpHeaders({ });
    }
    const httpOptions = {
      headers,
    };
    return this.http.get<any>(url, httpOptions);
  }

  public getCars(): Observable<Array<Car>> {
    const url = this.backendInfoService.absolutePath + 'cars';
    const token = this.accDataService.getToken();
    let headers: HttpHeaders;
    if (token !== 'null') {
      headers = new HttpHeaders({
        Authorization: 'JWT ' + token
      });
    }
    else {
      headers = new HttpHeaders({ });
    }
    const httpOptions = {
      headers,
    };
    return this.http.get<Array<Car>>(url, httpOptions);
  }

}

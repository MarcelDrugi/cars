import { AccDataService } from './../shared/services/acc-data.service';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Register } from '../models/register.model';
import { BackendInfoService } from '../shared/services/backend-info.service';

@Injectable({
  providedIn: 'root'
})
export class RegService {

  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
    private accDataService: AccDataService,
    ) { }

  postRegData(clientData: FormData): Observable<Register> {
    const url = this.backendInfoService.absolutePath + 'signup';

    return this.http.post<Register>(url, clientData);
  }

  public patchPassword(clientId: number, pass: any): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'client/' + clientId ;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.patch<any>(url, pass, httpOptions);
  }

  public patchData(clientId: number, data: any): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'client/' + clientId ;
    const headers = new HttpHeaders({
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.patch<any>(url, data, httpOptions);
  }

}

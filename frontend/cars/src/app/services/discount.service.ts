import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { Register } from '../models/register.model';
import { Client } from '../models/client.model';
import { Token } from '../models/token.model';

@Injectable({
  providedIn: 'root'
})
export class DiscountService {

  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
    private accDataService: AccDataService
  ) { }

  public getClients(): Observable<Array<Client>> {
    const url = this.backendInfoService.absolutePath + 'clients';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.get<Array<Client>>(url, httpOptions);
  }

  public getDiscounts(): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'discounts';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.get<Array<Client>>(url, httpOptions);
  }

  public assignDiscounts(discountData: any): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'discounts';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.put<Token>(url, discountData, httpOptions);
  }

  public postNewDiscount(discountData: any): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'discounts';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<Token>(url, discountData, httpOptions);
  }

  public delDiscount(id: number): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'discounts/' + id;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: 'JWT ' + this.accDataService.getToken()
    });
    const httpOptions = {
      headers,
    };
    return this.http.delete<Token>(url, httpOptions);
  }

}

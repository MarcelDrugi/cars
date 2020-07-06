import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { LogIn } from '../models/login.model';
import { Token } from '../models/token.model';
import { Observable } from 'rxjs';
import {AccDataService} from '../shared/services/acc-data.service';

@Injectable({
  providedIn: 'root'
})
export class LogService {


  constructor(private http: HttpClient, private accDataService: AccDataService) { }

  public postLogData(logUser: LogIn): Observable<Token> {
    const url = 'http://127.0.0.1:8000/api-token-auth/';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<Token>(url, logUser, httpOptions);
  }

}

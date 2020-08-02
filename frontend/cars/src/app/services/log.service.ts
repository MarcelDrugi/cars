import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { LogIn } from '../models/login.model';
import { Token } from '../models/token.model';
import { Observable } from 'rxjs';
import { BackendInfoService } from '../shared/services/backend-info.service';

@Injectable({
  providedIn: 'root'
})
export class LogService {


  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
    ) { }

  public postLogData(logUser: LogIn): Observable<Token> {
    const url = this.backendInfoService.absolutePath + 'api-token-auth/';
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    const httpOptions = {
      headers,
    };
    return this.http.post<Token>(url, logUser, httpOptions);
  }

  public getClient(username: string): Observable<any> {
    const url = this.backendInfoService.absolutePath + 'client/' + username;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    const httpOptions = {
      headers,
    };
    return this.http.get<any>(url, httpOptions);
  }

}

import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { retry } from 'rxjs/internal/operators';
import { Register } from '../models/register.model';

@Injectable({
  providedIn: 'root'
})
export class RegService {

  constructor(private http: HttpClient) { }

  postRegData(regUser: Register): Observable<Register> {
    const url = 'http://127.0.0.1:8000/signup';

    return this.http.post<Register>(url, regUser);
  }
}

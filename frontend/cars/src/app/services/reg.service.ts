import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Register } from '../models/register.model';
import { BackendInfoService } from '../shared/services/backend-info.service';

@Injectable({
  providedIn: 'root'
})
export class RegService {

  constructor(
    private http: HttpClient,
    private backendInfoService: BackendInfoService,
    ) { }

  postRegData(regUser: Register): Observable<Register> {
    const url = this.backendInfoService.absolutePath + 'signup';

    return this.http.post<Register>(url, regUser);
  }
}

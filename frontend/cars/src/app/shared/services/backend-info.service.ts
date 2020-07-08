import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BackendInfoService {

  public absolutePath: string;

  constructor() {
    this.absolutePath = 'http://127.0.0.1:8000/';
  }
}

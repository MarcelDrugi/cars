import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AccDataService {

  //public token: string;
  private username: BehaviorSubject<string>;

  constructor() {
    this.username = new BehaviorSubject<string>('');
  }

  public getToken(): string {
    console.log(localStorage.getItem('token'))
    return localStorage.getItem('token');
  }

  public setToken(token: string): void {
    if (!token) {
      this.setUsername('');
    }
    localStorage.setItem('token', token);
    console.log(localStorage.getItem('token'))
  }

  public setUsername(username: string): void {
    localStorage.setItem('username', username);
    this.username.next(localStorage.getItem('username'));
  }

  public getUsername(): Observable<string> {
    this.username.next(localStorage.getItem('username'));
    return this.username.asObservable();
  }
}

import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { threadId } from 'worker_threads';

@Injectable({
  providedIn: 'root'
})
export class AccDataService {

  private username: BehaviorSubject<string>;
  private avatar: BehaviorSubject<string>;

  constructor() {
    this.username = new BehaviorSubject<string>('');
    this.avatar = new BehaviorSubject<string>('');
  }

  public getToken(): string {
    return localStorage.getItem('token');
  }

  public setToken(token: string): void {
    if (!token) {
      this.setUsername('');
      this.setClient('');
    }
    localStorage.setItem('token', token);
  }

  public setUsername(username: string): void {
    localStorage.setItem('username', username);
    this.username.next(localStorage.getItem('username'));
  }

  public getUsername(): Observable<string> {
    this.username.next(localStorage.getItem('username'));
    return this.username.asObservable();
  }

  public setClient(client: any): void {
    localStorage.setItem('client', JSON.stringify(client));
    this.avatar.next(localStorage.getItem('client'));
  }

  public getClient(): Observable<string> {
    this.avatar.next(localStorage.getItem('client'));
    return this.avatar.asObservable();
  }
}

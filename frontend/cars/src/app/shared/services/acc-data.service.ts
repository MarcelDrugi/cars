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
    console.log(localStorage.getItem('token'))
    return localStorage.getItem('token');
  }

  public setToken(token: string): void {
    if (!token) {
      this.setUsername('');
      this.setAvatar('');
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

  public setAvatar(username: string): void {
    localStorage.setItem('avatar', username);
    this.avatar.next(localStorage.getItem('avatar'));
  }

  public getAvatar(): Observable<string> {
    this.avatar.next(localStorage.getItem('avatar'));
    return this.avatar.asObservable();
  }
}

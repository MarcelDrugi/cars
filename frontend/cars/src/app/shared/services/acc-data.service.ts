import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AccDataService {

  public token: string;
  private username: BehaviorSubject<string>;

  constructor() {this.username = new BehaviorSubject<string>(''); }

  public setUsername(username: string): void {
    this.username.next(username);
  }

  public getUsername(): Observable<string> {
    return this.username.asObservable();
  }
}

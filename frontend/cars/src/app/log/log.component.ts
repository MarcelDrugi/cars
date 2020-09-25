import { Component, OnInit } from '@angular/core';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';
import { LogService } from '../services/log.service';
import { LogIn } from '../models/login.model';
import {Token } from '../models/token.model';
import { AccDataService } from '../shared/services/acc-data.service';
import { Register } from '../models/register.model';
import { Router } from '@angular/router';

@Component({
  selector: 'rental-log',
  templateUrl: './log.component.html',
  styleUrls: ['./log.component.less'],
  providers: [LogService]
})
export class LogComponent implements OnInit {

  // form
  public form: FormGroup;
  public sent = false;
  public usernamePasswordError = false;
  // data containers
  public logUser: LogIn;
  public user: Register;
  // modal
  public warning = true

  constructor(
    private logService: LogService,
    private formBuilder: FormBuilder,
    private accDataService: AccDataService,
    private router: Router
  ) {}

  public validData(): void {
    this.sent = true;
    this.usernamePasswordError = false;
    if (this.form.valid) {
      this.logUser = {
        username: this.form.value.username,
        password: this.form.value.password
      };
      this.postLogData();
    }
  }

  private postLogData() {
    this.logService.postLogData(this.logUser).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
        this.accDataService.setUsername(this.logUser.username);
      },
      error => {
        console.log(error);
        if (error.status === 400) {
          this.usernamePasswordError = true;
        }
        else {
          console.log(error);
        }
      },
      () => {
        this.logService.getClient(this.logUser.username).subscribe(
          resp => {
            console.log(resp)
            this.accDataService.setClient(resp.client);
            this.user = resp.client;
            this.router.navigateByUrl('');
          },
          error => {
            this.accDataService.setClient({employee: true});
            this.router.navigateByUrl('');
          }
        );
      }
    );
  }

  public disableWarning(): void {
    this.warning = false;
  }

  public ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

}

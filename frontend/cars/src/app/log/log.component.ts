import { Component, OnInit } from '@angular/core';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';
import { LogService } from '../services/log.service';
import { LogIn } from '../models/login.model';
import {Token } from '../models/token.model';
import { AccDataService } from '../shared/services/acc-data.service';

@Component({
  selector: 'rental-log',
  templateUrl: './log.component.html',
  styleUrls: ['./log.component.less'],
  providers: [LogService]
})
export class LogComponent implements OnInit {

  public form: FormGroup;
  public logUser: LogIn;
  public sent = false;
  public usernamePasswordError = false;

  constructor(
    private logService: LogService,
    private formBuilder: FormBuilder,
    private accDataService: AccDataService
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
      }
    );
  }

  public ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

}

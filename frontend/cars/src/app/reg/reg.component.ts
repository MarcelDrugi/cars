import { Component, OnInit } from '@angular/core';
import { RegService } from '../services/reg.service';
import { Register } from '../models/register.model';
import { from } from 'rxjs';
import {Router} from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'rental-reg',
  templateUrl: './reg.component.html',
  styleUrls: ['./reg.component.less'],
  providers: [RegService]
})
export class RegComponent implements OnInit {

  public regUser: Register;
  public form: FormGroup;
  public sent = false;
  public takenUsernameError = false;
  public unknownError = false;

  constructor(
    private regService: RegService,
    private formBuilder: FormBuilder,
    private router: Router
  ) { }

  validData(): void {
    this.sent = true;
    this.takenUsernameError = false;
    this.unknownError = false;
    if (this.form.valid) {
      this.regUser = {
        username: this.form.value.username,
        first_name: this.form.value.firstName,
        last_name: this.form.value.firstName,
        email: this.form.value.email,
        password: this.form.value.password
      };
      this.postRegData();
    }
  }

  postRegData(): void {
    this.regService.postRegData(this.regUser).subscribe(
      (post: Register) => {
        console.log(post);
        this.router.navigateByUrl('signin');
      },
      error => {
        if (error.status === 409) {
          this.takenUsernameError = true;
        }
        else if (error.status === 400) {
          this.unknownError = true;
        }
        else {
          console.log(error);
        }
      }
    );
  }

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: ['', Validators.required],
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

}

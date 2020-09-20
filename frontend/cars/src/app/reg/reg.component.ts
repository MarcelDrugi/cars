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

  // data containers
  public form: FormGroup;
  public avatar: string;
  private clientData: FormData;
  private img: File;

  // modal
  public warning = true

  // form errors switches
  public sent = false;
  public takenUsernameError = false;
  public unknownError = false;
  public typeError = false;
  public sizeError = false;
  private imgValidator = true;

  public maxSize = 4096000;

  constructor(
    private regService: RegService,
    private formBuilder: FormBuilder,
    private router: Router
  ) { }

  public validData(): void {
    this.sent = true;
    this.takenUsernameError = false;
    this.unknownError = false;
    if (this.form.valid && this.imgValidator) {
      this.clientData = new FormData();

      this.clientData.append('username', this.form.value.username);
      this.clientData.append('email', this.form.value.email);
      this.clientData.append('first_name', this.form.value.firstName);
      this.clientData.append('last_name', this.form.value.lastName);
      this.clientData.append('avatar', this.img);
      this.clientData.append('password', this.form.value.password);

      this.postRegData();
    }
  }

  private postRegData(): void {
    this.regService.postRegData(this.clientData).subscribe(
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

  public validImg(img: Event): void {

    this.imgValidator = false;
    this.sizeError = false;
    this.typeError = false;


    const reader = new FileReader();
    reader.readAsDataURL(img.target['files'][0]);

    reader.onload = (event) => {
      this.avatar = '' + event.target.result;
    };

    this.img = img.target['files'].item(0);
    console.log('img: ', this.img)


    if (this.img.size > this.maxSize) {
      this.sizeError = true;
    }
    else if (!['image/png', 'image/jpg', 'image/jpeg', 'image/gif'].includes(this.img.type)) {
      this.typeError = true;
    }
    else {
      this.imgValidator = true;
    }
  }

  public disableWarning(): void {
    this.warning = false;
  }

  public ngOnInit(): void {
    this.form = this.formBuilder.group({
      username: ['', Validators.required],
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      img: ['', ]
    });
  }

}

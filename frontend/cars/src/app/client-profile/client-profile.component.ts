import { RegService } from './../services/reg.service';
import { Register } from './../models/register.model';
import { Reservation } from './../models/reservation.model';
import { Order } from './../models/order.model';
import { Component, OnInit } from '@angular/core';
import { ReservService } from '../services/reserv.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { LogService } from '../services/log.service';
import { Router } from '@angular/router';

@Component({
  selector: 'rental-client-profile',
  templateUrl: './client-profile.component.html',
  styleUrls: ['./client-profile.component.less']
})
export class ClientProfileComponent implements OnInit {

  // data contatiners
  public reservations: Array<any>;
  public client: Register;
  private clientId: number;
  public avatar: string;
  private basicAvatar: string;
  private clientData: FormData;
  private img: File;

  // forms
  public dataForm: FormGroup;
  public passwordForm: FormGroup;

  // template switches
  public dataEdition = false;
  public passwordEdition = false;
  public badData = false;

  // form errors switches
  public sentData = false;
  public sentPassword = false;
  public takenUsernameError = false;
  public unknownError = false;
  public sizeError = false;
  private imgValidator = true;
  public typeError = false;
  public newPassword = false;
  public newData = false;
  public wrongPass = false;

  public maxSize = 4096000;

  constructor(
    private rservService: ReservService,
    private accDataService: AccDataService,
    private formBuilder: FormBuilder,
    private regService: RegService,
    private logService: LogService,
    private router: Router,
  ) { }

  private getReservations(): void {
    this.rservService.getReservations().subscribe(
      (resp: any) => {
        this.reservations = resp;
        console.log('r: ', this.reservations);
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
    );
  }

  private getClient(): void {
    this.accDataService.getClient().subscribe((client: any) => {
      const parsedClient = JSON.parse(client);
      this.basicAvatar = parsedClient.avatar;
      this.avatar = this.basicAvatar;
      this.client = parsedClient.user;
      this.clientId = parsedClient.id;
    });
  }

  private refreshData(username: string): void {
    this.logService.getClient(username).subscribe(
      resp => {
        this.accDataService.setClient(resp.client);
      },
      error => {
        console.log(error);
      }
    );
  }

  public editData(): void {
    this.dataEdition = true;
    this.dataForm = this.formBuilder.group({
      username: [this.client.username, Validators.required],
      firstName: [this.client.first_name, Validators.required],
      lastName: [this.client.last_name, Validators.required],
      email: [this.client.email, [Validators.required, Validators.email]],
      img: ['', ]
    });
  }

  public dataEditionCancel(): void {
    this.avatar = this.basicAvatar;
    this.dataEdition = false;
  }

  private patchData(): void {
    this.regService.patchData(this.clientId, this.clientData).subscribe(
      (resp: any) => {
        this.refreshData(this.dataForm.value.username);
        this.newData = true;
        this.dataEdition = false;
        this.dataForm.reset();
        window.scrollTo(0, 0);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
        if (error.statusText === 'Bad Request' && error.status === 400) {
          this.unknownError = true;
        }
        if (error.statusText === 'Conflict' && error.status === 409) {

        }
      }
    );
  }

  public disableWarning(): void {
    this.newData = false;
    this.newPassword = false;
    this.wrongPass = false;
    this.badData = false;
  }

  public validData(): void {
    this.sentData = true;
    this.takenUsernameError = false;
    this.unknownError = false;
    if (this.dataForm.valid && this.imgValidator) {
      this.clientData = new FormData();

      this.clientData.append('username', this.dataForm.value.username);
      this.clientData.append('email', this.dataForm.value.email);
      this.clientData.append('first_name', this.dataForm.value.firstName);
      this.clientData.append('last_name', this.dataForm.value.lastName);
      this.clientData.append('avatar', this.img);
      this.clientData.append('password', this.dataForm.value.password);
      this.clientData.append('id', this.clientId.toString());
      this.patchData();
    }
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

  public editPassword(): void {
    this.passwordEdition = true;
    this.passwordForm = this.formBuilder.group({
      oldPassword: ['', [Validators.required, Validators.minLength(6)]],
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
    });
  }

  public passwordEditionCancel(): void {
    this.passwordEdition = false;
  }

  public validPassword(): void {
    this.unknownError = false;
    this.sentPassword = true;
    this.newPassword = false;

    if (this.passwordForm.valid) {
      const pass = {
        old_password: this.passwordForm.value.oldPassword,
        new_password: this.passwordForm.value.newPassword,
      };
      this.patchPassword(pass);
    }
  }

  private patchPassword(pass: any): void {
    this.regService.patchPassword(this.clientId, pass).subscribe(
      (resp: any) => {
        this.newPassword = true;
        this.passwordForm.reset();
        this.passwordEdition = false;
        this.sentPassword = false;
        window.scrollTo(0, 0);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
        if (error.statusText === 'Bad Request' && error.status === 400) {
          this.unknownError = true;
        }
        if (error.statusText === 'Conflict' && error.status === 409) {
          this.wrongPass = true;
          window.scrollTo(0, 0);
        }
      }
    );
  }

  public pay(id: number): void {
    this.rservService.existingOrder(this.reservations[id].id).subscribe(
      (resp: any) => {
        window.location.href = resp.payment_link;
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
        if (error.statusText === 'Bad Request' && error.status === 400) {
          this.badData = true;
          setTimeout(() => this.router.navigateByUrl('homepage'), 5200);
        }
        if (error.status === 406) {
          this.router.navigateByUrl('fail');
        }
      },
    );
  }

  ngOnInit(): void {
    this.getReservations();
    this.getClient();
  }

}

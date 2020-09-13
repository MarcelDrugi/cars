import { Component, OnInit } from '@angular/core';
import { Segment } from '../models/segment.model';
import { AccDataService } from '../shared/services/acc-data.service';
import { GetPublicDataService } from '../services/get-public-data.service';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ReservService } from '../services/reserv.service';
import { Reservation } from '../models/reservation.model';
import * as BulmaCalendar from '../../../node_modules/bulma-calendar/dist/js/bulma-calendar.min.js';
import { relative } from 'path';
import { Token } from '../models/token.model';
import { Router } from '@angular/router';
import { OrderService } from '../shared/services/order.service';
import { Register } from '../models/register.model';
import { Client } from '../models/client.model';
import { Car } from '../models/car.model';


@Component({
  selector: 'rental-homepage',
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.less', ],
  providers: [ReservService],
})
export class HomepageComponent implements OnInit {

  // data containers
  public segments: Array<Segment>;
  public cars: Array<Car>;
  public reservationForm: FormGroup;
  public theDate: Date;
  private termPlaceHolder = 'PRZEDZIAŁ CZASU';
  public termRange: string;
  private selectedSegment: number;
  public firstCarIndex: number;
  public baseFleetClass = 'column is-2 car '

  // form switches
  public rangeError = false;
  public segmentError = false;
  public loginError = false;
  public allowError = false;

  constructor(
    private accDataService: AccDataService,
    private getPublicDataService: GetPublicDataService,
    private rservService: ReservService,
    private router: Router,
    private orderService: OrderService,
  ) { }


  private getSegments(): void {
    this.getPublicDataService.getSegment().subscribe(
      (segments: any) => {
        this.accDataService.setToken(segments.slice(-1)[0].token);
        this.segments = segments.slice(0, -1);
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  private getCars(): void {
    this.getPublicDataService.getCars().subscribe(
      (cars: any) => {
        this.cars = cars
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  private postReservation(reservationData: Reservation): void {
    this.rservService.postReservation(reservationData).subscribe(
      (resp: any) => {
        this.accDataService.setToken(resp.token);
        if (resp.token !== '') {
          this.orderService.setReservation(resp.reservation);
          const client: Client = resp.client;
          client.user.avatar = resp.client.avatar;
          client.user.password = null;
          this.orderService.setClient(client);
          this.router.navigateByUrl('order');
        }
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
          this.loginError = true;
        }
        if (error.statusText === 'Conflict' && error.status === 409) {
          this.allowError = true;
        }
      },
    );
  }

  public validData(): void {

    // disable previous error messages
    this.rangeError = false;
    this.segmentError = false;
    this.loginError = false;
    this.allowError = false;

    if (this.termRange !== this.termPlaceHolder && this.termRange !== '' && this.selectedSegment) {
      const terms = this.termRange.split(' - ');
      const reservationData = {
        begin: terms[0],
        end: terms[1],
        segment: this.selectedSegment
      };
      this.postReservation(reservationData);
    }
    else if (this.termRange === '' || this.termRange === this.termPlaceHolder) {
      this.rangeError = true;
    }
    else {
      this.segmentError = true;
    }
  }

  public changeSegment(segment: number): void {
    this.selectedSegment = segment;
  }

  public onHoverEnter(event: any) {
    const className = event.target.className
    let div = document.getElementById(event.target.id);
    div.className = this.baseFleetClass + 'car-bigger';
    try {
      let divLeft = document.getElementById((parseInt(event.target.id)-1).toString());
      divLeft.className = this.baseFleetClass + 'car-bigger-side';
    }
    catch (e) { }
    try {
      let divLeft = document.getElementById((parseInt(event.target.id)+1).toString());
      divLeft.className = this.baseFleetClass + 'car-bigger-side';
    }
    catch (e) { }
  }

  public onHoverLeave(event: any) {
    let div = document.getElementById(event.target.id);
    div.className = this.baseFleetClass;
    try {
      let divLeft = document.getElementById((parseInt(event.target.id)-1).toString());
      divLeft.className = this.baseFleetClass;
    }
    catch (e) { }
    try {
      let divLeft = document.getElementById((parseInt(event.target.id)+1).toString());
      divLeft.className = this.baseFleetClass;
    }
    catch (e) { }
  }

  ngOnInit(): void {
    this.termRange = this.termPlaceHolder;
    this.getSegments();
    this.getCars();
    this.firstCarIndex = 0;

    const options = {
      type: 'date',
      isRange: true,
      closeOnSelect: false,
      headerPosition: 'top',
      todayButton: false,
      lang: 'pl',
      labelFrom: 'początek',
      labelTo: 'koniec',
      dateFormat: 'DD.MM.YYYY',
      displayMode: 'dialog',

    };

    const bulmaCalendar = require('bulma-calendar');
    const calendars = bulmaCalendar.attach('[type="date"]', options);

    calendars.forEach(calendar => {
      calendar.on('hide', date => {
        this.termRange = date.value();
      });
    });
  }
}

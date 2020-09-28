import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AccDataService } from '../shared/services/acc-data.service';
import { GetPublicDataService } from '../services/get-public-data.service';
import { Reservation } from '../models/reservation.model';
import { ReservService } from '../services/reserv.service';
import { OrderService } from '../shared/services/order.service';
import { Client } from '../models/client.model';
import { Car } from '../models/car.model';
import { Segment } from '../models/segment.model';

@Component({
  selector: 'rental-car-details',
  templateUrl: './car-details.component.html',
  styleUrls: ['./car-details.component.less']
})
export class CarDetailsComponent implements OnInit {

  // data containers
  public car: Car;
  private terms: Array<Reservation>;
  public segment: Segment;
  public termRange: string;

  private termPlaceHolder = 'WYBIERZ PRZEDZIAŁ';

  // form switches
  public rangeError = false;
  public loginError = false;
  public allowError = false;

  constructor(
    private accDataService: AccDataService,
    private getPublicDataService: GetPublicDataService,
    private rservService: ReservService,
    private orderService: OrderService,
    private router: Router,
  ) { }

  public getTerms(carId: number): void {
    this.getPublicDataService.getTerms(carId).subscribe(
      (terms: Array<Reservation>) => {
        this.terms = terms;
        console.log(this.terms)
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  public getCar(carId: number): void {
    this.getPublicDataService.getCar(carId).subscribe(
      (car: Car) => {
        this.car = car;
        console.log('mój samochód', this.car)
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  private postReservation(reservationData: any): void {
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

  public disableErrors(): void {
    this.rangeError = false;
    this.loginError = false;
    this.allowError = false;
  }

  public validData(): void {

    // disable previous error messages
    this.disableErrors()

    if (this.termRange !== this.termPlaceHolder && this.termRange !== '') {
      const terms = this.termRange.split(' - ');
      const reservationData = {
        begin: terms[0],
        end: terms[1],
        car_id: this.car.id,
      };
      this.postReservation(reservationData);
    }
    else if (this.termRange === '' || this.termRange === this.termPlaceHolder) {
      this.rangeError = true;
    }
  }

  ngOnInit(): void {
    if (window.history.state.car == null) {
      this.router.navigateByUrl('');
    }
    this.car = window.history.state.car;
    this.segment = window.history.state.segment;
    this.getTerms(this.car.id);

    this.termRange = this.termPlaceHolder;
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
      minDate: new Date(),

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

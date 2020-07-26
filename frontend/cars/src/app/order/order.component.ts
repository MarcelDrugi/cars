import { ReservService } from './../services/reserv.service';
import { Reservation } from './../models/reservation.model';
import { Component, OnInit } from '@angular/core';
import { OrderService } from '../shared/services/order.service';
import { Router } from '@angular/router';
import { Register } from '../models/register.model';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Segment } from '../models/segment.model';
import { AccDataService } from '../shared/services/acc-data.service';
import { SavedReservation} from '../models/saved-reservation';

@Component({
  selector: 'rental-order',
  templateUrl: './order.component.html',
  styleUrls: ['./order.component.less']
})
export class OrderComponent implements OnInit {

  // data containers
  public reservationId: number;
  public client: Register;
  public segment: Segment;
  public reservation: SavedReservation;

  // form
  public form: FormGroup;

  // boolen template switches
  public discount = false;
  public sent = false;

  constructor(
    private orderService: OrderService,
    private router: Router,
    private formBuilder: FormBuilder,
    private rservService: ReservService,
    private accDataService: AccDataService,
  ) { }

  public haveDiscount(): void {
    if (this.discount === false) {
      this.discount = true;
      this.form = this.formBuilder.group({
        code: ['', [Validators.required, Validators.minLength(4), Validators.maxLength(13)]]
      });
    }
    else {
      this.discount = false;
      this.form.reset();
      this.sent = false;
    }
  }

  public validCode(): void {
    this.sent = true;
  }

  private getSegment(id: string): void {
    this.rservService.getSegment(id).subscribe(
      (segment: Segment) => {
        this.segment = segment;
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  private getReservation(id: number): void {
    this.rservService.getReservation(id).subscribe(
      (reservation: any) => {
        this.reservation = reservation.reservation;
        console.log(reservation.reservation)
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  ngOnInit(): void {
    this.router.navigateByUrl('order').then(() => {
      this.reservationId = this.orderService.reservationId;
      this.client = this.orderService.client;
      this.getReservation(this.orderService.reservationId);
    });
  }
}

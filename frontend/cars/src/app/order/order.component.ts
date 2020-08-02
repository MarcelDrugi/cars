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
import { Client } from '../models/client.model';
import { Discount } from '../models/discount.model';

@Component({
  selector: 'rental-order',
  templateUrl: './order.component.html',
  styleUrls: ['./order.component.less']
})
export class OrderComponent implements OnInit {

  // data containers
  public reservationId: number;
  public client: Client;
  public segment: Segment;
  public reservation: SavedReservation;
  public totalCost: number;
  private finallyDiscount: Discount = null;
  public comments = '';

  // form
  public form: FormGroup;

  // boolen template switches
  public discount = false;
  public sent = false;
  public wrongDiscountCode = false;
  public discountUsed = false;
  public orderComments = false;

  // payment-response errors switches
  public badData = false;

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
    this.finallyDiscount = null;
    this.wrongDiscountCode = false;

    let multiplier = 1;
    if (this.form.valid) {
      this.client.discount.forEach((dis: any) => {
        if (dis.discount_code.toString() === this.form.value.code) {
          if (!this.discountUsed) {
            multiplier = dis.discount_value;
            this.discountUsed = true;
            this.finallyDiscount = dis;
          }
        }
      });
      if (multiplier === 1) {
        this.wrongDiscountCode = true;
      }
      this.totalCost = this.totalCost * multiplier;
    }
  }

  public return(): void {
    this.router.navigateByUrl('homepage');
  }

  public calculateCost(): void {
    this.discountUsed = false;

    const begin = new Date(this.reservation.begin);
    const end = new Date(this.reservation.end);
    let days = end.getTime() - begin.getTime();
    days /= (1000 * 3600 * 24);
    console.log(days);
    if (days < 7) {
      this.totalCost = this.reservation.car.segment.pricing.day * days;
      this.totalCost = parseFloat(this.totalCost.toFixed(2));
      console.log('day cost: ', this.totalCost);
    }
    else {
      const weeks = days / 7;
      this.totalCost = this.reservation.car.segment.pricing.week * weeks;
      this.totalCost = parseFloat(this.totalCost.toFixed(2));
      console.log('week cost: ', this.totalCost);
    }
  }

  public addComments(): void {
    if (this.orderComments) {
      this.orderComments = false;
    }
    else {
      this.orderComments = true;
    }
  }

  public acceptComments(event: Event): void {
    this.comments = event.target[0].value;
    if (this.orderComments){
      this.orderComments = false;
    }
    else {
      this.orderComments = true;
    }
  }

  public accept() {
    const fullData = {
      reserved_car: this.reservation.car.id,
      begin: this.reservation.begin,
      end: this.reservation.end,
      client: this.client.user.username,
      cost: this.totalCost.toFixed(2),
      comments: this.comments,
    };
    if (this.finallyDiscount) {
      fullData['discount'] = this.finallyDiscount.discount_code;
    }
    this.postOrder(fullData);
  }

  private postOrder(fullData: any): void {
    this.rservService.postOrder(fullData).subscribe(
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
    this.router.navigateByUrl('order').then(() => {
      this.client = JSON.parse(this.orderService.getClient());
      this.reservation = JSON.parse(this.orderService.getReservation());
      this.calculateCost();
    });
  }
}

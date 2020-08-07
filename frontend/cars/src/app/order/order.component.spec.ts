import { SavedReservation } from './../models/saved-reservation';
import { Pricing } from './../models/pricing.model';
import { Segment } from './../models/segment.model';
import { ReservedCar } from './../models/reserved-car.model';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OrderComponent } from './order.component';
import { Router, RouterModule } from '@angular/router';
import { OrderService } from '../shared/services/order.service';
import { FormBuilder, Validators } from '@angular/forms';
import { ReservService } from '../services/reserv.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { HttpClient } from '@angular/common/http';
import { RouterTestingModule } from '@angular/router/testing';
import { cpuUsage } from 'process';
import { Discount } from '../models/discount.model';
import { Client } from '../models/client.model';
import { Register } from '../models/register.model';

describe('OrderComponent', () => {
  let component: OrderComponent;
  let fixture: ComponentFixture<OrderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [ OrderComponent ],
      providers: [
        OrderService,
        FormBuilder,
        ReservService,
        AccDataService,
        { provide: HttpClient, useValue: { } }
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OrderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  const createEmptyForm = () => {
    const fB = new FormBuilder();
    component.form = fB.group({ code: ['', ] });
  };

  const createClientWithDiscount = (discountValue: number) => {
    const user = new Register();
    user.username = 'someUSername';

    component.client = new Client();
    component.client.user = user;

    const discount = new Discount();
    discount.id = 1;
    discount.discount_code = '12345678';
    discount.discount_value = discountValue.toString();

    component.client.discount = [discount];
  };

  const createReservation = () => {
    const pricing = new Pricing();
    pricing.id = 3;
    pricing.hour = 25.00;
    pricing.day = 120.00;
    pricing.week = 395.00;

    const segment = new Segment();
    segment.id = 4;
    segment.name = 'someSegment';
    segment.pricing = pricing;

    const reservedCar = new ReservedCar();
    reservedCar.id = 1;
    reservedCar.brand = 'someBrand';
    reservedCar.model = 'someModel';
    reservedCar.reg_number = '1234abc';
    reservedCar.segment = segment;
    reservedCar.img =  null;
    reservedCar.description = 'Some description of the car';

    const reservation = new SavedReservation();
    reservation.id = 138;
    reservation.begin = '2020-11-02';
    reservation.end = '2020-11-07';
    reservation.car = reservedCar;

    return reservation;
  };

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('haveDiscount() should create form with empty-string when discount == false', () => {
    component.discount = false;
    component.haveDiscount();

    expect(component.form.value.code).toEqual('');
  });

  it('haveDiscount() should reset form when discount == true', () => {
    component.discount = true;
    const fB = new FormBuilder();
    component.form = fB.group({
      code: ['899991234', [Validators.required, Validators.minLength(4), Validators.maxLength(13)]]
    });

    component.haveDiscount();
    expect(component.form.value.code).toEqual(null);
  });

  it('haveDiscount() should set discount and sent switches value to false', () => {
    createEmptyForm();
    component.discount = true;

    component.haveDiscount();
    expect(component.discount).toBeFalse();
    expect(component.sent).toBeFalse();
  });

  it('validCode() should set values (regardless of the validation process): sent -> true, finallyDiscount -> null', () => {
    createEmptyForm();
    component.client = new Client();
    component.client.discount = new Array();
    component['finallyDiscount'] = new Discount();
    component.sent = false;

    component.validCode();
    expect(component.sent).toBeTrue();
    expect(component['finallyDiscount']).toBeNull();
  });

  it('validCode() should set switch wrongDiscountCode value to true when validation was ok and client does not have the discount ', () => {
    component.client = new Client();
    component.client.discount = new Array();
    const fB = new FormBuilder();
    component.form = fB.group({ code: ['222212345', [Validators.required, Validators.minLength(4), Validators.maxLength(13)]] });

    component.validCode();
    expect(component.wrongDiscountCode).toBeTrue();
  });

  it('validCode() should reduce totalCost when client has a discount', () => {
    const totalCost = 100;
    const discountValue = 0.5;

    createClientWithDiscount(discountValue);
    const fB = new FormBuilder();
    component.form = fB.group({
      code: [component.client.discount[0].discount_code,
        [Validators.required, Validators.minLength(4), Validators.maxLength(13)]]
    });
    component.totalCost = totalCost;

    component.validCode();
    expect(component.totalCost).toEqual(totalCost * discountValue);
  });

  it('validCode() should overwrite finallyDiscount from the client\'s discount', () => {
    createClientWithDiscount(0.1);
    const fB = new FormBuilder();
    component.form = fB.group({
      code: [component.client.discount[0].discount_code,
        [Validators.required, Validators.minLength(4), Validators.maxLength(13)]]
    });

    component.validCode();
    expect(component['finallyDiscount']).toEqual(component.client.discount[0]);
  });

  it('calculateCost() should calculate and overwrite totalCost', () => {
    const reservation = createReservation();
    component.reservation = reservation;

    const days = (new Date(reservation.end).getTime() - new Date(reservation.begin).getTime()) / 86400000;
    const exceptedCost = days * reservation.car.segment.pricing.day;

    component.calculateCost();
    expect(component.totalCost).toEqual(exceptedCost);
  });

  it('addComments() should set orderCoommets-switch value to false when orderCoommets is true', () => {
    component.orderComments = true;
    component.addComments();
    expect(component.orderComments).toBeFalse();
  });

  it('addComments() should set orderCoommets-switch value to true when orderCoommets is false', () => {
    component.orderComments = false;
    component.addComments();
    expect(component.orderComments).toBeTrue();
  });

  it('accept() should call postOrder()', () => {
    component.reservation = createReservation();
    component.totalCost = 111.00;
    createClientWithDiscount(0.2);

    const postOrder = spyOn<any>(component, 'postOrder');
    component.accept();
    expect(postOrder).toHaveBeenCalled();
  });

});

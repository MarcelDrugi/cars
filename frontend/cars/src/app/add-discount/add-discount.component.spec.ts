import { Discount } from './../models/discount.model';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddDiscountComponent } from './add-discount.component';
import { HttpClient } from '@angular/common/http';
import { FormBuilder } from '@angular/forms';
import { of } from 'rxjs';
import { DiscountService } from '../services/discount.service';
import { Client } from '../models/client.model';
import { EventEmitter } from '@angular/core';

describe('AddDiscountComponent', () => {
  let component: AddDiscountComponent;
  let fixture: ComponentFixture<AddDiscountComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddDiscountComponent ],
      providers: [
        { provide: HttpClient, useValue: { get: () => of([{ }]), post: () => of([{ }]) } },
        FormBuilder,
      ]
    })
    .compileComponents();
  }));

  function prepareDiscountForm(): void {
    /**  Prepares the correct register form. */

    // form for adding car
    component.addDiscount.controls.discount_code.setValue('example');
    component.addDiscount.controls.discount_value.setValue('15');

    fixture.detectChanges();
  }

  beforeEach(() => {
    fixture = TestBed.createComponent(AddDiscountComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit should create empty form', () => {
    component.ngOnInit();
    expect(component.addDiscount.value.discount_code).toEqual('');
    expect(component.addDiscount.value.discount_value).toEqual('');
  });

  it('validNewDiscount() should set the sentNewDiscount-switch on true ', () => {
    component.validNewDiscount();
    expect(component.sentNewDiscount).toBeTrue();
  });

  it('validNewDiscount(), with correct data, should should clear addDiscount form ', () => {
    prepareDiscountForm();  // filling the form
    component.validNewDiscount();

    expect(component.addDiscount.value.discount_code).toBeNull();
    expect(component.addDiscount.value.discount_value).toBeNull();
  });

  it('clientSelection() should select client ', () => {
    const client = new Client();
    client.id = 22;
    component.clients = [client];
    component.clientSelection(0);

    expect(component.selectedClient.id).toEqual(client.id);
  });

});

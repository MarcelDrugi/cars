import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CarDetailsComponent } from './car-details.component';
import { AccDataService } from '../shared/services/acc-data.service';
import { GetPublicDataService } from '../services/get-public-data.service';
import { ReservService } from '../services/reserv.service';
import { OrderService } from '../shared/services/order.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { RouterTestingModule } from '@angular/router/testing';

describe('CarDetailsComponent', () => {
  let component: CarDetailsComponent;
  let fixture: ComponentFixture<CarDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [ CarDetailsComponent ],
      providers: [ 
        AccDataService,
        GetPublicDataService,
        ReservService,
        OrderService,
        { provide: HttpClient, useValue: { post: () => of([{ }]), get: () => of([{ }])} },
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    history.pushState({carId: 1}, '', '')
    fixture = TestBed.createComponent(CarDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('validData() should set: loginError, allowError form switches to false ', () => {
    component.loginError = true;
    component.allowError = true;

    component.validData()

    expect(component.loginError).toBeFalse()
    expect(component.allowError).toBeFalse()
  });

  it('validData() should set rangeError form switch to true when range is incorrect(or doesnt exist)', () => {
    component.rangeError = false;

    component.validData()

    expect(component.rangeError).toBeTrue()
  });

  it('validData() should call postReservation if termRange is correct', () => {
    const postReservation = spyOn<any>(component, 'postReservation');
    component.termRange = '01.01.2021 - 05.01.2021'

    component.validData()

    expect(postReservation).toHaveBeenCalled();
  });

});

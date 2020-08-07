import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HomepageComponent } from './homepage.component';
import { AccDataService } from '../shared/services/acc-data.service';
import { GetPublicDataService } from '../services/get-public-data.service';
import { ReservService } from '../services/reserv.service';
import { Router, RouterModule } from '@angular/router';
import { OrderService } from '../shared/services/order.service';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { RouterTestingModule } from '@angular/router/testing';

describe('HomepageComponent', () => {
  let component: HomepageComponent;
  let fixture: ComponentFixture<HomepageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [ HomepageComponent ],
      providers: [
        AccDataService,
        GetPublicDataService,
        ReservService,
        OrderService,
        { provide: HttpClient, useValue: { get: () => of() } }
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HomepageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('validData() with correct termRange should call postReservation()', () => {
    component['selectedSegment'] = 4;
    component.termRange = '25.11.2023 - 29.11.2023';
    const postReservation = spyOn<any>(component, 'postReservation');
    component.validData();

    expect(postReservation).toHaveBeenCalled();
  });

  it('validData() should set 3 switches to flase: segmentError, allowError, loginError, and one to true: rangeError', () => {
    component.validData();

    expect(component.rangeError).toBeTrue();
    expect(component.segmentError).toBeFalse();
    expect(component.allowError).toBeFalse();
    expect(component.loginError).toBeFalse();
  });

  it('ngOnInit() should call getSegments()', () => {
    const getSegments = spyOn<any>(component, 'getSegments');
    component.ngOnInit();
    expect(getSegments).toHaveBeenCalled();
  });

  it('changeSegment() should overwrite selectedSegment', () => {
    const segmentNumber = 8;
    component.changeSegment(segmentNumber);
    expect(component['selectedSegment']).toEqual(segmentNumber);
  });

});

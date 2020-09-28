import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FleetComponent } from './fleet.component';
import { GetPublicDataService } from '../services/get-public-data.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Segment } from '../models/segment.model';
import { Pricing } from '../models/pricing.model';
import { Car } from '../models/car.model';

class MockPublicService {
  public pricing: Pricing = {id: 0, hour:5, day: 10, week:20};
  public segment: Segment = {id: 0, name: 'someName', pricing: this.pricing};

  public getSegment(): Observable<any> {
    return of([this.segment, this.segment]);
  }
  
  public car: Car = {id: 0, brand: 'someBrand', model: 'someModel', reg_number: 'abcde123', description: 'some description', segment: 0, img: null};

  public getCars(): Observable<Array<Car>> {
    return of([this.car, this.car]);
  }
  
  public getCar(carId: number): Observable<Car> {
    return of(this.car);
  }
}

describe('FleetComponent', () => {
  let component: FleetComponent;
  let fixture: ComponentFixture<FleetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FleetComponent ],
      providers: [{ provide: GetPublicDataService, useValue: MockPublicService }, AccDataService, { provide: HttpClient, useValue: { post: () => of([{ }]), get: () => of([{ }])} },]
    })
    .compileComponents();

    TestBed.overrideComponent(FleetComponent, {
      set: {
        providers: [{ provide: GetPublicDataService, useClass: MockPublicService }]
      }
    });

  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FleetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit should call getCars() and getSegments()', () => {
    const getCars = spyOn(component, 'getCars');
    const getSegments = spyOn<any>(component, 'getSegments');

    component.ngOnInit();

    expect(getCars).toHaveBeenCalled();
    expect(getSegments).toHaveBeenCalled();
  });

  it('ngOnInit should assign a value 0 to selectedSegment', () => {
    component.ngOnInit();
    expect(component.selectedSegment).toEqual(0);
  });

  it('checkSegment() should assign a value to selectedSegment', () => {
    const someSegmentId = 0;
    const fakeEvent = {target: {value: someSegmentId}}

    component.checkSegment(fakeEvent)
    expect(component.selectedSegment).toEqual(someSegmentId);
  });

});

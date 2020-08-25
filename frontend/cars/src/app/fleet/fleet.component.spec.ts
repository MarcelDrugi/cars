import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FleetComponent } from './fleet.component';
import { GetPublicDataService } from '../services/get-public-data.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';

describe('FleetComponent', () => {
  let component: FleetComponent;
  let fixture: ComponentFixture<FleetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FleetComponent ],
      providers: [GetPublicDataService, AccDataService, { provide: HttpClient, useValue: { post: () => of([{ }]), get: () => of([{ }])} },]
    })
    .compileComponents();
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

  it('ngOnInit should assign a value 1 to selectedSegment', () => {
    component.ngOnInit();
    expect(component.selectedSegment).toEqual(1);
  });

  it('checkSegment() should assign a value to selectedSegment', () => {
    const someSegmentId = 7;
    const fakeEvent = {target: {value: someSegmentId}}

    component.checkSegment(fakeEvent)
    expect(component.selectedSegment).toEqual(someSegmentId);
  });

});

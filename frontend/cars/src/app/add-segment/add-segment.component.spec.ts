import { FormBuilder, FormGroup, FormControl } from '@angular/forms';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { AddSegmentComponent } from './add-segment.component';
import { AddEditCarService } from '../services/add-edit-car.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { GetPublicDataService } from '../services/get-public-data.service';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';

describe('AddSegmentComponent', () => {
  let component: AddSegmentComponent;
  let fixture: ComponentFixture<AddSegmentComponent>;
  const segment = {id: 5, name: 'example', pricing: {id: 3, hour: 20.00, day: 110.50, week: 350.00}};

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddSegmentComponent ],
      providers: [
        {
          provide: AddEditCarService,
          useValue: {
            postSegment: () => of({token: '123456789'}),
            deleteSegment: () => of({token: '987654321'})
          }
        },
        AccDataService,
        FormBuilder,
        {
          provide: GetPublicDataService,
          useValue: {
            getSegment: () => of([segment, {token: '123456789'}]),
          }
        },
        { provide: HttpClient, useValue: { } }
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddSegmentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  function prepareSegmentForm() {
    /**  Prepares the correct register form. */

    // form for adding car
    component.segmentForm.controls.name.setValue('example');
    component.segmentForm.controls.hour.setValue('25.50');
    component.segmentForm.controls.day.setValue('240.00');
    component.segmentForm.controls.week.setValue('710.00');

    fixture.detectChanges();
  }

  function prepareSegmentSelection() {
    component.segments = [
      { id: 1, name: 'other', pricing: { id: 1, hour: 15.50, day: 95.20, week: 250.00 }},
      segment,
    ];
    const segmentEvent = { target: { value: '5' }};
    component.segmentSelection(segmentEvent);
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit should create empty form', () => {
    component.ngOnInit();
    expect(component.segmentForm.value.name).toEqual('');
    expect(component.segmentForm.value.hour).toEqual('');
    expect(component.segmentForm.value.day).toEqual('');
    expect(component.segmentForm.value.week).toEqual('');
  });

  it('Calling validData() with correct segmentForm should clear segmentForm', () => {
    prepareSegmentForm();
    component.validData('create');

    expect(component.segmentForm.value.name).toBeNull();
    expect(component.segmentForm.value.hour).toBeNull();
    expect(component.segmentForm.value.day).toBeNull();
    expect(component.segmentForm.value.week).toBeNull();
  });

  it('segmentSelection() should create existingSegmentForm', () => {
    prepareSegmentSelection();

    expect(component.existingSegmentForm).toBeDefined();
  });

  it('segmentSelection() should enter segment values to existingSegmentForm', () => {
    prepareSegmentSelection();

    expect(component.existingSegmentForm.value.name).toEqual(segment.name);
    expect(component.existingSegmentForm.value.hour).toEqual(segment.pricing.hour);
    expect(component.existingSegmentForm.value.day).toEqual(segment.pricing.day);
    expect(component.existingSegmentForm.value.week).toEqual(segment.pricing.week);
  });

  it('deleteSegment() should reset existingSegmentForm', () => {

    component.existingSegmentForm = new FormGroup({
      name: new FormControl(),
      hour: new FormControl(),
      day: new FormControl(),
      week: new FormControl(),
    });

    component.selectedSegment = segment;

    component.existingSegmentForm.controls.name.setValue('otherExample');
    component.existingSegmentForm.controls.hour.setValue('35.50');
    component.existingSegmentForm.controls.day.setValue('140.00');
    component.existingSegmentForm.controls.week.setValue('610.00');

    component.deleteSegment();

    expect(component.existingSegmentForm.value.name).toBeNull();
    expect(component.existingSegmentForm.value.hour).toBeNull();
    expect(component.existingSegmentForm.value.day).toBeNull();
    expect(component.existingSegmentForm.value.week).toBeNull();
  });

});

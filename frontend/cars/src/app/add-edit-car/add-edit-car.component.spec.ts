import { Segment } from './../models/segment.model';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { AddEditCarComponent } from './add-edit-car.component';
import { AddEditCarService } from '../services/add-edit-car.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { GetPublicDataService } from '../services/get-public-data.service';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { exception } from 'console';
import { Car } from '../models/car.model';

describe('AddEditCarComponent', () => {
  let component: AddEditCarComponent;
  let fixture: ComponentFixture<AddEditCarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddEditCarComponent ],
      providers: [
        AccDataService,
        FormBuilder,
        { provide: HttpClient, useValue: { post: () => of([{ }]), put: () => of([{ }])} },
        {
          provide: AddEditCarService,
          useValue: {
            updateCar: () => of({token: '123456789'})
          }
        },
        {
          provide: GetPublicDataService,
          useValue: {
            getSegment: () => of([{name: 'example', pricing: {hour: '20.00', day: '110.50', week: '350.00'}}, {token: '123456789'}]),
            getCars: () => of([{
              id: 1,
              brand: 'Some Brand',
              model: 'Some Model',
              description: 'some description',
              img: 'https://images.pexels.com/photos/1098662/pexels-photo-1098662.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500',
              reg_number: 'abc1234'
            }])
          }
        },
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddEditCarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  function prepareEditCarForm() {
    component.selectedCar = new Car();

    component.selectedCar.id = 7,
    component.selectedCar.brand = 'testingBrand',
    component.selectedCar.model = 'testingModel',
    component.selectedCar.reg_number = 'aaa12345',
    component.selectedCar.segment = 3,
    component.selectedCar.img = new File([], 'someFile.png', { type: 'image/png' }),
    component.selectedCar.description = 'A bb ccc dddd.';

     // form for car edition
    component.existingCarForm = new FormGroup({
      brand: new FormControl(),
      model: new FormControl(),
      reg_number: new FormControl(),
      segment: new FormControl(),
      img: new FormControl(),
      description: new FormControl(),
    });
    component.existingCarForm.controls.brand.setValue('Cde');
    component.existingCarForm.controls.model.setValue('Fgh');
    component.existingCarForm.controls.reg_number.setValue('opr2345');
    component.existingCarForm.controls.segment.setValue('');
    component.existingCarForm.controls.img.setValue('');
    component.existingCarForm.controls.description.setValue('some other description');

    component['segment'] = 2;

     // validators
    component.existingCarForm.controls.brand.setValidators([Validators.required]);
    component.existingCarForm.controls.model.setValidators([Validators.required]);
    component.existingCarForm.controls.reg_number.setValidators([Validators.required, Validators.minLength(6), Validators.maxLength(8)]);
    component.existingCarForm.controls.description.setValidators([Validators.maxLength(2048)]);
  }

  function prepareAddCarForm() {
    /**  Prepares the correct register form. */

    // form for adding car
    component.addCarForm.controls.brand.setValue('Abc');
    component.addCarForm.controls.model.setValue('Xyz');
    component.addCarForm.controls.reg_number.setValue('def4567');
    component.addCarForm.controls.segment.setValue('');
    component.addCarForm.controls.img.setValue('');
    component.addCarForm.controls.description.setValue('example description');

    component['segment'] = 12;
    component['img'] = new File([], 'someFile.png', { type: 'image/png' });
    component['imgValidator'] = true;

    fixture.detectChanges();
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit should create empty form', () => {
    component.ngOnInit();
    expect(component.addCarForm.value.brand).toEqual('');
    expect(component.addCarForm.value.model).toEqual('');
    expect(component.addCarForm.value.reg_number).toEqual('');
    expect(component.addCarForm.value.segment).toEqual('');
    expect(component.addCarForm.value.img).toEqual('');
    expect(component.addCarForm.value.description).toEqual('');
  });

  it('Calling validData with correct addCarForm should clear addCarForm', () => {
    prepareAddCarForm();
    component.validData('create');

    expect(component.addCarForm.value.brand).toBeNull();
    expect(component.addCarForm.value.model).toBeNull();
    expect(component.addCarForm.value.reg_number).toBeNull();
    expect(component.addCarForm.value.segment).toBeNull();
    expect(component.addCarForm.value.img).toBeNull();
    expect(component.addCarForm.value.description).toBeNull();
  });

  it('Calling validData with correct existingCarForm should clear addCarForm', () => {
    prepareEditCarForm();
    component.validData('update');

    expect(component.existingCarForm.value.brand).toBeNull();
    expect(component.existingCarForm.value.model).toBeNull();
    expect(component.existingCarForm.value.reg_number).toBeNull();
    expect(component.existingCarForm.value.segment).toBeNull();
    expect(component.existingCarForm.value.img).toBeNull();
    expect(component.existingCarForm.value.description).toBeNull();
  });

  it('Calling validData with correct addCarForm: segment, img, createImgSrc switches should be null', () => {
    prepareAddCarForm();
    component.validData('create');

    expect(component['img']).toBeNull();
    expect(component['segment']).toBeNull();
    expect(component.createImgSrc).toBeNull();

  });

  it('Calling validData with correct existingCarForm: changeImgSrc switches should be null (when img is not in the form)', () => {
    prepareEditCarForm();
    component.validData('update');

    expect(component.changeImgSrc).toBeNull();

  });

  it('Calling validData with correct addCarForm: createConfirmation switch should be True', () => {
    prepareAddCarForm();
    component.validData('create');

    expect(component.createConfirmation).toBeTrue();
  });

  it('Calling validData with correct existingCarForm: updateConfirmation switch should be True', () => {
    prepareEditCarForm();
    component.validData('update');
    expect(component.updateConfirmation).toBeTrue();
  });

  it('Calling validData with incorrect addCarForm : sent should be true', () => {
    prepareAddCarForm();
    component.addCarForm.controls.reg_number.setValue('abc'); // too short reg_number (should be 6-8)
    component.validData('create');

    expect(component.sent).toBeTrue();
  });

  it('Calling validData with incorrect existingCarForm : editionSent should be true', () => {
    prepareEditCarForm();
    component.existingCarForm.controls.reg_number.setValue('abcdefghijkl'); // too long reg_number (should be 6-8)
    component.validData('update');

    expect(component.editionSent).toBeTrue();
  });

  it('addSegment() should overwrite the segment with its argument', () => {
    const nr = 22;
    component.addSegment(nr);

    expect(component['segment']).toEqual(nr);
  });

});

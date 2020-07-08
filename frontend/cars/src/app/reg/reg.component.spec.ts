import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { RegComponent } from './reg.component';
import { RegService } from '../services/reg.service';
import { HttpClient } from '@angular/common/http';
import { FormBuilder } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';


describe('RegComponent', () => {
  let component: RegComponent;
  let fixture: ComponentFixture<RegComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [ RegComponent ],
      providers: [
        RegService,
        {provide: HttpClient, useValue: {}},
        FormBuilder,
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RegComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  function prepareAndValidRegForm() {
    /**  Prepares the correct register form. */
    fixture = TestBed.createComponent(RegComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    component.form.controls.username.setValue('someUsername');
    component.form.controls.firstName.setValue('Jan');
    component.form.controls.lastName.setValue('Kowalski');
    component.form.controls.email.setValue('jankowalski@somedomain.ll');
    component.form.controls.password.setValue('somePass');

    spyOn<any>(component, 'postRegData');
    component.validData();
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit should create empty form', () => {
    component.ngOnInit();
    expect(component.form.value.firstName).toEqual('');
    expect(component.form.value.lastName).toEqual('');
    expect(component.form.value.username).toEqual('');
    expect(component.form.value.password).toEqual('');
    expect(component.form.value.email).toEqual('');
  });

  it('if form is correct, after calling validData() regUser fields should be equal form', () => {
    prepareAndValidRegForm();
    expect(component.form.value.firstName).toEqual(component.regUser.first_name);
    expect(component.form.value.lastName).toEqual(component.regUser.last_name);
    expect(component.form.value.username).toEqual(component.regUser.username);
    expect(component.form.value.password).toEqual(component.regUser.password);
    expect(component.form.value.email).toEqual(component.regUser.email);
  });

  it('calling validData() function should change "sent" boolean switch on true', () => {
    prepareAndValidRegForm();
    expect(component.sent).toEqual(true);
  });

  it('calling validData() function should change "takenUsernameError" boolean switch on false', () => {
    prepareAndValidRegForm();
    expect(component.takenUsernameError).toEqual(false);
  });

  it('calling validData() function should change "unknownError" boolean switch on false', () => {
    prepareAndValidRegForm();
    expect(component.unknownError).toEqual(false);
  });

});

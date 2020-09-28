import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { LogComponent } from './log.component';
import { LogService } from '../services/log.service';
import { FormBuilder } from '@angular/forms';
import { AccDataService } from '../shared/services/acc-data.service';
import { HttpClient } from '@angular/common/http';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';

describe('LogComponent', () => {
  let component: LogComponent;
  let fixture: ComponentFixture<LogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [LogComponent],
      providers: [
        {
          provide: LogService,
          useValue: {
            postLogData: () => of({token: '123456789'})
          }
        },
        {provide: HttpClient, useValue: {}},
        AccDataService,
        FormBuilder,
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    fixture = TestBed.createComponent(LogComponent);
    component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });

  function prepareAndValidLoginForm() {
    /**  Prepares the correct login form. */
    fixture = TestBed.createComponent(LogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    component.form.controls.username.setValue('someUsername');
    component.form.controls.password.setValue('somePass');

    spyOn<any>(component, 'postLogData');
    component.validData();
  }

  it('if form is correct, after calling validData() logUser fields should be equal form', () => {
    prepareAndValidLoginForm();
    expect(component.form.value).toEqual(component.logUser);
  });

  it('calling validData() function should change "sent" boolean switch on true', () => {
    prepareAndValidLoginForm();
    expect(component.sent).toEqual(true);
  });

  it('calling validData() function should change "sent" boolean switch on true', () => {
    prepareAndValidLoginForm();
    expect(component.sent).toEqual(true);
  });

  it('correct form -> validData() function should change "usernamePasswordError" on false', () => {
    prepareAndValidLoginForm();
    expect(component.usernamePasswordError).toEqual(false);
  });

  it('ngOnInit() shoud create form and insert empty strings to fields', () => {
    component.ngOnInit();
    expect(component.form.value.username).toEqual('');
  });

});

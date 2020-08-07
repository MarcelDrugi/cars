import { Client } from 'src/app/models/client.model';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ClientProfileComponent } from './client-profile.component';
import { HttpClient } from '@angular/common/http';
import { FormBuilder } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';
import { LogService } from '../services/log.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { ReservService } from '../services/reserv.service';
import { RegService } from '../services/reg.service';
import { Register } from '../models/register.model';

describe('ClientProfileComponent', () => {
  let component: ClientProfileComponent;
  let fixture: ComponentFixture<ClientProfileComponent>;
  const returnedClient = { avatar: '', user: {username: 'someUsername', first_name: 'someName', last_name: 'someLastName', email: 'some@email.com'} };
  const token = '12345abcde';

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [ ClientProfileComponent ],
      providers: [
        { provide: HttpClient, useValue: { get: () => of(), patch: () => of() } },
        FormBuilder,
        ReservService,
        {
          provide: AccDataService,
          useValue: {
            getClient: () => of(JSON.stringify(returnedClient)),
            getToken: () => of(token),
          }
        },
        RegService,
        LogService,
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ClientProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  function prepareDataForm(): void {
    const fB = new FormBuilder();
    component.dataForm = fB.group({ username: [], firstName: [], lastName: [], email: [], password: [] });
    component.dataForm.controls.username.setValue('Aaaa');
    component.dataForm.controls.firstName.setValue('Bbbb');
    component.dataForm.controls.lastName.setValue('Cccc');
    component.dataForm.controls.email.setValue('ddd@dd.dd');
    component.dataForm.controls.password.setValue('Eeeeee');
  }

  function preparePasswordForm(): void {
    const fB = new FormBuilder();
    component.passwordForm = fB.group({ oldPassword: [], newPassword: [] });
    component.passwordForm.controls.oldPassword.setValue('Aaaaaa');
    component.passwordForm.controls.newPassword.setValue('Bbbbbb');
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('editData() should set dataEdition switch to true', () => {
    expect(component.dataEdition).toBeFalse();

    component.editData();

    expect(component.dataEdition).toBeTrue();
  });

  it('editData() should insert client\'s value to dataForm', () => {
    component.editData();

    expect(component.dataForm.value.username).toEqual(component.client.username);
    expect(component.dataForm.value.firstName).toEqual(component.client.first_name);
    expect(component.dataForm.value.lastName).toEqual(component.client.last_name);
    expect(component.dataForm.value.email).toEqual(component.client.email);
  });

  it('dataEditionCancel() should restore basicAvatar and set dataEdition-swith to fasle', () => {
    component['basicAvatar'] = 'some/path';
    component.dataEditionCancel();

    expect(component.avatar).toEqual(component['basicAvatar']);
    expect(component.dataEdition).toBeFalse();
  });

  it('validData() should insert to clientData values from validated dataForm', () => {
    prepareDataForm();
    component['imgValidator'] = true;
    component['img'] = new File([], 'someFile.png', { type: 'image/png' })

    component.validData();

    expect(component.dataForm.status).toEqual('VALID');

    expect(component['clientData'].get('username')).toEqual(component.dataForm.value.username);
    expect(component['clientData'].get('first_name')).toEqual(component.dataForm.value.firstName);
    expect(component['clientData'].get('last_name')).toEqual(component.dataForm.value.lastName);
    expect(component['clientData'].get('email')).toEqual(component.dataForm.value.email);
  });

  it('editPassword() should recreate passwordForm with empty-strings', () => {
    component.editPassword();

    expect(component.passwordForm.value.oldPassword).toEqual('');
    expect(component.passwordForm.value.newPassword).toEqual('');
  });

  it('editPassword() should set passwordEdition switch on true', () => {
    expect(component.passwordEdition).toBeFalse();
    component.editPassword();
    expect(component.passwordEdition).toBeTrue();
  });

  it('passwordEditionCancel() should set passwordEdition switch on false', () => {
    component.passwordEdition = true;
    component.passwordEditionCancel();
    expect(component.passwordEdition).toBeFalse();
  });

  it('validPassword() with correct passwordForm should call patchPassword()', () => {
    const patchPassword = spyOn<any>(component, 'patchPassword');
    preparePasswordForm();
    component.validPassword();

    expect(component.passwordForm.status).toEqual('VALID');
    expect(patchPassword).toHaveBeenCalled();
  });

  it('validPassword() should set  switches: unknownError -> false, sentPassword -> true, newPassword -> false', () => {
    preparePasswordForm();
    component.validPassword();

    expect(component.unknownError).toBeFalse();
    expect(component.sentPassword).toBeTrue();
    expect(component.newPassword).toBeFalse();
  });

});

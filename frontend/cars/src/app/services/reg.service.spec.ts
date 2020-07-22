import { TestBed } from '@angular/core/testing';
import { RegService } from './reg.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { Register } from '../models/register.model';

describe('RegService', () => {
  let service: RegService;
  let httpMock: HttpTestingController;
  let backendInfoService: BackendInfoService;
  let newUser: Register;
  let regData: FormData;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        RegService,
        BackendInfoService
      ],
    });
    service = TestBed.inject(RegService);
    backendInfoService = TestBed.inject(BackendInfoService);
    httpMock = TestBed.get(HttpTestingController);
  });

  beforeEach(() => {
    newUser = {
        first_name: 'Adam',
        last_name: 'Mickiewicz',
        username: 'litewskipoeta',
        email: 'ciemno@wszedzie.ll',
        password: 'gluchowszedzie',
        avatar: new File([], 'someFile.png', { type: 'image/png' })
    };

    regData = new FormData();

    regData.append('username', newUser.username);
    regData.append('email', newUser.email);
    regData.append('first_name', newUser.first_name);
    regData.append('last_name', newUser.last_name);
    regData.append('password', newUser.password);
    regData.append('avatar', newUser.avatar);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('request should be POST with suitable merge url', () => {
    service.postRegData(regData).subscribe();

    const url = backendInfoService.absolutePath + 'signup';
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('POST');
  });

  it('request should be contain regData', () => {
    service.postRegData(regData).subscribe(resp => {
      expect(resp).toEqual(newUser);
    }
    );

    const url = backendInfoService.absolutePath + 'signup';
    httpMock.expectOne(url).flush(newUser);
  });

});

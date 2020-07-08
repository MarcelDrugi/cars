import { TestBed } from '@angular/core/testing';
import { RegService } from './reg.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { Register } from '../models/register.model';
import { HttpRequest } from '@angular/common/http';

describe('RegService', () => {
  let service: RegService;
  let httpMock: HttpTestingController;
  let backendInfoService: BackendInfoService;
  let regData: Register;

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
    regData = {
        first_name: 'Adam',
        last_name: 'Mickiewicz',
        username: 'litewskipoeta',
        email: 'ciemno@wszedzie.ll',
        password: 'gluchowszedzie'
    };
  });

  it('request should be POST with suitable merge url', () => {
    service.postRegData(regData).subscribe();

    const url = backendInfoService.absolutePath + 'signup';
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('POST');
    req.flush(regData);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return registerd user data after correct registration', () => {
    service.postRegData(regData).subscribe((returnedData) => {
      expect(returnedData).toEqual(regData);
    });
  });
});

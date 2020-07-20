import { TestBed } from '@angular/core/testing';
import { GetPublicDataService } from './get-public-data.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AccDataService } from '../shared/services/acc-data.service';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { Car } from '../models/car.model';

describe('GetPublicDataService', () => {
  let service: GetPublicDataService;
  let httpMock: HttpTestingController;
  let backendInfoService: BackendInfoService;
  let accDataService: AccDataService;
  let segmentResp: any;
  let carResp: Array<Car>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AccDataService,
        BackendInfoService
      ],
    });
    service = TestBed.inject(GetPublicDataService);
    accDataService = TestBed.inject(AccDataService);
    backendInfoService = TestBed.inject(BackendInfoService);
    httpMock = TestBed.get(HttpTestingController);
  });

  beforeEach(() => {
    segmentResp = [
      {
        id: 7,
        name: 'Some Name',
        pricing: {
          id: 3,
          hour: 23.50,
          day: 115.00,
          week: 489.00
        }
      },
      { token: '987654321abcdefghijk' }
    ];

    carResp = [{
      id: 1,
      brand: 'Fiat',
      model: 'Mirafiori 131',
      reg_number: 'cdef234',
      segment: 5,
      img: null,
      description: 'some description of the car'
    }];
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('request of getSegment() should be GET', () => {
    service.getSegment().subscribe();

    const url = backendInfoService.absolutePath + 'segments';
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('GET');
  });

  it('getSegment() should return segmentResp', () => {

    service.getSegment().subscribe((resp: any) => {
      expect(resp).toEqual(segmentResp);
    });

    const url = backendInfoService.absolutePath + 'segments';
    httpMock.expectOne(url).flush(segmentResp);
  });

  it('request of getCars() should be GET', () => {
    service.getCars().subscribe();

    const url = backendInfoService.absolutePath + 'cars';
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('GET');
  });

  it('getCars() should return carResp (array of Cars)', () => {

    service.getCars().subscribe((resp: Array<Car>) => {
      expect(resp).toEqual(carResp);
    });

    const url = backendInfoService.absolutePath + 'cars';
    httpMock.expectOne(url).flush(carResp);
  });

});

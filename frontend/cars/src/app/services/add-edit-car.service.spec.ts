import { Segment } from './../models/segment.model';
import { TestBed } from '@angular/core/testing';
import { AddEditCarService } from './add-edit-car.service';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Car } from '../models/car.model';
import { Token } from '../models/token.model';

describe('AddEditCarService', () => {
  let service: AddEditCarService;
  let httpMock: HttpTestingController;
  let backendInfoService: BackendInfoService;
  let accDataService: AccDataService;
  let newCar: Car;
  let carData: FormData;
  let segmentData: Segment;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AccDataService,
        BackendInfoService
      ],
    });
    service = TestBed.inject(AddEditCarService);
    accDataService = TestBed.inject(AccDataService);
    backendInfoService = TestBed.inject(BackendInfoService);
    httpMock = TestBed.get(HttpTestingController);
  });

  beforeEach(() => {
    newCar = {
      id: 9,
      brand: 'Fiat',
      model: '125p',
      reg_number: 'abcd456',
      segment: 3,
      img: new File([], 'someFile.png', { type: 'image/png' }),
      description: 'rly nice car'
    };
    carData = new FormData();

    carData.append('id', newCar.id.toString());
    carData.append('brand', newCar.brand);
    carData.append('model', newCar.model);
    carData.append('reg_number', newCar.reg_number);
    carData.append('description', newCar.description);
    carData.append('img', newCar.img);
    carData.append('segment', newCar.segment.toString());

    segmentData = {
      id: 3,
      name: 'Some Name',
      pricing: {
        id: 2,
        hour: 23.50,
        day: 110.00,
        week: 499.00
      }
    };
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('request of postCar() should be POST with suitable merge url', () => {
    service.postCar(carData).subscribe();

    const url = backendInfoService.absolutePath + 'cars';
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('POST');
  });

  it('postCar() should return token', () => {
    const token = '123456789';

    service.postCar(carData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });

    const url = backendInfoService.absolutePath + 'cars';
    httpMock.expectOne(url).flush({ token });
  });

  it('request of udpateCar() should be PUT with suitable merge url', () => {
    service.updateCar(carData).subscribe();

    const url = backendInfoService.absolutePath + 'cars';
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('PUT');
  });

  it('updateCar() should return token', () => {
    const token = '123456789';

    service.updateCar(carData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });

    const url = backendInfoService.absolutePath + 'cars';
    httpMock.expectOne(url).flush({ token: token });
  });

  it('request of deleteCar() should be DELETE with suitable merge url', () => {
    const carNb = 22;
    service.deleteCar(carNb).subscribe();

    const url = backendInfoService.absolutePath + 'cars/' + carNb;
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('DELETE');
  });

  it('deleteCar() should return token', () => {
    const token = '123456789';
    const carNb = 22;

    service.deleteCar(carNb).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });

    const url = backendInfoService.absolutePath + 'cars/' + carNb;
    httpMock.expectOne(url).flush({ token: token });
  });

  it('request of postSegment() should be POST with suitable merge url', () => {
    service.postSegment(segmentData).subscribe();

    const url = backendInfoService.absolutePath + 'segments';
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('POST');
  });

  it('postSegment() should return token', () => {
    const token = '123456789';

    service.postSegment(segmentData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });

    const url = backendInfoService.absolutePath + 'segments';
    httpMock.expectOne(url).flush({ token: token });
  });

  it('request of udpateSegment() should be PUT with suitable merge url', () => {
    service.updateSegment(segmentData).subscribe();

    const url = backendInfoService.absolutePath + 'segments/' + segmentData.id;
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('PUT');
  });

  it('updateSegment() should return token', () => {
    const token = '123456789';

    service.updateSegment(segmentData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });

    const url = backendInfoService.absolutePath + 'segments/' + segmentData.id;
    httpMock.expectOne(url).flush({ token: token });
  });

  it('request of deleteSegment() should be DELETE with suitable merge url', () => {
    const segmentNb = 13;
    service.deleteSegment(segmentNb).subscribe();

    const url = backendInfoService.absolutePath + 'segments/' + segmentNb;
    const req = httpMock.expectOne(url);

    expect(req.request.method).toEqual('DELETE');
  });

  it('deleteSegment() should return token', () => {
    const token = '123456789';
    const segmentNb = 13;

    service.deleteSegment(segmentNb).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });

    const url = backendInfoService.absolutePath + 'segments/' + segmentNb;
    httpMock.expectOne(url).flush({ token: token });
  });


});

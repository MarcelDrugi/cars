import { TestBed } from '@angular/core/testing';
import { ReservService } from './reserv.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AccDataService } from '../shared/services/acc-data.service';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { Reservation } from '../models/reservation.model';
import { Token } from '../models/token.model';

describe('ReservService', () => {
  let service: ReservService;
  let backendInfoService: BackendInfoService;
  let accDataService: AccDataService;
  let httpMock: HttpTestingController;
  const token = '987654321abcdefghij';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AccDataService,
        BackendInfoService
      ],
    });
    service = TestBed.inject(ReservService);
    accDataService = TestBed.inject(AccDataService);
    backendInfoService = TestBed.inject(BackendInfoService);
    httpMock = TestBed.get(HttpTestingController);
  });

  const createReservation = () => {
    const reservation = new Reservation();
    reservation.segment = 7;
    reservation.begin = '2020-11-03';
    reservation.end = '2020-11-12';

    return reservation;
  };

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('request of postNewDiscount() should be POST with suitable merge url', () => {
    const reservation = createReservation();

    service.postReservation(reservation).subscribe();
    const url = backendInfoService.absolutePath + 'checkres';
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('POST');

    service.postReservation(reservation).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });
    httpMock.expectOne(url).flush({ token });
  });

  it('request of delReservation() should be DELETE with suitable merge url', () => {
    const resId = 4359;
    service.delReservation(resId).subscribe();
    const url = backendInfoService.absolutePath + 'reservation/' + resId;
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('DELETE');

    service.delReservation(resId).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });
    httpMock.expectOne(url).flush({ token });
  });

  it('request of postOrder() should be POST with suitable merge url', () => {
    const fullData = { };
    service.postOrder(fullData).subscribe();
    const url = backendInfoService.absolutePath + 'order';
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('POST');

    service.postOrder(fullData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });
    httpMock.expectOne(url).flush({ token });
  });

});

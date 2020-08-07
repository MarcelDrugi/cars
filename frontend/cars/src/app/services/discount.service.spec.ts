import { TestBed } from '@angular/core/testing';

import { DiscountService } from './discount.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { BackendInfoService } from '../shared/services/backend-info.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Token } from '../models/token.model';

describe('DiscountService', () => {
  let service: DiscountService;
  let discountData: object;
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
    service = TestBed.inject(DiscountService);
    accDataService = TestBed.inject(AccDataService);
    backendInfoService = TestBed.inject(BackendInfoService);
    httpMock = TestBed.get(HttpTestingController);
  });

  beforeEach( () => {
    discountData = {
      client: 'someUsername',
      discount: 12,
      acction: 'remove',
    };
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('request of assignDiscounts() should be PUT with suitable merge url', () => {

    service.assignDiscounts(discountData).subscribe();
    const url = backendInfoService.absolutePath + 'discounts';
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('PUT');

    service.assignDiscounts(discountData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });
    httpMock.expectOne(url).flush({ token });
  });

  it('request of postNewDiscount() should be POST with suitable merge url', () => {

    service.postNewDiscount(discountData).subscribe();
    const url = backendInfoService.absolutePath + 'discounts';
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('POST');

    service.postNewDiscount(discountData).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });
    httpMock.expectOne(url).flush({ token });
  });

  it('request of pdelDiscount() should be DELETE with suitable merge url', () => {
    const disID = 4;

    service.delDiscount(disID).subscribe();
    const url = backendInfoService.absolutePath + 'discounts/' + disID;
    const req = httpMock.expectOne(url);
    expect(req.request.method).toEqual('DELETE');

    service.delDiscount(disID).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(token);
    });
    httpMock.expectOne(url).flush({ token });
  });

});

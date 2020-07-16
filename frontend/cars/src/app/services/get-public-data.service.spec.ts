import { TestBed } from '@angular/core/testing';

import { GetPublicDataService } from './get-public-data.service';

describe('GetPublicDataService', () => {
  let service: GetPublicDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetPublicDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

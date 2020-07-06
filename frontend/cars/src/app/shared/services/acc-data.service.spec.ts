import { TestBed } from '@angular/core/testing';

import { AccDataService } from './acc-data.service';

describe('AccDataService', () => {
  let service: AccDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AccDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

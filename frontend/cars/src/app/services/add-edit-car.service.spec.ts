import { TestBed } from '@angular/core/testing';

import { AddEditCarService } from './add-edit-car.service';

describe('AddEditCarService', () => {
  let service: AddEditCarService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AddEditCarService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

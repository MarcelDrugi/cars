import { TestBed } from '@angular/core/testing';

import { AccDataService } from './acc-data.service';
import { BehaviorSubject } from 'rxjs';

describe('AccDataService', () => {
  let service: AccDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AccDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getUsername() should return Observable with username', () => {
    service['username'] = new BehaviorSubject('someUsername');
    const returnedObser = service.getUsername();
    expect(returnedObser.source['_value']).toEqual(service['username']['_value'])
  });

  it('setUsername() should assign value to username', () => {
    const testUsername = 'someUsername';
    service.setUsername(testUsername)
    expect(service['username']['_value']).toEqual(testUsername);
  });

});

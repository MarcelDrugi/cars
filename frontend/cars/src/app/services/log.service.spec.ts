import { TestBed } from '@angular/core/testing';
import { Token } from '../models/token.model';
import { HttpClient } from '@angular/common/http';
import { LogService } from './log.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { of } from 'rxjs';


class TestHttp {
  post(url, body, options) {}
}


describe('LogService', () => {
  let service: LogService;
  let http: HttpClient;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        AccDataService,
        LogService,
        { provide: HttpClient, useClass: TestHttp }
      ],
    });
    service = TestBed.inject(LogService);
    http = TestBed.get(HttpClient);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return token after call postLogData()', () => {
    const testUser = {username: 'someUsername', password: 'somePass'};
    const testToken = {token: 'abc123'};
    spyOn(http, 'post').and.returnValue(of(testToken));

    service.postLogData(testUser).subscribe((returnedToken: Token) => {
      expect(returnedToken.token).toEqual(testToken.token);
    });
  });

});

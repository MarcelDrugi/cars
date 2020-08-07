import { TestBed, async, ComponentFixture } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';
import { AccDataService } from './shared/services/acc-data.service';
import { RegComponent } from './reg/reg.component';
import { By } from '@angular/platform-browser';
import { of, Observable } from 'rxjs';

describe('AppComponent', () => {

  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let accDataService: AccDataService;
  const returnedClient = { avatar: '', user: {username: 'someUsername', first_name: 'someName', last_name: 'someLastName', email: 'some@email.com'} };
  const token = '12345abcde';
  const username = 'exampleUsername';

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        RouterTestingModule
      ],
      declarations: [
        AppComponent
      ],
      providers: [
        {
          provide: AccDataService,
          useValue: {
            getClient: () => of(JSON.stringify(returnedClient)),
            setClient: () => of(),
            getToken: () => of(token),
            setToken: () => of(),
            getUsername: () => of(username),
            setUsername: () => of(''),
          }
        },
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it(`should have as title 'cars'`, () => {
    expect(component.title).toEqual('cars');
  });

  it('login switch should be false', () => {
    expect(component.login).toEqual(false);
  });

  it('username should be equal username-variable ', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('.username').textContent).toEqual('Jesteś zalogowany jako ' + username);
  });

  it('calling logOut() should call 3 AccDataService methods: setUsername, setToken, setClient', () => {
    accDataService = TestBed.get(AccDataService);
    const setUsername = spyOn(accDataService, 'setUsername');
    const setToken = spyOn(accDataService, 'setToken');
    const setClient = spyOn(accDataService, 'setClient');

    component.logOut();

    expect(setUsername).toHaveBeenCalled();
    expect(setToken).toHaveBeenCalled();
    expect(setClient).toHaveBeenCalled();
  });

  it('calling ngOnInit() should set the username such as return getUsername() in AccDataService', () => {
    accDataService = TestBed.get(AccDataService);
    const testUsername = 'exampleUsername';
    spyOn(accDataService, 'getUsername').and.returnValue(of(testUsername));

    component.ngOnInit();

    expect(component.username).toEqual(testUsername);
  });

  it('subscribing a non-null username from AccDataService should enter text into the class .username in HTML template', () => {
    accDataService = TestBed.get(AccDataService);
    const subscribedUsername = 'exampleUsername';
    spyOn(accDataService, 'getUsername').and.returnValue(of(subscribedUsername));

    component.ngOnInit();
    fixture.detectChanges();
    const displayUsername = fixture.debugElement.query(By.css('.username')).nativeElement;
    expect(displayUsername.textContent).toBe('Jesteś zalogowany jako ' + subscribedUsername);
  });

});

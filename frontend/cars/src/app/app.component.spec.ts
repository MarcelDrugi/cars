import { TestBed, async, ComponentFixture } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';
import { AccDataService } from './shared/services/acc-data.service';
import { RegComponent } from './reg/reg.component';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';

describe('AppComponent', () => {

  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let accDataService: AccDataService;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        RouterTestingModule
      ],
      declarations: [
        AppComponent
      ],
      providers: [AccDataService],
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

  it('username should be null before logging in', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('.username')).toBe(null);
  });

  it('calling logOut() should set the token variable to null', () => {
    accDataService = TestBed.get(AccDataService);
    accDataService.token = '123456789';
    spyOn(accDataService, 'setUsername');

    component.logOut();

    expect(accDataService.token).toBe(null);
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

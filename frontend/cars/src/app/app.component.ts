import { Component, OnInit, AfterViewInit } from '@angular/core';
import { NavigationCancel, NavigationEnd, NavigationError, NavigationStart, Router, RouterEvent } from '@angular/router';
import { AccDataService } from './shared/services/acc-data.service';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'rental-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less', './app.component.sass', './fog.less'],
})
export class AppComponent implements OnInit, AfterViewInit {
  title = 'cars';
  public login = false;
  public username: string;
  public avatar: string;
  public employee: boolean;

  // mobile switch
  public mobile: boolean;
  public smallMobile: boolean;
  public globalClass: string;

  // loading bar switch
  public pageLoader = true;

  constructor(private accDataService: AccDataService, private router: Router, private cdRef:ChangeDetectorRef, ) {
    this.employee = false
  }

  public logOut() {
    this.accDataService.setToken('');
    this.accDataService.setUsername('');
    this.accDataService.setClient('');
    this.router.navigateByUrl('');
  }

  public ngOnInit(): void {

    this.accDataService.getUsername().subscribe((username: string) => {
      this.username = username;
    });

    this.accDataService.getClient().subscribe((client: any) => {
      const parsedClient = JSON.parse(client);
      this.avatar = parsedClient.avatar;
      if (parsedClient.employee) {
        this.employee = true;
      }
    });

    if (window.innerHeight > window.innerWidth) {
      this.mobile = true;
    }
    window.onresize = () => {
      if(window.innerHeight > window.innerWidth) {
        this.mobile = true
      }
      else {
        this.mobile = false
      }
    }
    if(this.mobile) {
      this.globalClass = "long"
    }
    else {
      this.globalClass = ""
    }
  }

  public ngAfterViewInit(): void {
    this.pageLoader = false;

    this.cdRef.detectChanges();
  }
}

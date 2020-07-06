import { Component, OnInit } from '@angular/core';
import { LogService } from './services/log.service';
import { AccDataService } from './shared/services/acc-data.service';

@Component({
  selector: 'rental-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less'],
})
export class AppComponent implements OnInit {
  title = 'cars';
  public login = false;
  public username: string;

  constructor(private logService: LogService, private accDataService: AccDataService) { }

  public logOut() {
    this.accDataService.token = null;
    this.accDataService.setUsername('');
  }
  ngOnInit(): void {
    this.accDataService.getUsername().subscribe((username: string) => {
      this.username = username;
    });
  }
}

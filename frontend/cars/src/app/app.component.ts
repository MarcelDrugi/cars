import { Component, OnInit } from '@angular/core';
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

  constructor(private accDataService: AccDataService) { }

  public logOut() {
    this.accDataService.setToken(null);
    this.accDataService.setUsername('');
  }
  public ngOnInit(): void {
    this.accDataService.getUsername().subscribe((username: string) => {
      this.username = username;
    });
    console.log(this.accDataService.getToken())
  }
}

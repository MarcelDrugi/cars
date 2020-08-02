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
  public avatar: string;

  constructor(private accDataService: AccDataService) { }

  public logOut() {
    this.accDataService.setToken('');
    this.accDataService.setUsername('');
    this.accDataService.setClient('');
  }
  public ngOnInit(): void {
    this.accDataService.getUsername().subscribe((username: string) => {
      this.username = username;
    });

    this.accDataService.getClient().subscribe((client: any) => {
      const parsedClient = JSON.parse(client);
      this.avatar = parsedClient.avatar;
    });

    console.log(this.accDataService.getToken());
  }
}

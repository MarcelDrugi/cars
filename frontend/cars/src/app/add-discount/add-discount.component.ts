import { Component, OnInit } from '@angular/core';
import { Register } from '../models/register.model';
import { Discount } from '../models/discount.model';
import { Client } from '../models/client.model';
import { DiscountService } from '../services/discount.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { Token } from '../models/token.model';
import { Observable, zip } from 'rxjs';
import { tap } from 'rxjs/operators';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'rental-add-discount',
  templateUrl: './add-discount.component.html',
  styleUrls: ['./add-discount.component.less'],
  providers: [DiscountService]
})
export class AddDiscountComponent implements OnInit {

  // data containers
  public clients: Array<Client>;
  public assignedClients: Array<Client>;
  public selectedClient: Client;
  public selectedClientIndex: number;
  public discounts: Array<Discount>;
  public selectedDiscount: Discount;
  public selectedDiscountToRemove: Discount;

  // forms
  public addDiscount: FormGroup;
  public editDiscount: FormGroup;

  // form switches
  public addDiscountButton = false;
  public sentNewDiscount = false;
  public responseError = false;

  constructor(
    private discountService: DiscountService,
    private accDataService: AccDataService,
    private formBuilder: FormBuilder,
  ) { }

  public getClients(): Observable<any>{
    return this.discountService.getClients().pipe(tap(
      (clients: Array<Client>) => {
        this.clients = clients.slice(0, -1);
        this.accDataService.setToken(clients.slice(-1)[0]['token']);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
    ));
  }

  public getDiscounts(): void {
    this.discountService.getDiscounts().subscribe(
      (discounts: any) => {
        this.discounts = discounts.slice(0, -1);
        this.accDataService.setToken(discounts.slice(-1)[0]['token']);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
    );
  }

  public clientSelection(client): void{
    this.addDiscountButton = false;
    this.selectedClientIndex = client;
    this.selectedClient =  this.clients[this.selectedClientIndex];
  }

  public delDiscount(discountId: string) {
    const discountData = {
      client: this.selectedClient.user.username,
      discount: discountId,
      acction: 'remove',
    };
    this.discountService.assignDiscounts(discountData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
      () => {
        this.getClients().subscribe(() => {
          const b = this.clientSelection(this.selectedClientIndex);
        });
      }
    );
  }

  public assignDiscount(acction: string) {
    const discountData = {
      client: this.selectedClient.user.username,
      discount: this.selectedDiscount.id,
      acction,
    };
    this.discountService.assignDiscounts(discountData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
      () => {
        this.getClients().subscribe(() => {
          const b = this.clientSelection(this.selectedClientIndex);
        });
      }
    );
  }

  private postNewDiscount(discountData: any): void {
    this.discountService.postNewDiscount(discountData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
        this.sentNewDiscount = false;
        this.addDiscount.reset();
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
        else {
          this.responseError = true;
        }
      },
      () => {
        this.getDiscounts();
      }
    );
  }

  public validNewDiscount(): void {
    this.sentNewDiscount = true;

    if (this.addDiscount.valid) {
      const discountData = {
        discount_code: parseInt(this.addDiscount.value.discount_code, 10),
        discount_value: parseFloat(this.addDiscount.value.discount_value) / 100
      };
      console.log('val:  ', discountData.discount_value)
      this.postNewDiscount(discountData);
    }
  }

  public removeDiscount(): void {
    this.discountService.delDiscount(this.selectedDiscountToRemove.id).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
      },
      error => {
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
      () => {
        this.getDiscounts();
      }
    );
  }

  public discountSelection(discount: Event) {
    this.addDiscountButton = true;
    this.selectedDiscount = this.discounts[discount.target['value']];
  }

  public discountToRemove(discount: Event) {
    this.assignedClients = [ ];
    this.selectedDiscountToRemove = this.discounts[discount.target['value']];
    this.clients.forEach((client: Client) => {
      client.discount.forEach((el: any) => {
        if (el.discount_code === this.selectedDiscountToRemove.discount_code) {
          this.assignedClients.push(client);
        }
      });
    });
  }

  ngOnInit(): void {
    this.addDiscount = this.formBuilder.group({
      discount_code: ['', Validators.required],
      discount_value: ['', Validators.required],
    });

    this.getClients().subscribe(() => { });
    this.getDiscounts();
  }

}

import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule, HttpClientXsrfModule} from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RegComponent } from './reg/reg.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LogComponent } from './log/log.component';
import {AccDataService} from './shared/services/acc-data.service';
import {BackendInfoService} from './shared/services/backend-info.service';
import { AddEditCarComponent } from './add-edit-car/add-edit-car.component';
import { GetPublicDataService } from './services/get-public-data.service';
import { AddSegmentComponent } from './add-segment/add-segment.component';
import { HomepageComponent } from './homepage/homepage.component';
import { FleetComponent } from './fleet/fleet.component';
import { AboutComponent } from './about/about.component';
import { LocationComponent } from './location/location.component';
import { RulesComponent } from './rules/rules.component';
import { CarDetailsComponent } from './car-details/car-details.component';
import { OrderComponent } from './order/order.component';
import { OrderService } from './shared/services/order.service';
import { AddDiscountComponent } from './add-discount/add-discount.component';
import { SuccessComponent } from './success/success.component';
import { FailComponent } from './fail/fail.component';

@NgModule({
  declarations: [
    AppComponent,
    RegComponent,
    LogComponent,
    AddEditCarComponent,
    AddSegmentComponent,
    HomepageComponent,
    FleetComponent,
    AboutComponent,
    LocationComponent,
    RulesComponent,
    CarDetailsComponent,
    OrderComponent,
    AddDiscountComponent,
    SuccessComponent,
    FailComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    HttpClientXsrfModule.withOptions({
      cookieName: 'XSRF-TOKEN',
      headerName: 'X-XSRF-TOKEN',
    }),
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [AccDataService, BackendInfoService, GetPublicDataService, OrderService],
  bootstrap: [AppComponent]
})
export class AppModule { }

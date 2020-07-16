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

@NgModule({
  declarations: [
    AppComponent,
    RegComponent,
    LogComponent,
    AddEditCarComponent,
    AddSegmentComponent,
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
  providers: [AccDataService, BackendInfoService, GetPublicDataService],
  bootstrap: [AppComponent]
})
export class AppModule { }

import { CarDetailsComponent } from './car-details/car-details.component';
import { RulesComponent } from './rules/rules.component';
import { LocationComponent } from './location/location.component';
import { AboutComponent } from './about/about.component';
import { FleetComponent } from './fleet/fleet.component';
import { HomepageComponent } from './homepage/homepage.component';
import { RegComponent } from './reg/reg.component';
import { LogComponent } from './log/log.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AddEditCarComponent } from './add-edit-car/add-edit-car.component';
import { AddSegmentComponent } from './add-segment/add-segment.component';
import { OrderComponent } from './order/order.component';
import { AddDiscountComponent } from './add-discount/add-discount.component';
import { SuccessComponent } from './success/success.component';
import { FailComponent } from './fail/fail.component';


const routes: Routes = [
  { path: 'signup', component: RegComponent },
  { path: 'signin', component: LogComponent },
  { path: 'addcar', component: AddEditCarComponent },
  { path: 'addsegment', component: AddSegmentComponent },

  { path: 'homepage', component: HomepageComponent },
  { path: 'fleet', component: FleetComponent },
  { path: 'about', component: AboutComponent },
  { path: 'location', component: LocationComponent },
  { path: 'rules', component: RulesComponent },
  { path: 'cardetails', component: CarDetailsComponent },
  { path: 'order', component: OrderComponent },
  { path: 'adddiscount', component: AddDiscountComponent },
  { path: 'success', component: SuccessComponent },
  { path: 'fail', component: FailComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

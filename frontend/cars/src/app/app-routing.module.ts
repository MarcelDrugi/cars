import { RegComponent } from './reg/reg.component';
import { LogComponent } from './log/log.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AddEditCarComponent } from './add-edit-car/add-edit-car.component';
import { AddSegmentComponent } from './add-segment/add-segment.component';


const routes: Routes = [
  { path: 'signup', component: RegComponent},
  { path: 'signin', component: LogComponent},
  { path: 'addcar', component: AddEditCarComponent},
  { path: 'addsegment', component: AddSegmentComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

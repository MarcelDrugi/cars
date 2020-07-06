import { RegComponent } from './reg/reg.component';
import { LogComponent } from './log/log.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';


const routes: Routes = [
  { path: 'signup', component: RegComponent},
  { path: 'signin', component: LogComponent}
];;

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

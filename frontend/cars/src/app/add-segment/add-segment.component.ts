import { Component, OnInit } from '@angular/core';
import { AddEditCarService } from '../services/add-edit-car.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Segment } from '../models/segment.model';
import { Pricing } from '../models/pricing.model';
import { Token } from '../models/token.model';

@Component({
  selector: 'rental-add-segment',
  templateUrl: './add-segment.component.html',
  styleUrls: ['./add-segment.component.less']
})
export class AddSegmentComponent implements OnInit {

  public form: FormGroup;

  public sent = false;
  public confirmation = false;

  constructor(
    private addEditCarService: AddEditCarService,
    private accDataService: AccDataService,
    private formBuilder: FormBuilder,
  ) { }

  public validData(): void {
    this.sent = true;

    const segmentData = new Segment();
    const pricingData = new Pricing();

    if (this.form.valid) {
      pricingData.hour = this.form.value.hour;
      pricingData.day = this.form.value.day;
      pricingData.week = this.form.value.week;

      segmentData.name = this.form.value.name;
      segmentData.pricing = pricingData;

      console.log(segmentData);
      this.postSegment(segmentData);
    }
  }

  private postSegment(segmentData: Segment): void {
    this.addEditCarService.postSegment(segmentData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
        if (resp.token !== '') {
          this.confirmation = true;
          this.form.reset();
          this.sent = false;
        }
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      name: ['', Validators.required],
      hour: ['', [Validators.pattern('[0-9]{1,3}\.[0-9]{2}'), Validators.required]],
      day: ['', [Validators.pattern('[0-9]{1,4}\.[0-9]{2}'), Validators.required]],
      week: ['', [Validators.pattern('[0-9]{1,5}\.[0-9]{2}'), Validators.required]],
    });
  }

}

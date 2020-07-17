import { Component, OnInit } from '@angular/core';
import { AddEditCarService } from '../services/add-edit-car.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Segment } from '../models/segment.model';
import { Pricing } from '../models/pricing.model';
import { Token } from '../models/token.model';
import { GetPublicDataService } from '../services/get-public-data.service';

@Component({
  selector: 'rental-add-segment',
  templateUrl: './add-segment.component.html',
  styleUrls: ['./add-segment.component.less']
})
export class AddSegmentComponent implements OnInit {

  public segmentForm: FormGroup;
  public existingSegmentForm: FormGroup;
  public segments: Array<Segment>;
  public selectedSegment: Segment;

  public sent = false;
  public editionSent = false;
  public confirmation = false;
  public editSegment = false;

  constructor(
    private addEditCarService: AddEditCarService,
    private accDataService: AccDataService,
    private formBuilder: FormBuilder,
    private getPublicDataService: GetPublicDataService,
  ) { }

  public validData(kind: string): void {

    let data: any;
    if (kind === 'create') {
      this.sent = true;
      data = this.segmentForm;
    }
    else {
      this.editionSent = true;
      data = this.existingSegmentForm;
    }

    const segmentData = new Segment();
    const pricingData = new Pricing();

    if (data.valid) {
      pricingData.id = this.selectedSegment.pricing.id;
      pricingData.hour = data.value.hour;
      pricingData.day = data.value.day;
      pricingData.week = data.value.week;

      segmentData.name = data.value.name;
      segmentData.pricing = pricingData;

      if (kind === 'create') {
        this.postSegment(segmentData);
      }
      else {
        segmentData.id = this.selectedSegment.id;
        this.updateSegment(segmentData);
      }
    }
  }

  private postSegment(segmentData: Segment): void {
    this.addEditCarService.postSegment(segmentData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
        if (resp.token !== '') {
          this.confirmation = true;
          this.segmentForm.reset();
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

  private updateSegment(segmentData: Segment): void {
    this.addEditCarService.updateSegment(segmentData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
        if (resp.token !== '') {
          this.confirmation = true;
          this.existingSegmentForm.reset();
          this.editionSent = false;
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

  private getSegments(): void {
    this.getPublicDataService.getSegment().subscribe(
      (segments: any) => {
        this.accDataService.setToken(segments.slice(-1)[0].token);
        this.segments = segments.slice(0, -1);
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  public segmentSelection(segment): void {
    this.editSegment = true;
    this.segments.forEach(
      (iteratedSegment: Segment) => {
        if (iteratedSegment.id.toString() === segment.target.value) {
          this.selectedSegment = iteratedSegment;
        }
      }
    );
    console.log(this.selectedSegment)

    this.existingSegmentForm = this.formBuilder.group({
      name: [this.selectedSegment.name, Validators.required],
      hour: [this.selectedSegment.pricing.hour, [Validators.pattern('[0-9]{1,3}\.[0-9]{2}'), Validators.required]],
      day: [this.selectedSegment.pricing.day, [Validators.pattern('[0-9]{1,4}\.[0-9]{2}'), Validators.required]],
      week: [this.selectedSegment.pricing.week, [Validators.pattern('[0-9]{1,5}\.[0-9]{2}'), Validators.required]],
    });
    //this.addSegment(this.selectedCar.segment['id'])
  }

  ngOnInit(): void {
    this.segmentForm = this.formBuilder.group({
      name: ['', Validators.required],
      hour: ['', [Validators.pattern('[0-9]{1,3}\.[0-9]{2}'), Validators.required]],
      day: ['', [Validators.pattern('[0-9]{1,4}\.[0-9]{2}'), Validators.required]],
      week: ['', [Validators.pattern('[0-9]{1,5}\.[0-9]{2}'), Validators.required]],
    });

    this.getSegments();
  }

}

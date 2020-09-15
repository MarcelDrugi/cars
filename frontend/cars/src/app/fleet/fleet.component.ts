import { Component, OnInit } from '@angular/core';
import { GetPublicDataService } from '../services/get-public-data.service';
import { Segment } from '../models/segment.model';
import { Car } from '../models/car.model';
import { AccDataService } from '../shared/services/acc-data.service';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'rental-fleet',
  templateUrl: './fleet.component.html',
  styleUrls: ['./fleet.component.less']
})
export class FleetComponent implements OnInit {

  // data containers
  public segments: Array<Segment>;
  public cars: Array<Car>;
  public selectedSegment: number;
  public selectedSegmentId: number;

  constructor(
    private getPublicDataService: GetPublicDataService,
    private accDataService: AccDataService,
  ) { }

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
      },
      () => {
        this.selectedSegment = 0;
        this.selectedSegmentId = this.segments[this.selectedSegment].id
        console.log(this.selectedSegmentId)
      }
    );
  }

  public getCars(): void {
    console.log('pobieram auta')
    this.getPublicDataService.getCars().subscribe(
      (cars: Array<Car>) => {
        this.cars = cars;
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }

  public checkSegment(event: any) {
    this.selectedSegment = event.target.value
    this.selectedSegmentId = this.segments[this.selectedSegment].id
  }

  ngOnInit(): void {
    this.getCars();
    this.getSegments();
  }

}

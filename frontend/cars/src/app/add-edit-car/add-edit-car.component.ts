import { Component, OnInit } from '@angular/core';
import { AddEditCarService } from '../services/add-edit-car.service';
import { AccDataService } from '../shared/services/acc-data.service';
import { Segment } from '../models/segment.model';
import { Car } from '../models/car.model';
import { GetPublicDataService } from '../services/get-public-data.service';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Token } from '../models/token.model';

@Component({
  selector: 'rental-add-edit-car',
  templateUrl: './add-edit-car.component.html',
  styleUrls: ['./add-edit-car.component.less'],
  providers: [AddEditCarService]
})
export class AddEditCarComponent implements OnInit {

  public segments: Array<Segment>;
  public form: FormGroup;

  private uploadedData: Car;
  private img: File;
  private segment: number;

  public sent = false;
  private imgValidator = false;
  public typeError = false;
  public sizeError = false;
  public confirmation = false;

  public maxSize = 4096000;

  constructor(
    private addEditCarService: AddEditCarService,
    private accDataService: AccDataService,
    private getPublicDataService: GetPublicDataService,
    private formBuilder: FormBuilder,
  ) { }

  private postCar(carData: FormData): void {
    this.addEditCarService.postCar(carData).subscribe(
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

  public validData(): void {
    this.sent = true;
    if (this.form.valid && this.imgValidator) {

      const carData = new FormData();
      this.uploadedData = this.form.getRawValue();

      carData.append('brand', this.uploadedData.brand);
      carData.append('model', this.uploadedData.model);
      carData.append('regNumber', this.uploadedData.regNumber);
      carData.append('description', this.uploadedData.description);
      carData.append('img', this.img);
      carData.append('segment', this.segment.toString());

      this.postCar(carData);
    }
  }

  public validImg(img: FileList): void {

    this.imgValidator = false;
    this.sizeError = false;
    this.typeError = false;

    this.img = img.item(0);

    if (this.img.size > this.maxSize) {
      this.sizeError = true;
    }
    else if (!['image/png', 'image/jpg', 'image/jpeg', 'image/gif'].includes(this.img.type)) {
      this.typeError = true;
    }
    else {
      this.imgValidator = true;
    }
  }

  public addSegment(nb: number): void {
    this.segment = nb;
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
  /*
  public getCars(): void {
    this.getPublicDataService.getCars().subscribe(
      (cars: Array<Car>) => {
        console.log(cars);
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      }
    );
  }
  */

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      brand: ['', Validators.required],
      model: ['', Validators.required],
      regNumber: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(8)]],
      segment: ['', ],
      img: ['', ],
      description: ['', [Validators.maxLength(2048)]]
    });

    this.getSegments();
  }

}

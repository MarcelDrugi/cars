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

  // data containers
  public segments: Array<Segment>;
  public addCarForm: FormGroup;
  public existingCarForm: FormGroup;

  private uploadedData: Car;
  private img: File;
  private segment: number;
  public cars: Array<Car>;
  public selectedCar: Car;
  public createImgSrc: string;
  public changeImgSrc: string;

  // switches for displaying data in the template
  public sent = false;
  public editionSent = false;
  public typeError = false;
  public sizeError = false;
  public createConfirmation = false;
  public updateConfirmation = false;
  public delConfirmation = false;
  public editCar = false;

  // validation form data
  private imgValidator = true;
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
          this.createConfirmation = true;
          this.addCarForm.reset();
          this.sent = false;
          this.createImgSrc = null;
          this.img = null;
          this.segment = null;
        }
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
      () => {
        this.getCars();
      }
    );
  }

  public validData(kind: string): void {
    this.createConfirmation = false;
    this.updateConfirmation = false;
    this.delConfirmation = false;

    if (kind === 'create') {
      this.sent = true;
    }
    else {
      this.editionSent = true;
      if (this.addCarForm.value['img'] === '') {
        this.imgValidator = true;
      }
      this.editionSent = true;
    }

    if ((this.addCarForm.valid  || this.existingCarForm.valid) && this.imgValidator) {
      const carData = new FormData();
      if (kind === 'create') {
        this.uploadedData = this.addCarForm.getRawValue();
      }
      else {
        this.uploadedData = this.existingCarForm.getRawValue();
      }

      carData.append('brand', this.uploadedData.brand);
      carData.append('model', this.uploadedData.model);
      carData.append('reg_number', this.uploadedData.reg_number);
      carData.append('description', this.uploadedData.description);
      carData.append('img', this.img);
      carData.append('segment', this.segment.toString());

      if (!this.img) {
        carData.append('img', '');
      }

      if (kind === 'create') {
        this.postCar(carData);
      }
      else {
        carData.append('id', this.selectedCar.id.toString());
        this.updateCar(carData);
      }
    }
  }

  public validImg(img: FileList | Event | any, kind: string): void {

    this.imgValidator = false;
    this.sizeError = false;
    this.typeError = false;
    console.log('WSZEDŁEM !!!!!!!!!')

    if (img instanceof FileList) {
      this.img = img.item(0);
    }
    else {
      const reader = new FileReader();
      reader.readAsDataURL(img.target['files'][0]);

      reader.onload = (event) => {
        if (kind === 'create'){
          this.createImgSrc = '' + event.target.result;
        }
        else {
          this.changeImgSrc = '' + event.target.result;
        }
      };
      this.img = img.target['files'].item(0);
    }

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

  public getCars(): void {
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

  public carSelection(car): void {
    this.editCar = true;
    this.changeImgSrc = null;
    this.cars.forEach(
      (iteratedCar: Car) => {
        if (iteratedCar.reg_number === car.target.value) {
          this.selectedCar = iteratedCar;
        }
      },
    );
    if (this.selectedCar.img) {
      this.changeImgSrc = '' + this.selectedCar.img;
    }
    this.existingCarForm = this.formBuilder.group({
      brand: [this.selectedCar.brand, Validators.required],
      model: [this.selectedCar.model, Validators.required],
      reg_number: [this.selectedCar.reg_number, [Validators.required, Validators.minLength(6), Validators.maxLength(8)]],
      segment: ['', ],
      img: ['', ],
      description: [this.selectedCar.description, [Validators.maxLength(2048)]]
    });
    this.addSegment(this.selectedCar.segment['id'])
  }

  private updateCar(carData: FormData): void {
    this.addEditCarService.updateCar(carData).subscribe(
      (resp: Token) => {
        this.accDataService.setToken(resp.token);
        if (resp.token !== '') {
          this.updateConfirmation = true;
          this.existingCarForm.reset();
          this.editionSent = false;
          this.changeImgSrc = null;
          this.img = null;
          this.segment = null;
        }
      },
      error => {
        console.log(error);
        if (error.statusText === 'Unauthorized' && error.status === 401) {
          this.accDataService.setToken('');
        }
      },
      () => {
        this.getCars();
      }
    );
  }

  deleteCar(): void {
    this.createConfirmation = false;
    this.updateConfirmation = false;

    this.addEditCarService.deleteCar(this.selectedCar.id).subscribe(
      (token: Token) => {
        this.existingCarForm.reset();
        this.changeImgSrc = null;
        this.delConfirmation = true;
        this.cars = this.cars.filter((car: Car) => car.reg_number !== this.selectedCar.reg_number);

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
    this.addCarForm = this.formBuilder.group({
      brand: ['', Validators.required],
      model: ['', Validators.required],
      reg_number: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(8)]],
      segment: ['', ],
      img: ['', ],
      description: ['', [Validators.maxLength(2048)]]
    });

    this.getSegments();
    this.getCars();
  }

}

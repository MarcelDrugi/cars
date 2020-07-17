export class Car {
  id: number;
  brand: string;
  model: string;
  reg_number: string;
  segment: number;
  img: File;
  description: string;

  constructor() {
    this.description = '';
  }
}

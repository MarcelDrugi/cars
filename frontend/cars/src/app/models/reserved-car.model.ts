import { Segment } from './segment.model';

export class ReservedCar {
  id: number;
  brand: string;
  model: string;
  reg_number: string;
  segment: Segment;
  img: File;
  description: string;
}

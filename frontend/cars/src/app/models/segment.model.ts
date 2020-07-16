import { Pricing } from './pricing.model';

export class Segment {
  id: number;
  name: string;
  pricing: Pricing;

  constructor() {
    this.id = 0;
  }
}

import { Car } from './car.model';
import { ReservedCar } from './reserved-car.model';

export class SavedReservation {
  id: number;
  begin: string;
  end: string;
  car: ReservedCar;
}

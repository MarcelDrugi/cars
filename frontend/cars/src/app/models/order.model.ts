import { Client } from './client.model';

export class Order {
  id: number;
  client: Client;
  cost: number;
  paid: boolean;
  canceled: boolean;
  payment_id: string;
  comments: string;
}

export interface TagDTO {
  id: string;
  name: string;
  color: string;
}

export interface TagUpsertDTO {
  id?: string;
  name?: string;
  color?: string;
}

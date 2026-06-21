export type User = {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type RegisterInput = {
  full_name: string;
  email: string;
  password: string;
};

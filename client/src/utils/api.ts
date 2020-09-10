
export interface ApiError {
  error: boolean;
  error_message: string;
}

export interface ApiSignUpRequest {
  username: string;
  password: string;
}

interface SignUpResponse {
  success: boolean;
}

export type ApiSignUpResponse = SignUpResponse | ApiError

export interface ApiLoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  next: string;
}

export type ApiLoginResponse = LoginResponse | ApiError
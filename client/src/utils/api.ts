
export interface ApiError {
  error: boolean;
  // eslint-disable-next-line camelcase
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

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface ApiInfoRequest { }

interface InfoResponse {
  success: boolean;
  username: string;
  // eslint-disable-next-line camelcase
  last_update: number;
}

export type ApiInfoResponse = InfoResponse | ApiError

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface ApiImageRequest { }

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface ApiImagesRequest { }

export interface ImageObject {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  name: string;
}

export interface ImageResponse {
  id: number;
  // eslint-disable-next-line camelcase
  original_filename: string;
  owner: string;
  // eslint-disable-next-line camelcase
  original_width?: number;
  // eslint-disable-next-line camelcase
  original_height?: number;
  objects: Array<ImageObject>
}

export type ApiImagesResponse = Array<ImageResponse> | ApiError

export type ApiImageResponse = ImageResponse | ApiError

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface ApiDeleteImageRequest { }

interface DeleteImageResponse {
  success: boolean;
  username: string;
}

export type ApiDeleteImageResponse = DeleteImageResponse | ApiError

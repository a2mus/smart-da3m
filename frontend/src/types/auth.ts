export type UserRole = 'STUDENT' | 'PARENT' | 'EXPERT'

export interface User {
  id: string
  email: string | null
  role: UserRole
  language: 'AR' | 'FR'
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface PinCredentials {
  pinCode: string
}

export interface AuthResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  user: User
}

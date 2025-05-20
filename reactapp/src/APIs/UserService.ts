import axios from "axios";
import { BASIC_API_URL } from "@/main";
import type { User } from "@/auth";

export type LoginData = {
  email: string;
  password: string;
};

export type RegesterData = {
  username: string;
  email: string;
  password: string;
};

export default class UserService {
  static async login(data: LoginData): Promise<boolean> {
    try {
      await axios.post(`${BASIC_API_URL}/login`, data, {
        withCredentials: true,
      });
      return true;
    } catch (error) {
      return false;
    }
  }

  static async regester(data: RegesterData): Promise<User | null> {
    try {
      const response = await axios.post(`${BASIC_API_URL}/regestration`, data, {
        withCredentials: true,
      });
      return response.status === 200 ? (response.data as User) : null;
    } catch (error) {
      return null;
    }
  }

  static async logout(): Promise<boolean> {
    try {
      await axios.delete(`${BASIC_API_URL}/logout`, { withCredentials: true });
      return true;
    } catch (error) {
      return false;
    }
  }

  static async getUser(): Promise<User | null> {
    try {
      const response = await axios.get(`${BASIC_API_URL}/user`, {
        withCredentials: true,
      });
      return response.status === 200 ? (response.data as User) : null;
    } catch {
      return null;
    }
  }
}

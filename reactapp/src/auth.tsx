import * as React from "react";
import UserService, {
  type LoginData,
  type RegesterData,
} from "./APIs/UserService";

export type User = {
  id: string;
  username: string;
};

export interface AuthContext {
  isAuthenticated: () => Promise<boolean>;
  login: (data: LoginData) => Promise<boolean>;
  logout: () => Promise<void>;
  regester: (data: RegesterData) => Promise<User | null>;
  user: User | null;
}

const AuthContext = React.createContext<AuthContext | null>(null);

const key = "auth.user";

function getStoredUser() {
  let user = localStorage.getItem(key);
  if (user) {
    return JSON.parse(user) as User;
  }
  return null;
}

function setStoredUser(user: User | null) {
  if (user) {
    localStorage.setItem(key, JSON.stringify(user));
  } else {
    localStorage.removeItem(key);
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(getStoredUser());
  const isAuthenticated = async () => !!(await UserService.getUser());

  const regester = React.useCallback(async (data: RegesterData) => {
    const user = await UserService.regester(data);
    setStoredUser(user);
    setUser(user);
    return user;
  }, []);

  const logout = React.useCallback(async () => {
    if (await UserService.logout()) {
      setStoredUser(null);
      setUser(null);
    }
  }, []);

  const login = React.useCallback(async (data: LoginData) => {
    if (await UserService.login(data)) {
      const user = await UserService.getUser();
      setStoredUser(user);
      setUser(user);
      return true;
    }
    return false;
  }, []);

  React.useEffect(() => {
    async function init() {
      const user = await UserService.getUser();
      setStoredUser(user);
      setUser(user);
    }
    init();
  }, []);

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, login, logout, regester }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

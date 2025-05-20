import { Outlet, createRootRouteWithContext } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

import Header from "../components/Header";

import type { AuthContext } from "../auth";

interface MyRouterContext {
  auth: AuthContext;
}
export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: () => (
    <div>
      <Header />

      <Outlet />
    </div>
  ),
});

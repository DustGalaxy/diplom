import { Outlet, createRootRouteWithContext } from "@tanstack/react-router";

import Header from "../components/Header";

import type { AuthContext } from "../auth";
import Footer from "@/components/Footer";

interface MyRouterContext {
  auth: AuthContext;
}
export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: () => (
    <div className="min-h-screen grid grid-rows-[auto_1fr_auto]">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  ),
});

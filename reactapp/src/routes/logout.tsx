import { useAuth } from "@/auth";
import { createFileRoute, Navigate } from "@tanstack/react-router";

export const Route = createFileRoute("/logout")({
  component: RouteComponent,
});

function RouteComponent() {
  const auth = useAuth();
  auth.logout();
  Navigate({ to: "/login" });
  return <div>logout...</div>;
}

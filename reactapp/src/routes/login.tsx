import React from "react";

import {
  createFileRoute,
  redirect,
  useNavigate,
  useRouter,
  useRouterState,
} from "@tanstack/react-router";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useAuth } from "@/auth";
import { sleep } from "@/lib/utils";

const fallback = "/home" as const;

const formSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

const loginRedirectSchema = z.object({
  redirect: z.string().optional().catch(""),
});

export const Route = createFileRoute("/login")({
  beforeLoad: async ({ context, search }) => {
    if (await context.auth.isAuthenticated()) {
      throw redirect({ to: search.redirect || fallback });
    }
  },
  component: Login,
  validateSearch: loginRedirectSchema,
});

function Login() {
  const navigate = useNavigate({ from: "/login" });
  const auth = useAuth();
  const router = useRouter();
  const search = Route.useSearch();
  const isLoading = useRouterState({ select: (s) => s.isLoading });
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsSubmitting(true);
    try {
      const success = await auth.login({
        email: values.email,
        password: values.password,
      });

      await router.invalidate();
      await sleep(1);
      await navigate({ to: search.redirect || fallback });
    } catch (error) {
      console.error("Error logging in: ", error);
    } finally {
      setIsSubmitting(false);
    }
  }

  const isLoggingIn = isLoading || isSubmitting;
  return (
    <div className="flex justify-center items-center m-10 p-10 ">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-8 bg-slate-700 m-10 p-10 rounded-2xl w-md h-[500px] flex flex-col justify-between"
        >
          <div className="h-screen ">
            <Label className="h-1/3 text-3xl w-full justify-center text-white">
              Вхід до <span className="text-[#ff0000]">Ravluk!</span>
            </Label>
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem className="h-1/3">
                  <FormLabel>Ім'я користувача</FormLabel>
                  <FormControl>
                    <Input placeholder="shadcn" type="email" {...field} />
                  </FormControl>

                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem className="h-1/3">
                  <FormLabel>Пароль</FormLabel>
                  <FormControl>
                    <Input placeholder="87654321" type="password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <Button
            type="submit"
            variant="outline"
            className="w-full bg-slate-700 my-4"
            disabled={isLoggingIn}
          >
            {isLoggingIn ? "Завантаження..." : "Увійти"}
          </Button>
        </form>
      </Form>
    </div>
  );
}

import StatService from "@/APIs/StatService";
import TrackList from "@/components/TrackList";
import { createFileRoute } from "@tanstack/react-router";
import React from "react";

export const Route = createFileRoute("/account")({
  loader: async () => {
    const result = await StatService.getHistory();
    if (result) {
      return result.sort((a, b) => {
        return (
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      });
    }
    return [];
  },
  component: RouteComponent,
});

function RouteComponent() {
  const data = Route.useLoaderData();
  const tracks = React.useMemo(() => {
    console.log("History data loaded:", data);
    return data?.map((item) => item.track) ?? [];
  }, [data]);
  return (
    <div>
      <div className="text-lg md:text-2xl text-white text-center my-4">
        Історія прослуховувань
      </div>

      <div>
        {data?.length === 0 && <div>Історія порожня</div>}
        {data && <TrackList tracks_={tracks} />}
      </div>
    </div>
  );
}

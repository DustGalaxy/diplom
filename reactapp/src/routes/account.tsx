import StatService from "@/APIs/StatService";
import TrackList from "@/components/TrackList";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/account")({
  loader: async () => {
    const result = await StatService.getHistory();
    if (result) {
      return result.sort((a, b) => {
        return (
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
      });
    }
  },
  component: RouteComponent,
});

function RouteComponent() {
  const data = Route.useLoaderData();
  return (
    <div>
      <div>Історія прослуховувань</div>
      <div>
        {data?.length === 0 && <div>Історія порожня</div>}
        {data && <TrackList tracks_={data.map((item) => item.track)} />}
      </div>
    </div>
  );
}

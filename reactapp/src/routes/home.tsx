import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";

import PlaylistItem from "@/components/PlaylistItem";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import PlaylistService, { type TrackData } from "@/APIs/PlaylistService";
import { useAuth } from "@/auth";

export const Route = createFileRoute("/home")({
  component: Home,
  beforeLoad: async ({ context, location }) => {
    if (!(await context.auth.isAuthenticated())) {
      throw redirect({
        to: "/login",
        search: {
          redirect: location.href,
        },
      });
    }
  },
  loader: async () => {
    const playlists = await PlaylistService.getPlaylists();
    return playlists;
  },
});

export default function Home() {
  const data = Route.useLoaderData();
  const [playlists, setPlaylists] = React.useState(data);
  const [trackQuery, setTrackQuery] = React.useState("");
  const [seachedTracks, setSeachedTracks] = React.useState<TrackData[]>([]);

  const auth = useAuth();

  const createPlaylist = async () => {
    const playlist = await PlaylistService.newPlaylist("новий плейлиcт");
    if (playlist) {
      setPlaylists([...playlists, playlist]);
    }
  };

  const fetchTracks = async () => {
    const tracks = await PlaylistService.getTracksByQuery(trackQuery);
    if (tracks) {
      setSeachedTracks(tracks);
    }
  };

  return (
    <div className="main h-screen ">
      <div className="app w-full items-center p-4"></div>
      <Tabs
        defaultValue="playlists"
        className="w-[98%]  flex  justify-self-center"
      >
        <TabsList className="w-full bg-gray-600 flex justify-self-center ">
          <TabsTrigger
            className="text-white data-[state=active]:bg-gray-700"
            value="playlists"
          >
            Плейлисти
          </TabsTrigger>
          <TabsTrigger
            className="text-white data-[state=active]:bg-gray-700"
            value="music"
          >
            Треки
          </TabsTrigger>
        </TabsList>
        <TabsContent value="playlists">
          <Button
            variant={"ghost"}
            className="w-[98%] justify-self-center bg-gray-600 my-4 flex items-center "
            onClick={createPlaylist}
          >
            <div className="text-lg md:text-2xl ">+ Створити плейлист</div>
          </Button>
          {playlists.map((item, index) => (
            <PlaylistItem
              playlist_title={item.name}
              playlist_id={item.id}
              amount={item.tracks_amount}
            />
          ))}
        </TabsContent>
        <TabsContent value="music">
          <div className="flex mb-4">
            <Button
              onClick={fetchTracks}
              variant={"ghost"}
              className=" bg-gray-600 mr-4 "
            >
              Знайти треки
            </Button>
            <Input
              placeholder="Назва треку"
              onChange={(e) => setTrackQuery(e.target.value)}
              value={trackQuery}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

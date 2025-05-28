import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";

import PlaylistItem from "@/components/PlaylistItem";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import PlaylistService, { type TrackData } from "@/APIs/PlaylistService";
import TrackList from "@/components/TrackList";
import { Input } from "@/components/ui/input";
import StatService, { type ArtistData } from "@/APIs/StatService";

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
  const [tracks, setTracks] = React.useState<TrackData[]>([]);
  const [artists, setArtists] = React.useState<ArtistData[]>([]);
  const [filter, setFilter] = React.useState("");
  const createPlaylist = async () => {
    const playlist = await PlaylistService.newPlaylist("новий плейлиcт");
    if (playlist) {
      setPlaylists([...playlists, playlist]);
    }
  };

  const findTracks = async () => {
    const tracks = await PlaylistService.getTracksByQuery(filter);
    if (tracks) {
      setTracks(tracks);
    }
  };

  const fetchArtists = async () => {
    const today = new Date(Date.now());
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);

    const artists_data = await StatService.artistStat(yesterday, today);
    if (artists_data) {
      setArtists(artists_data);
    }
  };

  return (
    <div className="main ">
      <div className="app w-full items-center p-4"></div>
      <Tabs
        defaultValue="playlists"
        className="w-[98%]  flex  justify-self-center"
      >
        <TabsList className="w-full bg-gray-600 flex justify-self-center ">
          <TabsTrigger
            className="text-white data-[state=active]:bg-gray-700"
            value="atrists"
            onClick={fetchArtists}
          >
            Артисти
          </TabsTrigger>
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
        <TabsContent value="atrists">
          <div className="text-lg md:text-2xl text-white text-center my-4">
            Популярні артисти за останні 24 години
          </div>
          {artists.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {artists.map((artist, index) => (
                <div
                  key={index}
                  className="bg-gray-700 p-4 rounded-lg text-center"
                >
                  <div className="text-xl font-bold">{artist.artist}</div>
                  <div className="text-gray-400">
                    Прослуховувань: {artist.play_count}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm md:text-base text-gray-400 text-center">
              Немає даних про популярних артистів
            </div>
          )}
        </TabsContent>
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
          {/* <div className="flex mb-4">
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
          </div> */}
          <div className="flex mb-2 md:mb-4">
            <Button
              onClick={findTracks}
              disabled={!filter}
              variant={"ghost"}
              className=" bg-gray-600 mr-4 "
            >
              Знайти
            </Button>
            <Input
              placeholder="Назва трека"
              onChange={(e) => setFilter(e.target.value)}
              value={filter}
              className="text-sm md:text-base"
            />
          </div>
          <TrackList tracks_={tracks} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

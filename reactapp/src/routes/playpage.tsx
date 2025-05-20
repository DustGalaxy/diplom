import { createFileRoute, redirect } from "@tanstack/react-router";
import React from "react";
import YoutubePlayer from "../components/YoutubePlayer";

import PlayList from "../components/PlayList";
import PlaylistService, { type TrackData } from "@/APIs/PlaylistService";
import { z } from "zod";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { isYouTubeVideoURL } from "@/lib/utils";

const playlistSearchSchema = z.object({
  p: z.string(),
});

type PlaylistSearch = z.infer<typeof playlistSearchSchema>;

export const Route = createFileRoute("/playpage")({
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
  validateSearch: playlistSearchSchema,
  loaderDeps: ({ search }) => ({
    p: (search as { p: string }).p,
  }),
  loader: async ({ deps: { p } }) => await PlaylistService.getTracks(p),
  component: PlayPage,
});

export type state = {
  nowPlay: string;
  setNowPlay: React.Dispatch<React.SetStateAction<string>>;
  playlist_id: string;
  playlistContent: TrackData[];
  setPlaylistContent: React.Dispatch<React.SetStateAction<TrackData[]>>;
};

export const NowPlayContext = React.createContext<state>({} as state);

export default function PlayPage() {
  const [nowPlay, setNowPlay] = React.useState<string>("");
  const { p } = Route.useSearch();
  const tracks = Route.useLoaderData();
  const [playlistContent, setPlaylistContent] =
    React.useState<TrackData[]>(tracks);

  const [newTrackUrl, setNewTrackUrl] = React.useState("");
  const [isCorrectUrl, setIsCorrectUrl] = React.useState(false);
  const addtrack = async () => {
    const track = await PlaylistService.addTrackToPlaylist(p, newTrackUrl);
    if (track) {
      setPlaylistContent([...playlistContent, track]);
      setNewTrackUrl("");
    }
  };

  const nextTrack = () => {
    const index = playlistContent.findIndex((track) => track.yt_id === nowPlay);
    if (index === playlistContent.length - 1) {
      setNowPlay(playlistContent[0].yt_id);
    } else {
      setNowPlay(playlistContent[index + 1].yt_id);
    }
  };

  React.useEffect(() => {
    if (isYouTubeVideoURL(newTrackUrl)) {
      setIsCorrectUrl(true);
    } else {
      setIsCorrectUrl(false);
    }
  }, [newTrackUrl]);

  return (
    <div className="main h-screen ">
      <div className="app w-full items-center p-4">
        <NowPlayContext.Provider
          value={{
            nowPlay: nowPlay,
            setNowPlay: setNowPlay,
            playlist_id: p,
            playlistContent: playlistContent,
            setPlaylistContent: setPlaylistContent,
          }}
        >
          <div
            className={`w-full flex justify-center p-4 ${!nowPlay && "hidden"}`}
          >
            <YoutubePlayer nextVideo={nextTrack} />
          </div>
          <div className="flex mb-4">
            <Button
              onClick={addtrack}
              disabled={!isCorrectUrl}
              variant={"ghost"}
              className=" bg-gray-600 mr-4 "
            >
              Додати до плейлісту
            </Button>
            <Input
              placeholder="Посилання на youtube відео"
              onChange={(e) => setNewTrackUrl(e.target.value)}
              value={newTrackUrl}
            />
          </div>
          <div className="List">
            <PlayList />
          </div>
        </NowPlayContext.Provider>
        {/* <div className="Recomend">
          <Recomendations />
        </div> */}
      </div>
    </div>
  );
}
